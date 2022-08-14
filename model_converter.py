import tensorflow as tf
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings


if __name__ =="__main__":

    # Convert the model
    saved_model_dir = "C:\\Users\\work\\Desktop\\school\\FIT4003\\Tensorflow\\workspace\\training\\models\\ssd_mobile_net_v2_tflite\\saved_model"
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    # converter.target_spec.supported_ops = [
    #     tf.lite.OpsSet.TFLITE_BUILTINS,  # enable TensorFlow Lite ops.
    #     tf.lite.OpsSet.SELECT_TF_OPS  # enable TensorFlow ops.
    # ]
    tflite_model = converter.convert()
    open("converted_model.tflite", "wb").write(tflite_model)

    #   # # Convert the model.
    #   # converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
    #   #     graph_def_file='C:\\Users\\work\\Desktop\\school\\FIT4003\\accessibilityservice\\BackendWithV2S\\python_v2s\\v2s\\phase1\\detection\\touch_model\\saved_model_n5\\frozen_inference_graph_n5.pb',
    #   #                     # both `.pb` and `.pbtxt` files are accepted.
    #   #     input_arrays=['input'],
    #   #     input_shapes={'input' : [1, 224, 224,3]},
    #   #     output_arrays=['MobilenetV1/Predictions/Softmax']
    #   # )
    #   # tflite_model = converter.convert()
    #   #
    #   # # Save the model.
    #   # with open('model.tflite', 'wb') as f:
    #   #   f.write(tflite_model)
    #
    # # Convert the model.
    # saved_model_dir = 'C:\\Users\\work\\Desktop\\school\\FIT4003\\accessibilityservice\\BackendWithV2S\\python_v2s\\v2s\\phase1\\detection\\touch_model\\my_model\\saved_model'
    # detect_fn = tf.saved_model.load(saved_model_dir)
    # # with tf.Session() as sess:
    # #   model = tf.saved_model.load(sess, ['serve'], saved_model_dir)
    # def load_image_into_numpy_array(path):
    #     """Load an image from file into a numpy array.
    #
    #     Puts image into numpy array to feed into tensorflow graph.
    #     Note that by convention we put it into a numpy array with shape
    #     (height, width, channels), where channels=3 for RGB.
    #
    #     Args:
    #     path: the file path to the image
    #
    #     Returns:
    #     uint8 numpy array with shape (img_height, img_width, 3)
    #     """
    #     return np.array(Image.open(path))
    #
    #
    # for image_path in IMAGE_PATHS:
    #     print('Running inference for {}... '.format(image_path), end='')
    #
    #     image_np = load_image_into_numpy_array(image_path)
    #
    #     # Things to try:
    #     # Flip horizontally
    #     # image_np = np.fliplr(image_np).copy()
    #
    #     # Convert image to grayscale
    #
    #     # image_np = np.tile(
    #     #     np.mean(image_np, 2, keepdims=True), (1, 1, 3)).astype(np.uint8)
    #
    #     # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    #     input_tensor = tf.convert_to_tensor(image_np)
    #     # The model expects a batch of images, so add an axis with `tf.newaxis`.
    #     input_tensor = input_tensor[tf.newaxis, ...]
    #
    #     # input_tensor = np.expand_dims(image_np, 0)
    #     detections = detect_fn(input_tensor)
    #
    #     # All outputs are batches tensors.
    #     # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    #     # We're only interested in the first num_detections.
    #     num_detections = int(detections.pop('num_detections'))
    #     detections = {key: value[0, :num_detections].numpy()
    #                 for key, value in detections.items()}
    #     detections['num_detections'] = num_detections
    #
    #     # detection_classes should be ints.
    #     detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
    #
    #     image_np_with_detections = image_np.copy()
    #
    #     viz_utils.visualize_boxes_and_labels_on_image_array(
    #       image_np_with_detections,
    #       detections['detection_boxes'],
    #       detections['detection_classes'],
    #       detections['detection_scores'],
    #       category_index,
    #       use_normalized_coordinates=True,
    #       max_boxes_to_draw=200,
    #       min_score_thresh=.30,
    #       agnostic_mode=False)
    #
    #     # plt.figure()
    #     plt.imshow(image_np_with_detections)
    #     plt.show()
    #     print('Done')
    # plt.show()