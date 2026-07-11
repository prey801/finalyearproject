import os
import cv2
import torch
import pandas as pd
from pathlib import Path
from torch.utils.data import Dataset, DataLoader

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data.config import DataPaths, DatasetConfig
from data.preprocess import get_transforms

class NIHMalariaDataset(Dataset):
    """
    PyTorch Dataset for the NIH Malaria Cell Classification.
    Reads images from the split directory based on metadata.csv.
    """
    def __init__(self, split="train", image_size=224, transform=None):
        """
        Args:
            split (str): 'train', 'val', or 'test'.
            image_size (int): Target size for images (used if transform is None).
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.split = split
        if split == "train":
            self.data_dir = DataPaths.TRAINING_DIR
        elif split == "val":
            self.data_dir = DataPaths.VALIDATION_DIR
        elif split == "test":
            self.data_dir = DataPaths.TESTING_DIR
        else:
            raise ValueError("Split must be 'train', 'val', or 'test'")
            
        self.images_dir = self.data_dir / "images"
        self.metadata_path = self.data_dir / "metadata.csv"
        
        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found at {self.metadata_path}. "
                "Make sure you run scripts/split_data.py first."
            )
            
        self.df = pd.read_csv(self.metadata_path)
        
        # Create class to index mapping based on config
        self.classes = DatasetConfig.NIH_MALARIA_CLASSES
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        
        # Assign transforms
        if transform:
            self.transform = transform
        else:
            self.transform = get_transforms(split=split, image_size=image_size)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = self.df.iloc[idx, 0] # First column is filename
        label_str = self.df.iloc[idx, 1] # Second column is label
        
        img_path = self.images_dir / img_name
        image = cv2.imread(str(img_path))
        
        if image is None:
            raise ValueError(f"Could not read image {img_path}")
            
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]
            
        label = self.class_to_idx[label_str]
        
        return image, torch.tensor(label, dtype=torch.long)

def get_dataloaders(image_size=224, batch_size=32, num_workers=4):
    """
    Returns DataLoaders for train, val, and test splits.
    
    Returns:
        dict: containing 'train', 'val', and 'test' DataLoaders.
    """
    dataloaders = {}
    
    for split in ["train", "val", "test"]:
        dataset = NIHMalariaDataset(split=split, image_size=image_size)
        shuffle = (split == "train")
        
        dataloaders[split] = DataLoader(
            dataset, 
            batch_size=batch_size, 
            shuffle=shuffle, 
            num_workers=num_workers,
            pin_memory=True
        )
        
    return dataloaders
