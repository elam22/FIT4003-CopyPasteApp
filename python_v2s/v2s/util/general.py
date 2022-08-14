################################################################################
# Copyright (c) 2011-2013, Lorenzo Gomez (lorenzobgomez@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of 
# conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this list 
# of conditions and the following disclaimer in the documentation and/or other materials 
# provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED 
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################

import json
import math
import os
import subprocess as sp
import sys
from threading import Thread

import numpy as np
import tensorflow as tf
from PIL import Image, ImageFile

from v2s.util.constants import DIST_THRESHOLD

class ProgressBar():
    """
    Enables progress bar to be output.

    Methods
    -------
    display(data, prefix, size, file)
        Displays a progress bar to the screen.
    """
    @staticmethod
    def display(data, prefix="", size=50, file=sys.stdout):
        """
        Displays a progress bar to terminal screen or other file specified.

        Parameters
        ----------
        data : 
            data being processed that progress data is desired about
        prefix : string, optional
            value to output before bar
        size : int, optional
            size of bar
        file : string, optional
            file to output to
        """
        count = len(data)

        def show(curr_prog):
            x = int(size * curr_prog / count)
            file.write("%s[%s%s] %i/%i\r" % (prefix, "#" * x, "." * (size - x), curr_prog, count))
            file.flush()

        show(0)
        for i, item in enumerate(data):
            yield item
            show(i + 1)
        file.write("\n")
        file.flush()

class ImageUtils():
    """
    Static methods for images.

    Methods
    -------
    load_image_into_numpy_array(image)
        Loads image data into a numpy array.
    save_image_array_as_jpg(image, output_path)
        Saves an image (represented as a numpy array) to JPEG.
    """

    @staticmethod
    def load_image_into_np_array(image):
        """
        Loads image into a numpy array.

        Parameters
        ----------
        image :
            image to be converted

        Returns
        -------
        np array : 
            a np array with shape [heigh, width, 3]
        """
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape(
                        (im_height, im_width, 3)).astype(np.uint8)

    @staticmethod
    def save_image_array_as_jpg(image, output_path):
        """
        Saves an image (represented as a numpy array) to JPEG.

        Parameters
        ----------
        image :
            a numpy array with shape [height, width, 3]
        output_path : 
            path to which image should be written
        """
        image_pil = Image.fromarray(np.uint8(image)).convert('RGB')
        with tf.io.gfile.GFile(output_path, 'w') as fid:
            image_pil.save(fid, 'JPEG', quality=80, optimize=True, 
                           progressive=True)


class GeneralUtils():
    """
    General utils like distance functions, and other functions that are used
    throughout the pipeline.

    Methods
    -------
    get_distance(tap1, tap2)
        Returns the distance between two taps based on their x,y coords.
    are_consecutive_frames(action1, action2)
        Returns boolean depicting whether the frames in two actions are
        consecutive. May signify that those two actions can be merged.
    close_complex_actions(action1, action2, distance)
        Returns whether two actions are close in distance. May signify that 
        two actions can be merged.
    """

    @staticmethod
    def get_distance(tap1, tap2):
        """
        Returns the distance between two taps based on their x,y coords.
        
        Parameters
        ----------
        tap1 : 
            first tap
        tap2 : 
            second tap
        """
        x2 = (tap2.get_x() - tap1.get_x()) ** 2
        y2 = (tap2.get_y() - tap1.get_y()) ** 2
        return math.sqrt(x2 + y2)
    
    @staticmethod
    def are_consecutive_frames(action1, action2):
        """
        Returns boolean depicting whether the frames in two actions are
        consecutive. May signify that those two actions can be merged.

        Parameters
        ----------
        action1 : 
            first action
        action2 :
            second action
        """
        frames1 = action1.get_frames()
        frames2 = action2.get_frames()
        # return if the last frame of the first action has id+1 of the
        # first frame in the second action
        return frames1[-1] == frames2[0] - 1

    @staticmethod
    def close_complex_actions(action1, action2, distance=DIST_THRESHOLD):
        """
        Returns whether two actions are close in distance. May signify that 
        two actions can be merged.

        Parameters
        ----------
        action1 : 
            first action
        action2 :
            second action
        distance : optional
            distance threshold to say they are close or not; default is 31
        """
        # compare dist of last tap in action1 and first tap in action2
        taps_list_1 = action1.get_taps()
        taps_list_2 = action2.get_taps()
        tap1 = taps_list_1[-1]
        tap2 = taps_list_2[0]
        return GeneralUtils.get_distance(tap1, tap2) < distance

