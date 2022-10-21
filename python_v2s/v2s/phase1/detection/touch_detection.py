# touch_detection.py
import datetime
import glob
import logging
import ntpath
import os
import sys
from abc import ABC, abstractmethod

import numpy as np
import tensorflow as tf
from PIL import Image, ImageFile
from v2s.util.general import ImageUtils, ProgressBar
from v2s.util.screen import Frame, ScreenTap

from tflite_support.task import vision
from tflite_support.task import core
from tflite_support.task import processor


# object detection will only be recognized if it has been added to the path
OB_DET_PATH = os.path.join("phase1", "detection", "object_detection") + os.sep
sys.path.append(OB_DET_PATH)

from .object_detection.utils import visualization_utils as vis_util
from .object_detection.utils.label_map_util import (
    convert_label_map_to_categories, create_category_index, load_labelmap)

class AbstractTouchDetector(ABC):
    """
    Completes touch detection.

    Attributes
    ----------
    detection_time : float
        time to execute detection

    Methods
    -------
    execute_detection()
        Executes touch detection.
    get_detection_time()
        Returns time to execute detections.
    set_detection_time(time)
        Changes detection time to specified value.
    """

    @abstractmethod
    def __init__(self):
        self.touch_detections = []
        self.detection_time = 0

    @abstractmethod
    def execute_detection(self):
        """
        Executes touch detection.
        """
        pass

    def get_detection_time(self):
        """
        Returns time to execute detections.

        Returns
        -------
        time : float
            time required to detect
        """
        return self.detection_time

    def set_detection_time(self, time):
        """
        Changes detection time to specified value.

        Parameters
        ----------
        time : float
            time required to complete detection process
        """
        self.detection_time = time

