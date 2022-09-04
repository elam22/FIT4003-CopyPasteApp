import math
import os
import re
import difflib
from v2s.util.general import JSONFileUtils
import requests
import json
from base64 import b64encode


class TextBoundArray:
    def __init__(self, text_bounds):
        self.text_bounds = text_bounds

    def find_nearest_text(self, coordinate):
        for text_bound in self.text_bounds:
            if text_bound.in_bound(coordinate):
                return text_bound.text

        manhattan_distance = math.inf
        text = ""
        for text_bound in self.text_bounds:
            distance_from_center = text_bound.get_distance(coordinate)

            # scale the vertical distance so that horizontal element is preferred
            distance = distance_from_center["x"] + distance_from_center["y"] * 5

            if distance < manhattan_distance:
                manhattan_distance = distance
                text = text_bound.text

        return text


class TextBound:
    def __init__(self, text, vertices):
        self.text = text
        self.top_left = vertices[0]
        self.top_right = vertices[1]
        self.bottom_right = vertices[2]
        self.bottom_left = vertices[3]
        self.center = {"x": (self.top_left["x"] + self.top_right["x"]) / 2,
                       "y": (self.top_left["y"] + self.bottom_left["y"]) / 2}

    def get_center(self):
        return self.center

    def in_bound(self, coordinate):
        return self.top_left["x"] < coordinate["x"] < self.top_right["x"] \
               and self.top_left["y"] < coordinate["y"] < self.bottom_left["y"]

    def get_distance(self, coordinate):
        return {"x": abs(self.center["x"] - coordinate["x"]), "y": abs(self.center["y"] - coordinate["y"])}


def ocr(img_path):
    ocr_result = ocr_detection_google(img_path)
    # filtered_text = remove_symbol(filter_noise(ocr_result))

    res = ''
    for result in ocr_result:
        res += result['description']

    # return filtered_text
    return res

def google_ocr_make_image_data(img_path):
    with open(img_path, 'rb') as f:
        ctxt = b64encode(f.read()).decode()
        img_req = {
            'image': {
                'content': ctxt
            },
            'features': [{
                'type': 'DOCUMENT_TEXT_DETECTION',
                # 'type': 'TEXT_DETECTION',
                'maxResults': 1
            }]
        }
    return json.dumps({"requests": img_req}).encode()


def ocr_detection_google(img_path):
    url = 'https://vision.googleapis.com/v1/images:annotate'
    api_key = 'AIzaSyC9Vx_8fQbreU_WpPr39tN2oRxgHY5i5WQ'  # *** Replace with your own Key ***
    img_data = google_ocr_make_image_data(img_path)
    response = requests.post(url,
                             data=img_data,
                             params={'key': api_key},
                             headers={'Content_Type': 'application/json'})
    if response.json()['responses'] == [{}]:
        # No Text
        return None
    else:
        return response.json()['responses'][0]['textAnnotations'][1:]


def filter_noise(respond):
    valid_texts = ''
    for i in range(len(respond)):
        current_text = respond[i]["description"]
        if len(current_text) <= 1 and current_text.lower() not in ['a', ',', '.', '!', '?', '$', '%', ':', '&', '+']:
            continue
        valid_texts += current_text
    return valid_texts


def remove_symbol(string):
    new_string = ''
    for char in string:
        current_char_value = ord(char)
        if (65 <= current_char_value <= 90) or (97 <= current_char_value <= 122):
            new_string += char
    return new_string


def identify_type(extracted_actions):
    actions = []
    type_action = {}
    type_start = None

    for i in range(len(extracted_actions)):
        ocr_result = extracted_actions[i]['resulting_screen_ocr']
        keyboard_pattern = re.search(r'[asdfghjkl]{5,}.*[zxcvbnm]{5,}', ocr_result)

        if not keyboard_pattern:
            if type_action:
                actions.append(type_action)
            else:
                actions.append(extracted_actions[i])
        elif keyboard_pattern and not type_start:
            type_start = extracted_actions[i]
            type_action = {'act_type': "TYPE", 'actions': [extracted_actions[i]]}
        elif keyboard_pattern and i != len(extracted_actions) - 1:
            type_action['actions'].append(extracted_actions[i])
        elif keyboard_pattern and i == len(extracted_actions) - 1:
            type_action['actions'].append(extracted_actions[i])
            actions.append(type_action)

    for action in actions:
        if action['act_type'] == 'TYPE':
            detect_potential_type_text(action)

    return actions

