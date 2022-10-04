import os
import re
import math
import json
import difflib
import requests
from PIL import Image
from base64 import b64encode
from v2s.util.general import JSONFileUtils


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

    def get_text_bounds(self):
        return self.text_bounds

    def to_json(self):
        dic = []
        for t in self.text_bounds:
            dic.append(t.to_json())
        return dic


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

    def to_json(self):
        return json.dumps(self.__dict__)

# class ComplexEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if hasattr(obj, 'asJson'):
#             return obj.asJson()
#         else:
#             return json.JSONEncoder.default(self, obj)
#
#
# class JSONFileUtils():
#     """
#     Contains methods to read data from json files.
#
#     Methods
#     -------
#     read_data_from_json(file_path)
#         Reads data from json file.
#     output_data_to_json(data, file_path)
#         Outputs data to json file using ComplexEncoder.
#     """
#
#     @staticmethod
#     def read_data_from_json(file_path):
#         """
#         Reads data from json file.
#
#         Parameters
#         ----------
#         file_path : string
#             path to file to read from
#
#         Returns
#         -------
#         data :  dict
#             json information
#         """
#         file_path = os.path.join(file_path)
#         file_json = open(file_path, 'r')
#         data = json.load(file_json)
#         file_json.close()
#         return data
#
#     @staticmethod
#     def output_data_to_json(data, file_path):
#         """
#         Outputs data to json file using ComplexEncoder.
#
#         Parameters
#         ----------
#         data :
#             data to output to json
#         file_path : string
#             path to file to output to
#         """
#         json_data = json.dumps(data, cls=ComplexEncoder, sort_keys=True)
#         file = open(file_path, "w+")
#         file.write(json_data)
#         file.close()


def ocr(img_path):
    # ocr_result = JSONFileUtils.read_data_from_json("C:/Users/w7947/Desktop/FIT4003-CopyPasteApp/flask_application/asset/test/ocr.json")
    ocr_result = ocr_detection_google(img_path)
    filtered_text = remove_symbol(filter_noise(ocr_result))
    unfiltered_text = unfiltered_screen_ocr(ocr_result)
    text_bounds = text_bound_from_ocr_result(ocr_result)

    return {"resulting_screen_ocr": filtered_text, "unfiltered_screen_ocr": unfiltered_text, "text_bounds": text_bounds}


def test_ocr(img_path):
    ocr_result = JSONFileUtils.read_data_from_json("C:/Users/w7947/Desktop/FIT4003-CopyPasteApp/flask_application/asset/test/test_ocr.json")
    # ocr_result = test_ocr_detection_google(img_path)
    filtered_text = remove_symbol(filter_noise(ocr_result))
    unfiltered_text = unfiltered_screen_ocr(ocr_result)
    text_bounds = text_bound_from_ocr_result(ocr_result)

    return {"resulting_screen_ocr": filtered_text, "unfiltered_screen_ocr": unfiltered_text, "text_bounds": text_bounds}


def test_ocr_detection_google(img_path):
    url = 'https://vision.googleapis.com/v1/images:annotate'
    api_key = ''  # *** Replace with your own Key ***
    img_data = google_ocr_make_image_data(img_path)
    response = requests.post(url,
                             data=img_data,
                             params={'key': api_key},
                             headers={'Content_Type': 'application/json'})
    if response.json()['responses'] == [{}]:
        # No Text
        return None
    else:
        # print("output")
        JSONFileUtils.output_data_to_json(response.json()['responses'][0]['textAnnotations'][1:], "C:/Users/w7947/Desktop/FIT4003-CopyPasteApp/flask_application/asset/test/test_ocr.json")
        return response.json()['responses'][0]['textAnnotations'][1:]


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
        # print("output")
        JSONFileUtils.output_data_to_json(response.json()['responses'][0]['textAnnotations'][1:], "C:/Users/w7947/Desktop/FIT4003-CopyPasteApp/flask_application/asset/test/ocr.json")
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


def unfiltered_screen_ocr(ocr_result):
    res = ''
    for result in ocr_result:
        res += result['description']

    return res


def identify_type(extracted_actions, file_path):
    actions = group_type_action(extracted_actions)

    # detect text
    for action in actions:
        if action['act_type'] == 'TYPE':
            action["potential_type"] = detect_potential_type_text(action, file_path)

    return actions


def group_type_action(extracted_actions):
    actions = []
    type_action = {}
    type_start = False

    for i in range(len(extracted_actions)):
        action = extracted_actions[i]
        keyboard_pattern = re.search(r'[asdfghjkl]{5,}.*[zxcvbnm]{5,}', action['unfiltered_screen_ocr'])

        if not keyboard_pattern:
            if type_start:
                actions.append(type_action)
                type_action = {}
                type_start = False

            actions.append(action)
        elif not type_start:
            type_start = True
            type_action = {'act_type': "TYPE", 'actions': [action]}
        else:
            type_action['actions'].append(action)

    if type_start:
        actions.append(type_action)

    return actions


def detect_potential_type_text(type_actions, file_path):
    type_start = type_actions['actions'][0]
    for action in type_actions['actions']:
        if action["act_type"] == "CLICK" and len(action["action_hint"]) == 1:
            type_start = action
            break

    potential_type_by_location = find_text_by_location(type_actions, type_start, file_path)

    type_start_ocr = type_start['unfiltered_screen_ocr']
    type_end_ocr = type_actions['actions'][-1]['unfiltered_screen_ocr']
    potential_type_by_difference = find_text_by_difference(type_start_ocr, type_end_ocr)

    potential_type = find_potential_type(potential_type_by_location, potential_type_by_difference)

    return potential_type


