# opacity_detection.py
import datetime
import logging
import os
from abc import ABC, abstractmethod

import numpy as np
from keras.models import load_model
from PIL import Image
from tensorflow.keras.utils import img_to_array, load_img

from v2s.util.general import ImageUtils

class AbstractOpacityDetector(ABC):
    """
    Completes opacity detection on detected touches.

    Attributes
    ----------
    prediction_time : float
        time to complete predictions

    Methods
    -------
    execute_detection()
        Executes opacity prediction.
    get_prediction_time()
        Returns prediction time.
    set_prediction_time(time)
        Changes prediction time to specified value.
    """

    @abstractmethod
    def __init__(self):
        self.prediction_time = 0

    @abstractmethod
    def execute_detection(self):
        """
        Executes opacity prediction.
        """
        pass

    def get_prediction_time(self):
        """
        Returns prediction time.

        Returns
        -------
        prediction_time : float
            time to predict
        """
        return self.prediction_time

    def set_prediction_time(self, time):
        """
        Changes prediction time to specified value.

        Parameters
        ----------
        time : float
            new prediction time
        """
        self.prediction_time = time

class OpacityDetectorALEXNET(AbstractOpacityDetector):
    """
    Opacity detector using ALEXNET trained model. Inputs extracted frames with 
    touches already detected, crops those frames, and feeds the cropped touch 
    detectors into a model to detect opacity. Outputs opacity predictions which
    can then be added to the detections.
    
    Executes one video at a time.

    Attributes
    ----------
    frames : list of Frames
        frames touches are detected in
    video_path : string
        path to video file being analyzed
    cropped_path : string
        path where cropped images will be placed
    opacity_predictions : array of int
        predictions of opacity
    prediction_time : float
        time to complete predictions
    model_path : string
        path to trained opacity model
    keras_model : keras model
        keras model to use
    size : int
        size of image to pass into model
    touch_indicator_size : int
        size of touch indicator based on model


    Methods
    -------
    execute_detection()
        Executes opacity prediction.
    __crop_and_compile_images()
        Crops and compiles detected touch images into a format that can be
        fed to model.
    __load_model(path)
        Loads model to be used so that predictions can be made.
    set_indicator_size(size)
        Changes touch indicator size to specified value.
    get_opacity_predictions()
        Returns opacity predictions.
    set_opacity_predictions(preds)
        Changes opacity predictions to specified value.
    get_frames()
        Returns frames.
    set_frames(frames)
        Changes frames to specified value.
    get_video_path()
        Returns video path.
    set_video_path(path)
        Changes video path to specified value.
    get_cropped_path()
        Returns cropped path.
    set_cropped_path(path)
        Changes cropped path to specified value.
    get_model_path()
        Returns path to opacity model.
    set_model_path(path)
        Changes model path to specified value.
    """

    def __init__(self, frames, model=None, video_path=None, indicator=None):
        """
        Parameters
        ----------
        frames : list of Frames
            list of frames that touches are detected in
        model : string, optional
            path to trained opacity model
        video_path : string, optional
            path to video file to be detected
        device : enum
            device model
        """
        super().__init__()
        self.frames = frames
        self.opacity_predictions = None
        self.model_path = model
        self.video_path = video_path
        self.touch_indicator_size = indicator
        # This is the size defined in the model for AlexNet architecture
        self.size = 227

    def execute_detection(self):
        """
        Executes opacity prediction.
        """
        self.__crop_and_compile_images()
        # get the images in the cropped folder
        logging.info("Detecting opacity value for video : " +
                                             os.path.basename(self.video_path))
        img_list = [img for img in os.listdir(self.cropped_path) if
                                            os.path.splitext(img)[1] == ".jpg"]
        # sort image list so we know the order of the predictions
        img_list.sort()
        predictions = []
        images = []
        for img in img_list:
            touch = os.path.join(self.cropped_path, img)
            temp_image = load_img(touch)
            temp_image = temp_image.resize((self.size, self.size), Image.ANTIALIAS)
            temp_image_np = img_to_array(temp_image)
            # Normalization
            temp_image_np = temp_image_np.reshape((1,) + temp_image_np.shape) / 255
            images.append(temp_image_np)

        # resize all images together to get ready to pass into model
        images = np.array(images).reshape(len(images), self.size, self.size, 3)
        # load model
        self.keras_model = self.__load_model(self.model_path)
        # use model to predict
        # set attribute opacity_predictions
        predictions = self.keras_model.predict(images)
        self.set_opacity_predictions(predictions)

    
    def __crop_and_compile_images(self):
        """
        Crops and compiles detected touch images into a format that can be
        fed to model.
        """
        # alias for shorter usage
        size = self.touch_indicator_size
        # ensure placement directory exists
        if not os.path.exists(self.cropped_path):
            os.mkdir(self.cropped_path)
        # path to extracted frames
        video_dir, video_file = os.path.split(self.video_path)
        video_name, video_extension = os.path.splitext(video_file)
        extracted_frames_dir_path = os.path.join(video_dir, video_name , 
                                                 "extracted_frames")
        logging.info(extracted_frames_dir_path)
        # match the frame number with the image to crop
        for detection in self.frames:
            # format string as it was for images
            det_id = "%04d" % detection.get_id()
            img_base = det_id + ".jpg"
            img_path = os.path.join(extracted_frames_dir_path, img_base)
            loaded_image = Image.open(img_path)
            full_img = ImageUtils.load_image_into_np_array(loaded_image)
            # cycle through each screen tap and save a cropped image
            for num, tap in enumerate(detection.get_screen_taps()):
                x = max(round((tap.get_x() - self.touch_indicator_size / 2)), 0)
                y = max(round((tap.get_y() - self.touch_indicator_size / 2)), 0)
                
                crop_path = os.path.join(self.cropped_path, det_id + "_" + 
                                         str(num) + ".jpg")
                # slice from top of bounding box to size of touch indicator
                crop_img = full_img[int(y):int(y+size), int(x):int(x+size)]
                # save image
                ImageUtils.save_image_array_as_jpg(crop_img, crop_path)

    def __load_model(self, path):
        """
        Loads model to be used so that predictions can be made.

        Parameters
        ----------
        path : string
            path to keras model to load

        Returns
        -------
        keras_model: model
            model that can be used to predict with
        """
        return load_model(path)
    
    def set_indicator_size(self, size):
        """
        Changes the touch indicator size to specified value.

        Parameters
        ----------
        size : int
            size of touch indicator
        """
        self.touch_indicator_size = size
    
    def get_opacity_predictions(self):
        """
        Returns opacity predictions.
        """
        return self.opacity_predictions

    def set_opacity_predictions(self, preds):
        """
        Changes opacity predictions to specified value.

        Parameters
        ----------
        dets : array
            new opacity predictions
        """
        self.opacity_predictions = preds

    def get_frames(self):
        """
        Returns frames.

        Returns
        -------
        frames : list of Frames
            frames associated with predictions
        """
        return self.frames

    def set_frames(self, frames):
        """
        Changes frames to specified value.

        Parameters
        ----------
        frames : list of Frames
            new frames
        """
        self.frames = frames

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
        Changes video path to specified value. Also changes the cropped path to
        match.

        Parameters
        ----------
        path : string
            new video path
        """
        self.video_path = path

        video_dir, video_file = os.path.split(path)
        video_name, video_extension = os.path.splitext(video_file)
        vid_path_dir = os.path.join(video_dir, video_name)
        crop = os.path.join(vid_path_dir, "cropped_images")
        self.set_cropped_path(crop)

    def get_cropped_path(self):
        """
        Returns cropped path.

        Returns
        -------
        cropped_path : string
            path to cropped images
        """
        return self.cropped_path

    def set_cropped_path(self, path):
        """
        Changes cropped path to specified value.

        Parameters
        ----------
        path : string
            new cropped path
        """
        self.cropped_path = path

    def get_model_path(self):
        """
        Returns path to opacity model.

        Returns
        -------
        model_path : string
            path to opacity model
        """
        return self.model_path

    def set_model_path(self, path):
        """
        Changes model path to specified value.

        Parameters
        ----------
        path : string
            new model path
        """
        self.model_path = path