class TouchDetectorFRCNN(AbstractTouchDetector):
    """
    Touch detector for V2S using a Faster-RCNN technique. Requires model to 
    already be trained.

    Executes detection on one set of extracted frames at a time.

    Attributes
    ----------
    touch_detections : list of Frames
        detected touches
    model_path : string
        path to trained model (frozen graph) for touch detection
    labelmap_path : string
        path to label map for touch detections
    num_classes : int
        number of classes to be identified
    video_path : string
        path to video being analyzed; this information is used to reach extracted
        frames
    detection_time : float
        time to detect touches
    
    Methods
    -------
    execute_detection()
        Executes touch detection on extracted frames located at frames_path.
    set_object_det_path(path)
        Changes object_det_path to specified value.
    set_model_path(path)
        Changes model_path to specified value.
    get_model_path()
        Returns model_path.
    set_labelmap_path(path)
        Changes labelmap_path to specified value.
    get_labelmap_path()
        Returns labelmap_path.
    set_video_path(path)
        Changes video_path to specified value.
    get_video_path()
        Returns video_path.
    get_touch_detections()
        Returns touch detections.
    set_touch_detections(dets)
        Changes touch detections to specified value.
    """

    def __init__(self,  video_path=None, model=None, labelmap=None, 
                 num_classes=1):
        """
        Parameters
        ----------
        video_path : string, optional
            path to video that is being analyzed
        model : string, optional
            path to frozen graph
        labelmap : string, optional
            path to labelmap
        num_classes : int, optional
            number of detection classes
        """
        super(TouchDetectorFRCNN, self).__init__()
        self.touch_detections = []
        # set attributes to passed in values
        self.model_path = model
        self.labelmap_path = labelmap
        self.num_classes = num_classes
        self.video_path = video_path

    def execute_detection(self):
        """
        Executes touch detection on extracted frames located at frames_path.
        """
        # set the default graph in tf to trained touch detection model
        detection_graph = tf.compat.v1.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.compat.v1.gfile.Open(self.model_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.compat.v1.import_graph_def(od_graph_def, name='')

        # load and get information from labelmap
        label_map = load_labelmap(self.labelmap_path)
        categories = convert_label_map_to_categories(label_map,
                     max_num_classes=self.num_classes, use_display_name=True)
        category_index = create_category_index(categories)
        
        video_dir, video_file = os.path.split(self.video_path)
        video_name, video_extension = os.path.splitext(video_file)
        extracted_frames_dir_path = os.path.join(video_dir, video_name , 
                                                 "extracted_frames")

        # sort extracted frames so detections occur in a predictable order
        extracted_frames = glob.glob(os.path.join(extracted_frames_dir_path, '*'))
        extracted_frames.sort()

        detection_output_path = os.path.join(video_dir, video_name, 
                                             "detected_frames")
        # verify detection out path exists
        if not os.path.exists(detection_output_path):
            os.mkdir(detection_output_path)

        
        logging.info('Detecting touches for video: [{}]'.format(os.path.split(self.video_path)[1]))

        config =tf.compat.v1.ConfigProto(inter_op_parallelism_threads=4,
                            allow_soft_placement=True)

        start_detection_time = datetime.datetime.now().replace(microsecond=0)

        # begin a tf session to begin detecting touches
        with detection_graph.as_default():
            with tf.compat.v1.Session(graph=detection_graph, config=config) as sess:
                for image_path in ProgressBar.display(extracted_frames, "Computing: ", 40):
                    # print(image_path)
                    # the array based representation of the image will be used later in order to prepare the
                    # result image with boxes and labels on it.

                    # change the method to load image into np array
                    # image = Image.open(image_path)
                    # image_np = ImageUtils.load_image_into_np_array(image)
                    image_np = np.array(Image.open(image_path))

                    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                    image_np_expanded = np.expand_dims(image_np, axis=0)
                    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                    # Each box represents a part of the image where a particular object was detected.
                    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                    # Each score represents how level of confidence for each of the objects.
                    # Score is shown on the result image, together with the class label.
                    scores = detection_graph.get_tensor_by_name('detection_scores:0')
                    classes = detection_graph.get_tensor_by_name('detection_classes:0')
                    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                    # Actual detection.
                    (boxes, scores, classes, num_detections) = sess.run(
                        [boxes, scores, classes, num_detections],
                        feed_dict={image_tensor: image_np_expanded})

                    boxes = boxes[0]
                    scores = scores[0]

                    # add each detected tap to a Frame object
                    base_name = ntpath.basename(image_path)
                    base_name, file_extension = os.path.splitext(base_name)

                    detection = Frame(int(base_name))
                    (im_width, im_height) = image_np.shape[1], image_np.shape[0]
                    for i in range(len(boxes)):
                        box = boxes[i]
                        score = scores[i]

                        if score > 0.5:
                            # Add detection box on the image data
                            vis_util.visualize_boxes_and_labels_on_image_array(
                                image_np,
                                np.squeeze(boxes),
                                np.squeeze(classes).astype(np.int32),
                                np.squeeze(scores),
                                category_index,
                                use_normalized_coordinates=True,
                                line_thickness=8)

                            yMin = box[0] * im_height
                            xMin = box[1] * im_width
                            yMax = box[2] * im_height
                            xMax = box[3] * im_width
                            # calculate avg x-coord and avg y-coord
                            # for tap
                            x = xMin + ((xMax - xMin) / 2.0)
                            y = yMin + ((yMax - yMin) / 2.0)
                            detection.add_tap(ScreenTap(x, y, float(score)))

                    if (len(detection.get_screen_taps()) > 0):
                        self.touch_detections.append(detection)

                    # place bbox images in "detected_frames" directory
                    output_image_file = os.path.join(detection_output_path, 'bbox-' + base_name + file_extension)
                    # print('Processing: ' + output_image_file, flush=True)
                    # Don't remove, fixes weird error: https://stackoverflow.com/questions/19600147/sorl-thumbnail-encoder-error-2-when-writing-image-file/41018959#41018959
                    ImageFile.MAXBLOCK = im_width * im_height
                    ImageUtils.save_image_array_as_jpg(image_np,
                                            os.path.join(detection_output_path, 'bbox-' + base_name + file_extension))

            end_detection_time = datetime.datetime.now().replace(microsecond=0)
            self.set_detection_time(end_detection_time - start_detection_time)
            logging.info("Touch detection process took: " + str(self.detection_time))

    def execute_detection_tfl(self):
        """
        Executes touch detection on extracted frames located at frames_path.
        """

        video_dir, video_file = os.path.split(self.video_path)
        video_name, video_extension = os.path.splitext(video_file)
        extracted_frames_dir_path = os.path.join(video_dir, video_name,
                                                 "extracted_frames")


        # sort extracted frames so detections occur in a predictable order
        extracted_frames = glob.glob(os.path.join(extracted_frames_dir_path, '*'))
        extracted_frames.sort()

        detection_output_path = os.path.join(video_dir, video_name,
                                             "detected_frames")
        # verify detection out path exists
        if not os.path.exists(detection_output_path):
            os.mkdir(detection_output_path)



        logging.info('Detecting touches for video: [{}]'.format(os.path.split(self.video_path)[1]))

        # Initialization
        model_path = "/Users/yinghaoma/Desktop/ConvertModel/tflite_model/model-export_iod_tflite-tf_lite_indicator_20221003125826-2022-10-04T04_57_42.502381Z_model.tflite"
        base_options = core.BaseOptions(file_name=model_path)
        detection_options = processor.DetectionOptions(max_results=1)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        detector = vision.ObjectDetector.create_from_options(options)

        start_detection_time = datetime.datetime.now().replace(microsecond=0)

        # begin a tf session to begin detecting touches

        for image_path in ProgressBar.display(extracted_frames, "Computing: ", 40):


                image = vision.TensorImage.create_from_file(image_path)
                detection_result = detector.detect(image)
                if detection_result.detections[0].categories[0].score > 0.5:
                    print(detection_result)

        end_detection_time = datetime.datetime.now().replace(microsecond=0)
        self.set_detection_time(end_detection_time - start_detection_time)
        logging.info("Touch detection process took: " + str(self.detection_time))

    def execute_detection_2(self):
        """
        Executes touch detection on extracted frames located at frames_path using saved model instead of frozen graph
        """
        # set the default graph in tf to trained touch detection model
        # detection_graph = tf.Graph()
        # with detection_graph.as_default():
        #     od_graph_def = tf.GraphDef()
        #     with tf.gfile.Open(self.model_path, 'rb') as fid:
        #         serialized_graph = fid.read()
        #         od_graph_def.ParseFromString(serialized_graph)
        #         tf.import_graph_def(od_graph_def, name='')

        # load and get information from labelmap
        label_map = load_labelmap(self.labelmap_path)
        categories = convert_label_map_to_categories(label_map,
                                                     max_num_classes=self.num_classes, use_display_name=True)
        category_index = create_category_index(categories)

        video_dir, video_file = os.path.split(self.video_path)
        video_name, video_extension = os.path.splitext(video_file)
        extracted_frames_dir_path = os.path.join(video_dir, video_name,
                                                 "extracted_frames")

        # sort extracted frames so detections occur in a predictable order
        extracted_frames = glob.glob(os.path.join(extracted_frames_dir_path, '*'))
        extracted_frames.sort()

        detection_output_path = os.path.join(video_dir, video_name,
                                             "detected_frames")
        # verify detection out path exists
        if not os.path.exists(detection_output_path):
            os.mkdir(detection_output_path)

        logging.info('Detecting touches for video: [{}]'.format(os.path.split(self.video_path)[1]))

        # config = tf.ConfigProto(inter_op_parallelism_threads=4,
        #                         allow_soft_placement=True)

        start_detection_time = datetime.datetime.now().replace(microsecond=0)

        detect_fn = tf.saved_model.load(self.model_path)

        # begin a tf session to begin detecting touches
        # with detection_graph.as_default():
        #     with tf.Session(graph=detection_graph, config=config) as sess:
        for image_path in ProgressBar.display(extracted_frames, "Computing: ", 40):
            # print(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.

            # change the method to load image into np array
            # image = Image.open(image_path)
            # image_np = ImageUtils.load_image_into_np_array(image)

            image_np = np.array(Image.open(image_path))

            # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
            input_tensor = tf.convert_to_tensor(image_np)
            # The model expects a batch of images, so add an axis with `tf.newaxis`.
            input_tensor = input_tensor[tf.newaxis, ...]

            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            input_tensor = np.expand_dims(image_np, axis=0)
            # image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.

            detections = detect_fn(input_tensor)

            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                          for key, value in detections.items()}
            detections['num_detections'] = num_detections
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

            boxes = detections['detection_boxes']
            # Each score represents how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detections['detection_scores']
            classes = detections['detection_classes']
            num_detections = int(detections.pop('num_detections'))

            # num_detections = detection_graph.get_tensor_by_name('num_detections:0')
            # Actual detection.
            # (boxes, scores, classes, num_detections) = sess.run(
            #     [boxes, scores, classes, num_detections],
            #     feed_dict={image_tensor: image_np_expanded})

            # boxes = boxes[0]
            # scores = scores[0]

            # add each detected tap to a Frame object
            base_name = ntpath.basename(image_path)
            base_name, file_extension = os.path.splitext(base_name)

            detection = Frame(int(base_name))
            (im_width, im_height) = image_np.shape[1], image_np.shape[0]
            for i in range(len(boxes)):
                box = boxes[i]
                score = scores[i]

                if score > 0.5:
                    # Add detection box on the image data
                    vis_util.visualize_boxes_and_labels_on_image_array(
                        image_np,
                        np.squeeze(boxes),
                        np.squeeze(classes).astype(np.int32),
                        np.squeeze(scores),
                        category_index,
                        use_normalized_coordinates=True,
                        line_thickness=8)

                    yMin = box[0] * im_height
                    xMin = box[1] * im_width
                    yMax = box[2] * im_height
                    xMax = box[3] * im_width
                    # calculate avg x-coord and avg y-coord
                    # for tap
                    x = xMin + ((xMax - xMin) / 2.0)
                    y = yMin + ((yMax - yMin) / 2.0)
                    detection.add_tap(ScreenTap(x, y, float(score)))

            if (len(detection.get_screen_taps()) > 0):
                self.touch_detections.append(detection)

            # place bbox images in "detected_frames" directory
            output_image_file = os.path.join(detection_output_path, 'bbox-' + base_name + file_extension)
            # print('Processing: ' + output_image_file, flush=True)
            # Don't remove, fixes weird error: https://stackoverflow.com/questions/19600147/sorl-thumbnail-encoder-error-2-when-writing-image-file/41018959#41018959
            ImageFile.MAXBLOCK = im_width * im_height
            ImageUtils.save_image_array_as_jpg(image_np,
                                               os.path.join(detection_output_path,
                                                            'bbox-' + base_name + file_extension))

        end_detection_time = datetime.datetime.now().replace(microsecond=0)
        self.set_detection_time(end_detection_time - start_detection_time)
        logging.info("Touch detection process took: " + str(self.detection_time))

    def set_object_det_path(self, path):
        """
        Changes object_det_path to specified value.

        Parameters
        ----------
        path : string
            new object_det_path
        """
        self.object_det_path = path

    def set_model_path(self, path):
        """
        Changes model_path to specified value.
        
        Parameters
        ----------
        path : string
            new model_path
        """
        self.model_path = path

    def get_model_path(self):
        """
        Returns model_path.

        Returns
        -------
        model_path : string
            path to frozen graph
        """
        return self.model_path

    def set_labelmap_path(self, path):
        """
        Changes labelmap_path to specified value.
        
        Parameters
        ----------
        path : string
            new labelmap_path
        """
        self.labelmap_path = path

    def get_labelmap_path(self):
        """
        Returns labelmap_path.

        Returns
        -------
        labelmap_path : string
            path to labelmap of detections
        """
        return self.labelmap_path

    def set_video_path(self, path):
        """
        Changes video_path to specified value.

        Parameters
        ----------
        path : string
            new video_path
        """
        self.video_path = path

    def get_video_path(self):
        """
        Returns video_path.

        Returns
        -------
        video_path : string
            path to extracted frames from frame extractor
        """
        return os.path(self.video_path, "extracted_frames")

    def get_touch_detections(self):
        """
        Returns touch detections.

        Returns
        -------
        touch_detections : dict of string:Frames
            touch detections
        """
        return self.touch_detections

    def set_touch_detections(self, dets):
        """
        Changes touch detections to specified value.

        Parameters
        ----------
        dets : dict of string:Frames
            new touch detections
        """
        self.touch_detections = dets
