# video_manipulation.py
import logging
import os
from abc import ABC, abstractmethod

import ffmpeg

from v2s.util.constants import FRAMES_PER_SECOND


class AbstractVideoManipulator(ABC):
    """
    Edits video in desired way.

    Attributes
    ----------
    video_path : string
        path to video

    Methods
    -------
    execute()
        Executes video manipulation as necessary.
    """

    @abstractmethod
    def __init__(self, video_path=None):
        """
        Parameters
        ----------
        video_path : string
            path to video to manipulate
        """
        self.video_path = video_path

    @abstractmethod
    def execute(self):
        pass

class FrameExtractor(AbstractVideoManipulator):
    """
    Manipulates input video to standardize fps and then extract frames from
    video so detection can take place.

    Executes manipulation on all videos available in input folder.

    Attributes
    ----------
    video_path : string
        path to video to be manipulated
    fps : int
        desired frames per second of video
    frames_path : string
        where to place extracted frames

    Methods
    -------
    execute()
        Executes standardization and frame extraction.
    __fix_video_frame_rate()
        Standardizes video frame rate using ffmpeg.
    __extract_frames() 
        Extract frames from video using ffmpeg.
    get_fps()
        Returns desired fps rate.
    set_fps(fps)
        Changes desired fps to specified value.
    get_frames_path()
        Returns frames path.
    set_frames_path(path)
        Changes frames path to specified value.
    get_video_path()
        Returns video path.
    set_video_path(path)
        Changes video path to specified value.
    """

    def __init__(self, video_path=None, fps=FRAMES_PER_SECOND):
        """
        Parameters
        ----------
        video_path : string
            path to video
        fps : int
            desired fps
        """
        self.video_path = video_path
        # default is 30
        self.fps = fps

    def execute(self):
        """
        Executes standardization and frame extraction.
        """
        logging.info("Manipulating: " + os.path.basename(self.video_path))
        self.__fix_video_frame_rate()
        self.__extract_frames()

    def __fix_video_frame_rate(self):
        """
        Standardizes video frame rate using ffmpeg. 
        
        Creates a folder for each video to contain other intermediate info.
        Outputs video to same directory as input video with suffix "-fixed.mp4".
        
        video encoding: -vcodec libx264
        override output: -y
        -preset ultrafast
        constant rate factor: -crf 15
        """
        # separate the name and extension of the file
        video_file = os.path.basename(self.video_path)
        video_name, video_extension = os.path.splitext(video_file)
        dir_path = os.path.join(os.path.dirname(self.video_path), video_name)
       
        output_vid_path = os.path.join(dir_path, video_name + "-fixed.mp4")
        (
            ffmpeg
            .input(self.video_path)
            .output(output_vid_path, 
                    **{'vcodec':'libx264', 'r':self.fps, 'preset':'ultrafast', 
                    'crf':15, 'loglevel':'panic'})
            .run()
        )
        logging.info("Video frame rate fixed and placed at: " + output_vid_path)

    def __extract_frames(self):
        """ 
        Extract frames from video using ffmpeg.

        Outputs frames to frames_path with names specifying frame number as 
        "xxxx.jpg".
        """

        # separate the name and extension of the file
        video_file = os.path.basename(self.video_path)
        video_name, video_extension = os.path.splitext(video_file)
        # get the subdirectory of the video
        # created in phase1
        dir_path = os.path.join(os.path.dirname(self.video_path), video_name)
        fixed_video_path = os.path.normpath(dir_path + os.sep + video_name + "-fixed.mp4")
        extracted_frames_path = os.path.join(dir_path, 'extracted_frames' + os.sep)

        # for each folder, create a folder for extracted images
        if not os.path.exists(extracted_frames_path):
            os.mkdir(extracted_frames_path)
        (
            ffmpeg
            .input(fixed_video_path)
            .output(os.path.join(extracted_frames_path, '%04d.jpg'), 
                    **{'qscale:v': 3, 'vf':'fps='+str(self.fps), 'loglevel':'panic'})
            .run()
        )

        logging.info("Frames extracted and placed in: " + extracted_frames_path)
    
    def get_fps(self):
        """
        Returns desired fps rate.

        Returns
        -------
        fps : int
            desired frames per second of video
        """
        return self.fps

    def set_fps(self, fps):
        """
        Changes desired fps to specified value.

        Parameters
        ----------
        fps : int
            new fps for video
        """

    def get_frames_path(self):
        """
        Returns frames path.

        Returns
        -------
        frames_path : string
            path where extracted frames are placed
        """
        return self.frames_path

    def set_frames_path(self, path):
        """
        Changes frames path to specified value.

        Parameters
        ----------
        path : string
            new frames path
        """
        self.frames_path = path

    def get_video_path(self):
        """
        Returns video path.

        Returns
        -------
        video_path : string
            path to video
        """
        return self.video_path

    def set_video_path(self, path):
        """
        Changes video path to specified value.

        NOTE: Also changes frames path because these are usually set together.

        Parameters
        ----------
        path : string
            new path to video
        """
        self.video_path = path
        frames = os.path.join(os.path.dirname(self.video_path), 
                             "extracted_frames"+os.sep)
        self.set_frames_path(frames)