class RecordThread(Thread):
    """
    Thread that begins a screen recording.

    Attributes
    ----------
    adb : string
        path to adb packages
    replay_path : string
        path to video on device
    device_name : string
        device to execute on
    size : string
        size of recorded video; should be set to match input video

    Methods
    -------
    run()
        Begins screen recording.
    get_replay_path()
        Returns replay path.
    """
    def __init__(self, adb, replay_path, device_name, size='720x1280'):
        """
        Parameters
        ----------
        adb : string
            path to adb package
        replay_path : string
            path to video on device
        device_name : string
            device to execute on
        size : string
            size of the recorded video; should be set to match input video
        """
        super().__init__()
        self.adb = adb
        self.replay_path = replay_path
        self.device_name = device_name
        self.size = size

    def run(self):
        """
        Begins screen recording.
        """
        # specify the video size to ensure screenrecording is possible
        record = [self.adb, '-s', self.device_name, 'shell', 'screenrecord', self.replay_path, '--size', self.size]
        self.record = sp.Popen(record, shell=False)
        self.record.wait()
    
    def get_replay_path(self):
        """
        Returns replay path.

        Returns
        -------
        replay_path : string
            path to replay video
        """
        return self.replay_path

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'asJson'):
            return obj.asJson()
        else:
            return json.JSONEncoder.default(self, obj)


class JSONFileUtils():
    """
    Contains methods to read data from json files.

    Methods
    -------
    read_data_from_json(file_path)
        Reads data from json file.
    output_data_to_json(data, file_path)
        Outputs data to json file using ComplexEncoder.
    """
    @staticmethod
    def read_data_from_json(file_path):
        """
        Reads data from json file.

        Parameters
        ----------
        file_path : string
            path to file to read from
        
        Returns
        -------
        data :  dict
            json information
        """
        file_path = os.path.join(file_path)
        file_json = open(file_path, 'r')
        data = json.load(file_json)
        file_json.close() 
        return data

    @staticmethod
    def output_data_to_json(data, file_path):
        """
        Outputs data to json file using ComplexEncoder.

        Parameters
        ----------
        data : 
            data to output to json
        file_path : string
            path to file to output to
        """
        json_data = json.dumps(data, cls=ComplexEncoder, sort_keys=True)
        file = open(file_path, "w+")
        file.write(json_data)
        file.close()

