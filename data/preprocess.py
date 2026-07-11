import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2

def get_transforms(split="train", image_size=224):
    """
    Returns albumentations transforms for the given split and target image size.
    
    Args:
        split (str): 'train', 'val', or 'test'.
        image_size (int): Target size for resizing.
        
    Returns:
        A.Compose: Albumentations compose object.
    """
    # Common transformations (Resizing and Normalization)
    base_transforms = [
        A.Resize(height=image_size, width=image_size),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ]

    if split == "train":
        # Augmentations for training
        augmentations = [
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=45, p=0.5),
            A.RandomBrightnessContrast(p=0.2),
            A.GaussNoise(p=0.2),
        ]
        transforms = augmentations + base_transforms
    else:
        # No augmentations for val/test, just resize and normalize
        transforms = base_transforms
        
    # Append ToTensorV2 to convert to PyTorch tensors
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
