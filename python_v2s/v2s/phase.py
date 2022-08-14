# phase.py

from abc import ABC, abstractmethod

class AbstractPhase(ABC):
    """
    Executes each phase in pipeline.

    Methods
    -------
    execute()
        Executes phase.
    """

    @abstractmethod
    def execute(self):
        """
        Executes phase.
        """
        pass