# pipeline.py
from v2s.phase1.phase1 import Phase1V2S
from v2s.phase2.phase2 import Phase2V2S


class Pipeline():
    """
    Pipeline for tool.

    Attributes
    ----------
    phases : list of AbstractPhases
        list of phases in pipeline

    Methods
    -------
    add_phase(phase)
        Inserts a new phase into the pipeline.
    execute()
        Executes phases in the pipeline.
    """

    def __init__(self):
        # create a list of phases
        self.phases = []
    
    def add_phase(self, phase):
        """
        Inserts a new phase into the pipeline.

        Parameters
        ----------
        phase : AbstractPhase
            phase to insert
        """
        self.phases.append(phase)
    
    def execute(self):
        """
        Executes the pipeline by executing each phase listed.
        """
        for phase in self.phases:
            phase.execute()

class PipelineV2S(Pipeline):
    """
    Executes V2S pipeline containing Phase1, Phase2, and Phase3.

    Attributes
    ----------
    phases : list of AbstractPhases
        phases included in the pipeline
    """

    def __init__(self, config=None):
        """
        Parameters
        ----------
        args : arg parse
            arguments from command line
        """
        super().__init__()
        # add appropriate phases for V2S to pipeline
        self.add_phase(Phase1V2S(config))
        self.add_phase(Phase2V2S(config))