def detect_potential_type_text(type_actions):
    type_end_ocr = type_actions['actions'][-1]['resulting_screen_ocr']
    type_start_ocr = type_actions['actions'][0]['resulting_screen_ocr']
    difference = difflib.ndiff(type_start_ocr, type_end_ocr)

    # print(''.join(difference), end='')

    potential_types = []
    type_text = ''
    prev_text_idx = -1

    for j, s in enumerate(difference):
        if s[0] == '+':
            # print(u'Add "{}" to position {}'.format(s[-1], j))
            if len(type_text) == 0:
                type_text = s[-1]
            elif j == prev_text_idx + 1:
                type_text += s[-1]
            else:
                potential_types.append(type_text)
                type_text = s[-1]
            prev_text_idx = j
        elif len(type_text) > 0:
            potential_types.append(type_text)
            type_text = ''

    # for k in potential_types:
    #     print(k)

    type_actions['potential_types'] = potential_types


def extract_action(incomplete_actions, filepath):
    prev = incomplete_actions[0]
    screenId = [prev["screenId"]]
    taps = [prev["screenTap"][0]]
    detected_actions = []
    for action in incomplete_actions[1:]:
        try:
            if action["screenId"] - prev["screenId"] == 1:
                screenId.append(action["screenId"])
                taps.append(action["screenTap"][0])
                prev = action
            else:

                together = {"act_type": getAction(taps), "frames": screenId, "taps": taps}
                getAction(taps)
                detected_actions.append(together)
                prev = action
                screenId = [action["screenId"]]
                taps = [action["screenTap"][0]]
        except NameError:
            print("error")

    getAction(taps)
    together = {"act_type": getAction(taps), "frames": screenId, "taps": taps}
    detected_actions.append(together)

    JSONFileUtils.output_data_to_json(detected_actions, os.path.join(filepath.rsplit(".", 1)[0], "detected_actions.json"))

    actions = []
    for detected_action in detected_actions:
        action = dict()
        action['first_frame'] = detected_action["frames"][0]
        if detected_action["act_type"] == 'CLICK':
            action["act_type"] = detected_action["act_type"]
            x = 0
            y = 0
            for tap in detected_action["taps"]:
                x += tap["x"]
                y += tap["y"]

            coord = dict()
            coord["x"] = x // len(detected_action["taps"])
            coord["y"] = y // len(detected_action["taps"])
            action["taps"] = [coord]
        elif detected_action["act_type"] == 'SWIPE':
            action["act_type"] = detected_action["act_type"]
            x = 0
            y = 0
            action["taps"] = []
            for tap in detected_action["taps"]:
                x = tap["x"]
                y = tap["y"]

                coord = {}
                coord["x"] = x // 1
                coord["y"] = y // 1
                action["taps"].append(coord)
        elif detected_action["act_type"] == 'LONG_CLICK':
            action["act_type"] = detected_action["act_type"]
            x = 0
            y = 0
            for tap in detected_action["taps"]:
                x += tap["x"]
                y += tap["y"]

            coord = dict()
            coord["x"] = x // len(detected_action["taps"])
            coord["y"] = y // len(detected_action["taps"])
            action["taps"] = [coord]
        actions.append(action)

    return actions


def get_action_hint(file_path, action_coordinate):
    ocr_result = ocr_detection_google(file_path)
    text_objects = []
    for text in ocr_result:
        text_object = TextBound(text['description'], text['boundingPoly']['vertices'])
        text_objects.append(text_object)

    text_bound_array = TextBoundArray(text_objects)
    return text_bound_array.find_nearest_text(action_coordinate)


def getAction(taps):
    n = len(taps)
    x0 = taps[0]["x"]
    y0 = taps[0]["y"]
    x1 = taps[n // 2]["x"]
    y1 = taps[n // 2]["y"]
    x2 = taps[n - 2]["x"]
    y2 = taps[n - 2]["y"]

    if disBetweenPoint(x0, y0, x2, y2) > 5:
        return "SWIPE"
    else:
        if n > 30:
            return "LONG_CLICK"
        else:
            return "CLICK"


def disBetweenPoint(x1, y1, x2, y2):
    distance = math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))
    return distance

if __name__ == "__main__":
    pass