class Translator():
    """
    Provides methods to perform translation between sendevent commands output
    by the pipeline and the csv-style information that is necessary for RERAN.

    Methods
    -------
    translate()
        Translates between sendevent logs and reran.
    """

    @staticmethod
    def translate(event_path, e=None, t=False):
        """
        Translates sendevents to reran file.

        Parameters
        ----------
        event_path : string
            location of getevent lof
        e : string
            valid event list; if none, do them all;
            passed as #,#,#,# where # is the value of valid events
        t : string
            time warp values;
            passed as MIN,LOW,NEW,MAX
        
        Returns
        -------
        data : list of strings
            csv file data that can be used or output
        """
        data = []
        tp = 0
        code = 0
        value = 0
        prev_time_stamp = 0.0
        same_counter = 0
        all_events_valid = False

        split_event_on = ","

        # if user wants to only define certain event numbers as valid
        if e:
            valid_event_numbers = e.split(split_event_on)
        else:
            all_events_valid = True

        # number of events that will be sent to replay program
        num_lines = 0
        with open(event_path, 'r') as f:
            for line in f:
                if ('event' in line) and ('device' not in line) and ('name' not in line):
                    split_on = ' '
                    tokens = line.split(split_on)
                    input_device_type = tokens[5]
                    # remove colon
                    input_device_type = input_device_type[:-1]
                    event_number = input_device_type.replace('/dev/input/event', '')
                    current_event_is_valid = 1
                    if not all_events_valid:
                        # if valid events are 1,3,5
                        # checks to see if this event is valid
                        for valid in valid_event_numbers:
                            if event_number == valid:
                                current_event_is_valid = 1
                        if current_event_is_valid:
                            num_lines += 1
                    else:
                        num_lines += 1
			# Read the getevent file and build the event file
            # first line of the new file is the number of lines to be processed
            data.append(str(num_lines))
            written = 0		
            is_first_event = True
			
			# For each line in getevent, check to see if the user wants the event type,
			# build the type, code, value, and then write it to output
            with open(event_path, 'r') as f:
                for line in f:
                    # not an event with a timestamp
                    if not '[' in line:
                        continue
                    time_stamp = 0.0
                    interval = 0
                    split_on = ' '
                    seconds = 0
                    microseconds = 0
                    tokens = line.rstrip().split(split_on)
                    time_stamp_string = tokens[4].replace(']', '')
                    if (not time_stamp_string == 'add') and (len(time_stamp_string) != 0) and (not time_stamp_string == "could"):
                        times = time_stamp_string.split('.')
                        time_stamp = float(time_stamp_string)
                        input_device_type = tokens[5]
                        input_device_type = input_device_type[-2]
                        event_number = input_device_type.replace('/dev/input/event', '')
                        
                        current_event_is_valid = False
                        if not all_events_valid:
                            for x in valid_event_numbers:
                                if event_number == x:
                                    current_event_is_valid = True
                        if ((current_event_is_valid and (event_number != '*')) or (all_events_valid and (event_number != '*'))):
                            tp = int(tokens[6], 16)
                            code = int(tokens[7], 16)
                            value = int(tokens[8], 16)
                            
                            if is_first_event:
                                prev_time_stamp = time_stamp
                                
                            long_time_stamp = int(time_stamp * 1000000000)
                            long_prev_time_stamp = int(prev_time_stamp * 1000000000)
                            interval = long_time_stamp - long_prev_time_stamp
                            
                            if interval >= 0:
                                interval_nano = interval
                                
                                # if time-warping arguments passed
                                if t:
                                    # arg passed as MIN,LOW,NEW,MAX
                                    # all in nanosecs
                                    # MIN - minimum value (any interval less will run normally, usually gestures)
                                    # LOW - value detecting data entry
                                    # NEW - new value to replace the slow data entry 
                                    # MAX - maximum value to wait before cutting off
                                    time_warping_values = t.split(',')
                                    min_val = int(1000000000 * float(time_warping_values[0]))
                                    low_val = int(1000000000 * float(time_warping_values[1]))
                                    new_val = int(1000000000 * float(time_warping_values[2]))
                                    max_val = int(1000000000 * float(time_warping_values[3]))
                                    
                                    if not ((min_val < low_val) and (min_val < max_val) and (low_val < max_val)):
                                        raise IOError("ERROR: Bad range of time-warp values, check documentation.")
                                    if (interval_nano > min_val) and (interval_nano < low_val):
                                        interval_nano = new_val
                                    elif interval_nano > max_val:
                                        interval_nano = max_val
                                        
                                        
                                if interval_nano == 0:
                                    same_counter += 1
                                #sleep for time interval
                                data.append(str(interval_nano))
                            else:
                                print("ERROR, time interval between events should not be negative! Please check getevent log for event types that can be ignored.");
                                break
                            data.append(str(event_number)+','+str(tp)+','+str(code)+','+str(value))
                            written += 1
                            prev_time_stamp = time_stamp
                            if is_first_event:
                                is_first_event = False
                        else:
                            # ignore lines that start with * (usually when device is started)
                            # and also ignore the lines that the user chooses to skip, and continue
                            continue
                    else:
                        # ignore these lines as they are the initial output of "add device" and "name" of getevent
                        continue
        return data
