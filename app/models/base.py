from abc import ABC, abstractmethod
from typing import Any

class BaseVisionModel(ABC):
    @abstractmethod
    def load_weights(self, path: str):
        pass

    @abstractmethod
    def predict(self, input_data: Any) -> Any:
        pass
