# phase2.py
import logging
import os

from v2s.phase import AbstractPhase
from v2s.phase2.action_classification.action_classification import \
    GUIActionClassifier
from v2s.util.constants import THRESHOLD_CONFIDENCE
from v2s.util.event import GUIAction
from v2s.util.general import JSONFileUtils
from v2s.util.screen import Frame, ScreenTap


class Phase2V2S(AbstractPhase):
    """
    Takes touch detections from Phase 1 and classifies them into discrete actions
    on the screen. Loads in detections from json file from Phase1 and translates
    to output a list of GUIActions.

    Attributes
    ----------
    config : dict
        configuration with video/replay information
    touch_detections : list of Frames
        detections from Phase 1
    action_classifier : GUIActionClassifier
        will take care of classification
    actions : list of GUIActions
        GUIActions detected from detections; output of this phase

    Methods
    --------
    execute()
        Execute the action classification.
    read_detections_from_json(detection_path)
        Reads detections from json file from Phase 1.
    get_actions()
        Returns list of GUIActions.
    set_actions(actions)
        Changes actions to specified value.
    get_video_path()
        Returns video path.
    set_video_path(path)
        Changes video path to specified value.
    get_touch_detections()
        Returns touch detections.
    set_touch_detections(dets)
        Changes touch detections to specified value.
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config : dict
            configuration for video and device
        """
        self.config = config
        self.touch_detections = []
        self.action_classifier = GUIActionClassifier()
        self.actions = []
    
    def execute(self):
        '''
        Execute the action classification.
        '''
        # get video path
        cur_path = self.config["video_path"]
        # read the detections from phase 1
        video_dir, video_file = os.path.split(cur_path)
        video_name, video_extension = os.path.splitext(video_file)
        cur_dir_path = os.path.join(video_dir, video_name)

        logging.basicConfig(filename=os.path.join(cur_dir_path, 'v2s.log'), filemode='w', level=logging.INFO)

        detection_path = os.path.join(cur_dir_path, "detection_full.json")
        self.read_detections_from_json(detection_path, video_file)
        
        # filter detections before classifying
        final_detections = []
        for detection in self.touch_detections:
            remove = []
            for i in range(len(detection.get_screen_taps())):
                if detection.get_screen_taps()[i].get_touch_confidence() < THRESHOLD_CONFIDENCE:
                    remove.append(detection.get_screen_taps()[i])
                
            detection.set_screen_taps([tap for tap in detection.get_screen_taps() if tap not in remove])
            if len(detection.get_screen_taps()) != 0:
                final_detections.append(detection)
        
        self.touch_detections = final_detections

        self.action_classifier.set_touch_detections(self.touch_detections)
        self.action_classifier.execute_classification()

        actions = self.action_classifier.get_detected_actions()
        # add actions to self.actions dictionary of this class
        self.actions = actions

        action_path = os.path.join(cur_dir_path, "detected_actions.json")

        JSONFileUtils.output_data_to_json(actions, action_path)

    def read_detections_from_json(self, detection_path, vid_file):
        """
        Reads detections from json file from phase 1. 

        Parameters
        ----------
        detection_path : string
            path to detection json file
        vid_file : string
            video file name for dictionary key
        """
        # returns JSON object as  
        # a dictionary 
        data = JSONFileUtils.read_data_from_json(detection_path) 
        
        # list of frames that will be appended to as they are loaded
        frames = []

        # file is a list of dictionaries
        for det_dict in data:
            frame_id = det_dict["screenId"]
            taps = det_dict["screenTap"]
            tap_list = []
            # taps is a list of dictionaries with tap information
            for tap in taps:
                # extract tap information
                x = tap["x"]
                y = tap["y"]
                touch_confidence = tap["confidence"]
                opacity_confidence = tap["confidenceOpacity"]
                # create new tap
                new_tap = ScreenTap(x, y, touch_confidence)
                new_tap.set_opacity_confidence(opacity_confidence)
                # add the new tap to the list of taps associated with this frame
                tap_list.append(new_tap)
            # create new frame object
            frame = Frame(frame_id)
            frame.set_screen_taps(tap_list)
            frames.append(frame)

        # add these detections to the full detections dictionary
        self.touch_detections = frames

    def get_actions(self):
        """
        Returns dictionary of GUIActions.

        Returns
        -------
        actions : dict
            classified GUIAction
        """
        return self.actions

    def set_actions(self, actions):
        """
        Changes actions to specified value.

        Parameters
        ----------
        actions : dict
            new GUIActions
        """
        self.actions = actions

    def get_video_path(self):
        """
        Returns video path.

        Returns
        -------
        video_path : string
            path to video being analyzed
        """
        return self.video_path

    def set_video_path(self, path):
        """
        Changes video path to specified value.

        Parameters
        ----------
        video_path : string
            path to video being analyzed
        """
        self.video_path = path

    def get_touch_detections(self):
        """
        Returns touch detections.

        Returns
        -------
        touch_detections : dict
            touch detections from Phase1
        """
        return self.touch_detections
    
    def set_touch_detections(self, dets):
        """
        Changes touch detections to specified value.

        Parameters
        ----------
        dets : dict
            new detections
        """
        self.touch_detections = dets