def generate_mask(target_image):
    width, height = target_image.size

    top_mask = Image.new("RGBA", (width, 200), (255, 255, 255))
    keyboard_mask = Image.new("RGBA", (width, 700), (255, 255, 255))

    return {"top_mask": top_mask, "keyboard_mask": keyboard_mask}


def mask_image(target_image, mask, file_path, screen_number):
    save_path = os.path.join(file_path.rsplit(".", 1)[0], "masked_frames", f"{screen_number}.jpg")
    print(save_path)
    width, height = target_image.size
    top_mask = mask["top_mask"]
    keyboard_mask = mask["keyboard_mask"]

    target_image.paste(top_mask, (0, 0), top_mask)
    target_image.paste(keyboard_mask, (0, height - 700), keyboard_mask)

    if not os.path.isdir(os.path.join(file_path.rsplit(".", 1)[0], "masked_frames")):
        os.mkdir(os.path.join(file_path.rsplit(".", 1)[0], "masked_frames"))
    target_image.save(save_path)

    return save_path


def find_text_by_location(type_actions, type_start, file_path):
    type_start_screen_number = type_start['screen_number']
    type_end_screen_number = type_actions['actions'][-1]['screen_number']

    type_start_screen = Image.open(os.path.join(file_path.rsplit(".", 1)[0], "extracted_frames", f"{type_start_screen_number}.jpg"))
    type_end_screen = Image.open(os.path.join(file_path.rsplit(".", 1)[0], "extracted_frames", f"{type_end_screen_number}.jpg"))

    masked_type_start_screen_path = mask_image(type_start_screen, generate_mask(type_start_screen), file_path, type_start_screen_number)
    masked_type_end_screen_path = mask_image(type_end_screen, generate_mask(type_end_screen), file_path, type_end_screen_number)

    masked_type_start_action_hint = type_start['action_hint']
    masked_type_start_ocr = ocr(masked_type_start_screen_path)
    # masked_type_start_ocr = test_ocr(masked_type_start_screen_path)
    masked_type_start_text_bounds = masked_type_start_ocr["text_bounds"].get_text_bounds()

    type_start_text_bound_center = masked_type_start_text_bounds[0].get_center()
    for text_bound in masked_type_start_text_bounds:
        if text_bound.text == masked_type_start_action_hint:
            type_start_text_bound_center = text_bound.get_center()
            break

    masked_type_end_ocr = ocr(masked_type_end_screen_path)
    # masked_type_end_ocr = test_ocr(masked_type_end_screen_path)
    masked_type_end_text_bounds = masked_type_end_ocr["text_bounds"].get_text_bounds()

    potential_type = ''
    for text_bound in masked_type_end_text_bounds:
        if text_bound.in_bound(type_start_text_bound_center):
            potential_type = text_bound.text
            break

    return potential_type

def find_text_by_difference(type_start_ocr, type_end_ocr):
    difference = difflib.ndiff(type_start_ocr, type_end_ocr)

    # print(''.join(difference), end='')

    text_diffs = []
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
                text_diffs.append(type_text)
                type_text = s[-1]
            prev_text_idx = j
        elif len(type_text) > 0:
            text_diffs.append(type_text)
            type_text = ''

    return text_diffs


def find_potential_type(type_by_location, type_by_difference):
    for t in type_by_difference:
        if t == type_by_location:
            return t
    return type_by_location


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

    JSONFileUtils.output_data_to_json(detected_actions,
                                      os.path.join(filepath.rsplit(".", 1)[0], "detected_actions.json"))

    actions = []
    for detected_action in detected_actions:
        action = dict()
        action["first_frame"] = detected_action["frames"][0]
        action["last_frame"] = detected_action["frames"][-1]
        if detected_action["act_type"] == 'CLICK':
            action["act_type"] = detected_action["act_type"]
            x = 0
            y = 0
            for tap in detected_action["taps"]:
                x += tap["x"]
                y += tap["y"]

            coord = {"x": x // len(detected_action["taps"]), "y": y // len(detected_action["taps"])}
            action["taps"] = [coord]
        elif detected_action["act_type"] == 'SWIPE':
            action["act_type"] = detected_action["act_type"]
            x = 0
            y = 0
            action["taps"] = []
            for tap in detected_action["taps"]:
                x = tap["x"]
                y = tap["y"]

                coord = {"x": x // 1, "y": y // 1}
                action["taps"].append(coord)
        elif detected_action["act_type"] == 'LONG_CLICK':
            action["act_type"] = detected_action["act_type"]
            x = 0
            y = 0
            for tap in detected_action["taps"]:
                x += tap["x"]
                y += tap["y"]

            coord = {"x": x // len(detected_action["taps"]), "y": y // len(detected_action["taps"])}
            action["taps"] = [coord]
        actions.append(action)

    return actions


def text_bound_from_ocr_result(ocr_result):
    text_objects = []
    for text in ocr_result:
        text_object = TextBound(text['description'], text['boundingPoly']['vertices'])
        text_objects.append(text_object)

    return TextBoundArray(text_objects)


def get_action_hint(file_path, action_coordinate):
    ocr_result = ocr_detection_google(file_path)
    text_bounds = text_bound_from_ocr_result(ocr_result)

    return text_bounds.find_nearest_text(action_coordinate)


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
    # ocr_detection_google("C:/Users/w7947/Desktop/FIT4003-CopyPasteApp/flask_application/asset/test/extracted_frames/0001.jpg")
    pass
