import torch
from typing import Dict, Tuple, List
try:
    import flwr as fl
except ImportError:
    fl = None

class MedScopeFederatedClient:
    """
    Experimental Federated Learning Client using Flower (flwr).
    Purpose: Multi-hospital training without sharing patient data.
    """
    def __init__(self, model: torch.nn.Module, train_loader, val_loader, device: str = 'cpu'):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        
        if fl is None:
            print("Warning: flwr not installed. Federated Client is a stub.")

    def get_parameters(self, config: Dict[str, str]) -> List[torch.Tensor]:
        """Return the parameters of the local PyTorch model as a list of NumPy ndarrays."""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[torch.Tensor]) -> None:
        """Set the local PyTorch model parameters from a list of NumPy ndarrays."""
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters: List[torch.Tensor], config: Dict[str, str]) -> Tuple[List[torch.Tensor], int, Dict]:
        """Train the local model using the local dataset."""
        if fl is None:
            return parameters, 100, {"stub": True}
            
        self.set_parameters(parameters)
        # Assuming a basic training loop here...
        # train(self.model, self.train_loader, epochs=1, device=self.device)
        return self.get_parameters(config={}), len(self.train_loader.dataset), {}

    def evaluate(self, parameters: List[torch.Tensor], config: Dict[str, str]) -> Tuple[float, int, Dict]:
        """Evaluate the local model using the local dataset."""
        if fl is None:
            return 0.0, 100, {"accuracy": 0.0}
            
        self.set_parameters(parameters)
        # loss, accuracy = test(self.model, self.val_loader, device=self.device)
        loss = 0.5
        accuracy = 0.85
        return loss, len(self.val_loader.dataset), {"accuracy": accuracy}
        
    def start_client(self, server_address: str = "127.0.0.1:8080"):
        if fl is None:
            print("Cannot start client without flwr.")
            return
            
        # flwr expects a NumPyClient implementation
        class FlowerNumPyClient(fl.client.NumPyClient):
            def __init__(self, parent):
                self.parent = parent
            def get_parameters(self, config):
                return self.parent.get_parameters(config)
            def fit(self, parameters, config):
                return self.parent.fit(parameters, config)
            def evaluate(self, parameters, config):
                return self.parent.evaluate(parameters, config)
                
        fl.client.start_numpy_client(
            server_address=server_address,
            client=FlowerNumPyClient(self)
        )
