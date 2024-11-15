""" Abstract base class for prediction models.
"""

from abc import ABC, abstractmethod
from base import agent


class AbstractModel(ABC):
    def __init__(self, maze, name):
        self.environment = maze
        self.name = name

    def load(self, filename):
        """Load model from file."""
        pass

    def save(self, filename):
        """Save model to file."""
        pass

    def train(
        self,
        discount,
        exploration_rate,
        learning_rate,
        episodes,
        stop_at_convergence=False,
    ):
        """Train model."""
        pass

    @abstractmethod
    def q(self, state):
        """Return q values for state."""
        pass

    @abstractmethod
    def predict(self, state):
        """Predict value based on state."""
        pass
