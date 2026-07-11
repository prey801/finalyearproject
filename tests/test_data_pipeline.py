import pytest
import torch
import numpy as np
from pathlib import Path

from data.config import DataPaths, DatasetConfig
from data.preprocess import get_transforms
from data.dataset import NIHMalariaDataset

def test_config_paths():
    """Verify that DataPaths points to valid Path objects."""
    assert isinstance(DataPaths.DATA_DIR, Path)
    assert isinstance(DataPaths.TRAINING_DIR, Path)

def test_transforms_train():
    """Verify train transformations setup successfully."""
    transform = get_transforms(split="train", image_size=224)
    assert transform is not None
    
    # Create a dummy image
    dummy_img = np.zeros((300, 300, 3), dtype=np.uint8)
    augmented = transform(image=dummy_img)
    
    assert "image" in augmented
    tensor = augmented["image"]
    assert isinstance(tensor, torch.Tensor)
    # Output tensor shape should be (C, H, W)
    assert tensor.shape == (3, 224, 224)

def test_transforms_val():
    """Verify val transformations setup successfully."""
    transform = get_transforms(split="val", image_size=384)
    assert transform is not None
    
    dummy_img = np.zeros((150, 150, 3), dtype=np.uint8)
    augmented = transform(image=dummy_img)
    
    tensor = augmented["image"]
    assert tensor.shape == (3, 384, 384)

@pytest.mark.skipif(not (DataPaths.TRAINING_DIR / "metadata.csv").exists(), 
                    reason="Dataset metadata.csv not found. Skip actual dataset loading.")
def test_dataset_instantiation():
    """Verify the dataset can be instantiated if data exists."""
    dataset = NIHMalariaDataset(split="train", image_size=224)
    assert len(dataset) > 0
    
    img, label = dataset[0]
    assert img.shape == (3, 224, 224)
    assert isinstance(label, torch.Tensor)
