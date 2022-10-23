# MY ACCESSIBILITY SERVICE (COPYPASTE APP)

Updated implementation of [Accessbilityservice](https://gitlab.com/cheefengcheong/accessibilityservice/-/tree/master/BackendWithV2S/flask_application) with capabilities to run on Tensorflow 2.x and Python >= 3.6. 

## Introduction
This application was built and extended by two groups of students for their final year IT project. 
Its purpose is for users to be able to upload screenrecorded demonstrations of user actions and to convert them into a shortcut that can be replayed into their device. 

## Usage
The front-end application, which is run on the device, will allow the user to upload a video demonstration. This video will then be broken down through a modified version of [V2S](https://gitlab.com/SEMERU-Code-Public/Android/video2scenario/-/tree/master/python_v2s) to extract the detected action components. These actions will be stored in a json file with the action type, location and action hint. 

Once complete, the user will be able to enable the shortcut and rerun the action from the video onto their own device. 

The device loops through the json file and executes the action type at the specific location. After each action execution, the device checks the similatrity of the device screen and the video frame and if the similarity percent is below 90, it will try and rerun the previous action execution. After three tries, an 'action hint' will appear on the screen to prompt the user to click the right button/location. 

## Pre-requisites

### Model Links
Unable to store models on github repo due to size limitations. Please download the below files and place them in the correct folders. 
Link to Models: https://drive.google.com/drive/folders/1Hvd3IYrseYh7yO4uVlOu2qgHnuw1NZGc?usp=sharing

Model Type | Model Name | Location | 
--- | --- | --- |
Opactiy Model | model-saved-alex8-tuned.h5 | ```pythonv2s/v2s/phase1/detection/opacity_model/``` | 
Touch Model | frozen_inference_graph_n5.pb | ```pythonv2s/v2s/phase1/detection/touch_model/saved_model_n5/``` | 
Touch Model | saved_model.pb | ```pythonv2s/v2s/phase1/detection/touch_model/saved_model_n5/``` | 
Touch Model | frozen_inference_graph_n6.pb | ```pythonv2s/v2s/phase1/detection/touch_model/saved_model_n6p/``` | 
Touch Model | saved_model.pb | ```pythonv2s/v2s/phase1/detection/touch_model/saved_model_n6/``` | 
Touch Model | saved_model.pb | ```pythonv2s/v2s/phase1/detection/touch_model/saved_model_n7/``` | 

### Environment
1. Ceate a conda environment with python
2. Run ```cd to \BackendWithV2S\python_v2s``
3. Run ```pip install .``` or manually install the following list of requirements 
    - 'ffmpeg',
    - 'ffmpeg-python',
    - 'Keras==2.2.4',
    - 'Keras-Applications==1.0.8',
    - 'Keras-Preprocessing==1.1.0',
    - 'matplotlib==3.1.1',
    - 'numpy>=1.20.2',
    - 'Pillow==6.2.0',
    - 'scipy==1.3.1',
    - 'tensorboard==2.0.0',
    - 'tensorflow==2.5.0',
    - 'tensorflow-macos==2.0.0' (only install if you run a MacOS device)
4. Run ```cd to \BackendWithV2S\flask_application```
5. Run ```pip install -r requirements.txt```
6. Create an uploads folder in main directory 

### Docker
Needed for redis, which is a database then can save our result. Create and start an image of the backend. 
1. Download docker, install needed dependency such as WSL
2. Run ```docker pull redis```
3. Run ```docker run -d -p 6379:6379 redis```

### Emulator
Only set up if emulator is needed. 
1. On Android Studio, add a new device to Device Manager and choose Nexus 5
2. Select API33 System Image with the target that says Google API
3. Click Advanced Settings and change the Internal Storage and SD Card to 2000MB (or a value larger than 800) 
4. Open the Emulator and click Extended Controls (three dots on the side)
5. Settings -> Proxy -> Change Host to your IPV4 Address 

## Running the Application 
### Backend
1. Activate your environment
2. ```cd to \BackendWithV2S\flask_application```
3. Run ```python3 app.py```
4. In another cmd/terminal, run ```celery -A app.celery worker --loglevel=INFO --pool=solo``` to run celery, which is a task queue system
4. Open your docker application
5. Find the container that you have created last time for redis, start the image
6. To remove queue task run celery -A app.celery purge in cmd.

### Front-end
1. Build Gradle file located in ```\MyAccessibilityServce\```
2. In MainApplication.py change the ip address to be static to your ipv4 address
3. Open AccessibilityService App
4. Click 'Upload Video' Button and select video
5. A pop-up should appear notifying that the video is being processed
6. Click 'Check Progress' for video updates
7. Once complete, go to phone settings -> accessibility
8. Allow AccessibilityService access. 'Do Action' pop-up button should appear. 
9. Navigate to first screen of video demonstration. Click Do Action. 

## Modifications/Known Issues
* Network Address: Previous issues running ```flask run``` on ipv4 local network. Current Fix: hardcoding ipv4 address in app.py and running ```python3 app.py```
* Update State for Extracted Actions: Bug when trying to update state with extracted actions in ```app.py```. Current Fix: Comment out update line. Click 'Check Progress' button to see when the application load is successful. 

### How to run Tensorflow Lite Object detection Model
1. The normal ```pip install tflite-support``` will not work in most machines due to the tflite-support team changed they way they release
2. We need to use ```Bazel```, this is the website```https://bazel.build/```
3. The basic idea is to build your own ```wheel``` file which only works in your local machine
4. First you need to clone the git repo ```https://github.com/tensorflow/tflite-support``` into a folder
5. Once you installed the ```Bazel```, you can use the following script within the folder of the ```tflite-support```
This is the script ```bazel build -c opt tensorflow_lite_support/tools/pip_package:build_pip_package```
Once the build is finished, you can ```cd``` to where the file ```bazel-bin``` located.
Then you can run this script to produce the ```wheel``` file 
```./bazel-bin/tensorflow_lite_support/tools/pip_package/build_pip_package --dst wheels --nightly_flag```
6. Copy and paste the ```wheel``` file to the folder where the CopyPasteApp is.
7. Use ```pip install``` to install the wheels file

