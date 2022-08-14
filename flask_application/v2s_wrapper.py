import json
import os
import sys
sys.path.append(os.path.abspath(os.getcwd()).strip('flask_application') + "/python_v2s")
from v2s.pipeline import PipelineV2S

def execute_v2s(filepath):
    scene_config = {
        "video_path": filepath,
        "device_model": "Nexus_5",
        "arch": "x86",
        "emulator": "True",
       "touch_model": "/phase1/detection/touch_model/saved_model_n5/frozen_inference_graph_n5.pb",
        "labelmap": "/phase1/detection/touch_model/v2s_label_map.pbtxt",
        "opacity_model": "/phase1/detection/opacity_model/model-saved-alex8-tuned.h5", 
        "app_name": "<APP_NAME>"
    }
    # this is the path to use ssd model instead of faster rcnn, replace line 13 with the line below
    # "touch_model": "v2s/phase1/detection/touch_model/my_model/saved_model/",

    # v2s = PipelineV2S(scene_config)
    # v2s.execute()
    name, extension = os.path.splitext(filepath)
    detected_actions_path =  name + '/detected_actions.json'
    detected_actions = open(detected_actions_path, 'r')
    json_result = json.load(detected_actions)
    return json_result


if __name__ == "__main__":
    pass
