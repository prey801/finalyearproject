import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2

def get_transforms(split="train", image_size=224):
    """
    Returns albumentations transforms for the given split and target image size.

    Args:
        split (str): 'train', 'val', or 'test'.
        image_size (int): Target size for resizing (default 224 for Swin/ResNet).

    Returns:
        A.Compose: Albumentations compose object.

    Augmentation strategy for Swin Transformer:
        - Geometric: flips, rotation, ShiftScaleRotate  (spatial invariance)
        - Color: ColorJitter, RandomGamma               (stain normalisation robustness)
        - Regularisation: CoarseDropout (Cutout)        (prevents attention collapse)
        - Noise: GaussNoise                             (sensor noise simulation)

    Performance note:
        A.CLAHE internally calls cv2.createCLAHE(), which uses OpenCV's thread pool.
        With cv2.setNumThreads(0) (required for fork safety), CLAHE degrades to
        single-threaded and becomes the dominant CPU bottleneck per sample.
        A.RandomGamma achieves equivalent brightness/contrast normalisation via a
        pure-numpy gamma LUT — ~20x faster and fork-safe.
    """
    # Common transformations applied to every split
    base_transforms = [
        A.Resize(height=image_size, width=image_size),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ]

    if split == "train":
        augmentations = [
            # ── Geometric ──────────────────────────────────────────────────
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.0625, scale_limit=0.1, rotate_limit=45, p=0.5
            ),

            # ── Color / stain robustness ───────────────────────────────────
            # ColorJitter simulates staining batch variation common in histology.
            A.ColorJitter(
                brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05, p=0.4
            ),
            # RandomGamma: pure-numpy LUT, ~20x faster than CLAHE.
            # Gamma in [80, 120] normalises over/under-stained slide brightness
            # with the same practical effect as CLAHE for this task.
            A.RandomGamma(gamma_limit=(80, 120), p=0.3),

            # ── Regularisation ─────────────────────────────────────────────
            # CoarseDropout (Cutout) forces the Swin attention to not fixate on
            # a single region, improving generalisation.
            A.CoarseDropout(
                max_holes=8,
                max_height=image_size // 8,
                max_width=image_size // 8,
                min_holes=1,
                fill_value=0,
                p=0.3,
            ),

            # ── Noise ──────────────────────────────────────────────────────
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
            A.RandomBrightnessContrast(p=0.2),
        ]
        transforms = augmentations + base_transforms
    else:
        # No augmentations for val/test — just resize and normalize.
        transforms = base_transforms

    transforms.append(ToTensorV2())
    return A.Compose(transforms)


def preprocess_image(image_path, split="val", image_size=224):
    """
    Utility function to preprocess a single image file.

    Args:
        image_path (str): Path to the image file.
        split (str): 'train', 'val', or 'test'.
        image_size (int): Target size for resizing.

    Returns:
        torch.Tensor: Preprocessed image tensor.
    """
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    transform = get_transforms(split=split, image_size=image_size)
    augmented = transform(image=image)

    return augmented["image"]
