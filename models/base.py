from abc import ABC, abstractmethod
from typing import Any

class BaseModel(ABC):
    """
    Abstract base class for all machine learning models in MedScope AI.
    Provides a consistent interface for loading models, preprocessing data,
    and running inference.
    """

    @abstractmethod
    def load_model(self) -> None:
        """
        Load the model weights into memory.
        """
        pass

    @abstractmethod
    def preprocess(self, inputs: Any) -> Any:
        """
        Preprocess raw inputs into the format expected by the model.
        """
        pass

    @abstractmethod
    def predict(self, inputs: Any) -> Any:
        """
        Run inference on the preprocessed inputs and return the formatted output.
        """
        pass
