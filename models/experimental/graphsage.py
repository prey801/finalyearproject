import torch
import torch.nn.functional as F
try:
    from torch_geometric.nn import SAGEConv
except ImportError:
    SAGEConv = None

class PatientGraphSAGE(torch.nn.Module):
    """
    Experimental GraphSAGE model for Patient-Disease-Symptom networks.
    Purpose: Learn relationships among patients, diseases, and findings.
    """
    def __init__(self, in_channels: int = 128, hidden_channels: int = 64, out_channels: int = 32):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        
        if SAGEConv is not None:
            self.conv1 = SAGEConv(in_channels, hidden_channels)
            self.conv2 = SAGEConv(hidden_channels, out_channels)
        else:
            self.conv1 = None
            self.conv2 = None
            print("Warning: torch_geometric not installed. GraphSAGE using stub layers.")

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        x: Node feature matrix of shape [num_nodes, in_channels]
        edge_index: Graph connectivity matrix of shape [2, num_edges]
        """
        if self.conv1 is None:
            # Stub forward pass
            return torch.randn(x.size(0), self.out_channels, device=x.device)
            
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return x
