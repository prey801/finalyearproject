import unittest
from unittest.mock import patch, MagicMock
import torch
from PIL import Image

class TestExperimentalModels(unittest.TestCase):

    @patch('models.baselines.model.timm.create_model')
    def test_baseline_models(self, mock_create_model):
        from models.baselines.model import BaselineModel
        
        mock_model = MagicMock()
        # Mock returning 2 class logits
        mock_model.return_value = torch.tensor([[1.0, 0.0]])
        mock_create_model.return_value = mock_model
        
        # Test default (resnet50)
        model_resnet = BaselineModel(architecture='resnet50', num_classes=2)
        dummy_image = Image.new('RGB', (224, 224))
        result = model_resnet.predict(dummy_image)
        self.assertEqual(result["architecture"], "resnet50")
        
        # Test ViT
        model_vit = BaselineModel(architecture='vit-base', num_classes=2)
        result_vit = model_vit.predict(dummy_image)
        self.assertEqual(result_vit["architecture"], "vit-base")

    @patch('models.foundation.dinov2.torch.hub.load')
    def test_dinov2_encoder(self, mock_hub_load):
        from models.foundation.dinov2 import DINOv2Encoder
        
        mock_model = MagicMock()
        mock_model.return_value = torch.randn(1, 384)
        mock_hub_load.return_value = mock_model
        
        encoder = DINOv2Encoder(model_size='vits14')
        dummy_image = Image.new('RGB', (224, 224))
        features = encoder.extract_features(dummy_image)
        
        self.assertEqual(features.shape, (1, 384))

    def test_biomedclip_stub(self):
        from models.foundation.biomedclip import BiomedCLIPModel
        
        # Tests the stub behavior when open_clip is not installed
        model = BiomedCLIPModel()
        dummy_image = Image.new('RGB', (224, 224))
        
        img_features = model.encode_image(dummy_image)
        self.assertEqual(img_features.shape, (1, 512))
        
        txt_features = model.encode_text("Malaria parasite")
        self.assertEqual(txt_features.shape, (1, 512))

    def test_graphsage_stub(self):
        from models.experimental.graphsage import PatientGraphSAGE
        
        model = PatientGraphSAGE(in_channels=10, hidden_channels=5, out_channels=2)
        x = torch.randn(3, 10)
        edge_index = torch.tensor([[0, 1], [1, 2]])
        
        out = model(x, edge_index)
        # Check output matches num_nodes and out_channels
        self.assertEqual(out.shape, (3, 2))

    def test_federated_client_stub(self):
        from models.experimental.federated import MedScopeFederatedClient
        
        # Mock PyTorch model
        model = torch.nn.Linear(10, 2)
        client = MedScopeFederatedClient(model=model, train_loader=[], val_loader=[])
        
        # Test get params
        params = client.get_parameters(config={})
        self.assertEqual(len(params), 2) # weight and bias
        
        # Test evaluate stub
        loss, size, metrics = client.evaluate(params, config={})
        self.assertEqual(size, 100) # Stub returns 100 size

if __name__ == '__main__':
    unittest.main()
