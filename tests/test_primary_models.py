import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np

# Import the models (assumes dependencies like torch, timm, ultralytics are installed)
# In a CI environment without weights/gpu, we might mock the load_model methods.
# For these basic tests, we'll mock the backends to test the wrapper logic.

class TestPrimaryModels(unittest.TestCase):
    
    @patch('models.quality.model.timm.create_model')
    def test_quality_model(self, mock_create_model):
        from models.quality.model import QualityAssessmentModel
        
        # Mock the timm model
        mock_model = MagicMock()
        import torch
        # Return a tensor representing logits for 5 classes
        mock_model.return_value = torch.tensor([[0.1, 0.8, 0.05, 0.02, 0.03]])
        mock_create_model.return_value = mock_model
        
        model = QualityAssessmentModel(device='cpu')
        
        dummy_image = Image.new('RGB', (224, 224))
        result = model.predict(dummy_image)
        
        self.assertEqual(result, "Blurred") # 0.8 is index 1

    @patch('models.yolo.model.YOLO')
    def test_yolo_model(self, mock_yolo_cls):
        from models.yolo.model import ObjectDetectionModel
        
        mock_yolo_instance = MagicMock()
        
        # Mock ultralytics result object
        class MockBox:
            def __init__(self):
                self.xyxy = [[100.0, 120.0, 140.0, 160.0]]
                self.conf = [0.95]
                self.cls = [2] # parasite
        
        class MockResult:
            def __init__(self):
                self.boxes = [MockBox()]
                
        mock_yolo_instance.return_value = [MockResult()]
        mock_yolo_cls.return_value = mock_yolo_instance
        
        model = ObjectDetectionModel(device='cpu')
        dummy_image = Image.new('RGB', (640, 640))
        
        results = model.predict(dummy_image)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["class"], "parasite")
        self.assertEqual(results[0]["bbox"], [100.0, 120.0, 40.0, 40.0]) # w, h = 140-100, 160-120
        self.assertEqual(results[0]["confidence"], 0.95)

    @patch('models.segmentation.model.build_sam2', create=True)
    @patch('models.segmentation.model.SAM2ImagePredictor', create=True)
    def test_sam2_model(self, mock_predictor_cls, mock_build_sam2):
        from models.segmentation.model import SegmentationModel
        
        mock_predictor = MagicMock()
        # Return masks shape (1, 1, 100, 100)
        mock_predictor.predict.return_value = (np.ones((1, 1, 100, 100)), None, None)
        mock_predictor_cls.return_value = mock_predictor
        
        model = SegmentationModel(device='cpu')
        # Inject the mocked predictor since build_sam might fail/not run in test env if not installed
        model.predictor = mock_predictor
        
        dummy_image = Image.new('RGB', (100, 100))
        # Provide one dummy bbox: x, y, w, h
        dummy_bboxes = [[10.0, 10.0, 20.0, 20.0]]
        
        results = model.predict((dummy_image, dummy_bboxes))
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].shape, (100, 100))

    @patch('models.classification.model.timm.create_model')
    def test_classification_model(self, mock_create_model):
        from models.classification.model import DiseaseClassificationModel
        
        mock_model = MagicMock()
        import torch
        # Return a tensor representing logits for 2 classes
        mock_model.return_value = torch.tensor([[-2.0, 5.0]]) # Very high probability for Malaria (index 1)
        mock_create_model.return_value = mock_model
        
        model = DiseaseClassificationModel(device='cpu')
        
        dummy_image = Image.new('RGB', (224, 224))
        result = model.predict(dummy_image)
        
        self.assertEqual(result["prediction"], "Malaria")
        self.assertGreater(result["confidence"], 0.9)

if __name__ == '__main__':
    unittest.main()
