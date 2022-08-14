# event.py
from enum import Enum

from v2s.util.screen import ScreenTap
from v2s.util.spatial import Coords


class ActionType(Enum):
    CLICK = 0
    LONG_CLICK = 1
    SWIPE = 2

class GUIAction():
    """
    Certain classification of an interaction of a user with a screen.

    Attributes
    ----------
    act_type : ActionType
        type of action (CLICK=0, LONG_CLICK=1, SWIPE=2)
    taps : list of ScreenTaps
        list of ScreenTaps that make up  action
    frames : list of ints
        list of frames that make up action

    Methods
    -------
    get_type()
        Returns type of action as an integer.
    set_type(type)
        Changes action type to specified value.
    get_taps()
        Returns list of ScreenTaps that make up the action.
    set_taps(taps)
        Changes list of ScreenTaps to specified value.
    get_frames()
        Returns list of frame ids that make up the action.
    set_frames(ids)
        Changes list of frame ids to specified value.
    get_centroid()
        Get centroid of the taps that are involved in this action.
    asJson()
        Defines how to output GUIAction to JSON file.
    """
    def __init__(self, taps, frames, act_type=-1):
        """
        Parameters
        ----------
        taps : list of ScreenTaps
            taps that make up the action
        frames : list of ints
            ids of frames that make up action
        type : ActionType, optional
            type of action (CLICK=0, LONG_CLICK=1, SWIPE=2) (default=-1)
        """
        self.frames = frames
        self.type = act_type
        # if only a ScreenTap is passed, convert it to a list of taps
        if isinstance(taps, ScreenTap):
            self.taps = [taps]
        else:
            self.taps = taps
        
    def get_type(self):
        """
        Returns type of action.

        Returns
        -------
        type : enum
            action type
        """
        return self.type

    def set_type(self, type):
        """
        Changes action type to specified value.

        Parameters
        ---------
        type : enum
            action type
        """
        self.type = type
    
    def get_taps(self):
        """
        Returns list of ScreenTaps that make up the action.

        Returns
        -------
        taps : list of ScreenTaps
            taps associated with action
        """
        return self.taps

    def set_taps(self, taps):
        """
        Changes list of ScreenTaps to specified value.

        Parameters
        ----------
        taps : list of ScreenTaps
            new taps for GUIAction
        """
        self.taps = taps

    def get_frames(self):
        """
        Returns list of frame ids that make up the action.

        Returns
        -------
        frames : list of ints
            frame ids associated with GUIAction
        """
        return self.frames

    def set_frames(self, ids):
        """
        Changes list of frame ids to specified value.

        Parameters
        ----------
        ids : list of ints
            new frame ids
        """
        self.frames = ids

    def get_first_frame(self):
        """
        Returns the first frame of the object.

        Returns
        -------
        frame : int
            frame the action starts on
        """
        return self.frames[0]

    def get_centroid(self):
        """
        Returns the centroid of the taps involved with this action.

        Returns
        -------
        centroid : ScreenTap
            centroid of taps associated with GUIAction
        """
        x_sum = 0;
        y_sum = 0;
        for tap in self.taps:
            x_sum += tap.get_x()
            y_sum += tap.get_y()
        return ScreenTap(x_sum / len(self.taps), y_sum / len(self.taps))
    
    def __str__(self):
        """
        Defines string representation of GUIAction.

        Returns
        -------
        string : string
            string rep
        """
        if self.get_type() == ActionType.CLICK:
            str_type = "CLICK"
        elif self.get_type() == ActionType.LONG_CLICK:
            str_type = "LONG_CLICK"
        elif self.get_type() == ActionType.SWIPE:
            str_type = "SWIPE"
        return ("act{" +
                "ty=" + str_type +  
                ", fr=" + str(self.get_frames()) +
                ", tp=" + str([str(tap) for tap in self.taps]) +
                '}')

    def __eq__(self, other):
        if self is other:
            return True
        if other is None or type(self) != type(other):
            return False
        return ((self.get_taps() == other.get_taps()) and 
                (self.get_type() == other.get_type()) and 
                (self.get_frames() == other.get_frames()))
    
    def __hash__(self):
        return hash(taps)

    def asJson(self):
        """
        Defines how to output GUIAction information to JSON file. Outputs
        important information into a dictionary.
        """
        if self.type == ActionType.CLICK:
            tp = "CLICK"
        elif self.type == ActionType.LONG_CLICK:
            tp = "LONG_CLICK"
        elif self.type == ActionType.SWIPE:
            tp = "SWIPE"
        return dict(act_type=tp, taps=self.taps, frames=self.frames)

class Event():
    """
    Event that can be translated to a device.

    Attributes
    ----------
    start_loc : list of Coords
        x,y where event begins spatially
    end_loc : list of Coords
        x,y where event ends spatially
    frames : list of ints
        list of frames that make up action
    pause_duration : float
        length of pause if event is a delay
    action_duration : float
        how long action took
    last_event : float
        duration of previous event
    event_label : string
        what event is (CLICK, LONG CLICK, SWIPE, DELAY, etc)
    is_delay : bool
        if event is a delay
    wait_per_command : float
        amount of time to wait before executing next sendevent command   
    raw_commands : list of strings
        commands that are fed to device for replay

    Methods
    -------
    get_start_loc()
        Returns the start location of the event.
    set_start_loc(loc)
        Changes the start location of the event to the specified value.
    get_end_loc()
        Returns the end location of the event.
    set_end_loc(loc)
        Changes the end location of the event to the specified value.
    get_pause_duration()
        Returns duration of pause.
    set_pause_duration(dur)
        Changes the value of pause_duration to the specified value.
    get_duration()
        Returns duration of event.
    set_duration(dur)
        Changes the value of action_duration to the specified value.
    get_last_event()
        Returns the duration of the previous event.
    set_last_event(dur)
        Changes the value of the duration of the previous event to a specified 
        value.
    get_event_label()
        Returns the type of event.
    set_event_label(label)
        Changes the type of the event to the specified value.
    get_is_delay()
        Returns true if the event is a delay.
    set_is_delay(val)
        Changes the value of is_delay to the new value.
    get_wait_per_command()
        Returns the time waited between commands.
    set_wait_per_command(wait)
        Changes the value of wait_per_command to a new value.
    get_raw_commands()
        Returns the list of raw commands.
    set_raw_commands(commands)
        Changes the list of raw commands to the specified value.
    """

    def __init__(self, label, start=None, end=None, last_event=None, 
                 wait=0, pause_dur=None):
        """
        Parameters
        ----------
        label : string
            type of event (CLICK, LONG CLICK, SWIPE, DELAY, etc)
        start : list of Coords, optional
            start location of event
        end : list of Coords, optional
            end location of event
        last_event : float, optional
            duration of last event
        wait : float, optional
            time waited before executing next command
        pause_dir : floar, optional
            duration of pause if event is a delay
        """
        self.event_label = label.upper()
        self.wait_per_command = 0
        if self.event_label == "DELAY":
            self.pause_duration = pause_dur;
            self.is_delay = True;
            self.raw_commands = []
            self.raw_commands.append("sleep " + str(self.pause_duration))
        else:
            self.start_loc = start
            self.end_loc = end
            self.last_event = last_event
            self.wait_per_command = wait

    def get_start_loc(self):
        """
        Returns the start location of the event.

        Returns
        -------
        start_loc : Coords
            start loc of event
        """
        return self.start_loc

    def set_start_loc(self, loc):
        """
        Changes the start location of the event to the specified value.

        Parameters
        ----------
        loc : Coords
            new start loc
        """
        self.start_loc = loc
    
    def get_end_loc(self):
        """
        Returns the end location of the event.

        Returns
        -------
        end_loc : Coords
            end loc of event
        """
        return self.end_loc

    def set_end_loc(self, loc):
        """
        Changes the end location of the event to the specified value.

        Parameters
        ----------
        loc : Coords
            new end loc
        """
    
    def get_pause_duration(self):
        """
        Returns duration of pause.

        Returns
        -------
        pause_duration : float
            duration of pause
        """
        return self.pause_duration

    def set_pause_duration(self, dur):
        """
        Changes the value of pause_duration to the specified value.

        Parameters
        ----------
        dur : float
            duration of pause
        """
        self.pause_duration = dur

    def get_duration(self):
        """
        Returns duration of event.

        Returns
        -------
        duration : float
            event duration
        """
        return self.action_duration

    def set_duration(self, dur):
        """
        Changes the value of action_duration to the specified value.

        Parameters
        ----------
        dur : float
            duration of action
        """
        self.action_duration = dur
    
    def get_last_event(self):
        """
        Returns the duration of the previous event.

        Returns
        -------
        last_event : float
            duration of prev event
        """
        return self.last_event

    def set_last_event(self, dur):
        """
        Changes the value of the duration of the previous event to a specified 
        value.

        Parameters
        ----------
        last_event : float
            duration of prev event
        """
        self.last_event = dur

    def get_event_label(self):
        """
        Returns the type of event.

        Returns 
        -------
        event label : string
            event type
        """
        return self.event_label

    def set_event_label(self, label):
        """
        Changes the type of the event to the specified value.

        Parameters
        ----------
        label : string
            event label
        """
        self.event_label = label

    def get_is_delay(self):
        """
        Returns true if the event is a delay.

        Returns
        -------
        is_delay : bool
            whether the event is a delay
        """
        return self.is_delay

    def set_is_delay(self, val):
        """
        Changes the value of is_delay to the new value.

        Parameters
        ----------
        is_delay : bool
            new value of is_delay
        """
        self.is_delay = val

    def get_wait_per_command(self):
        """
        Returns the time waited between commands.

        Returns
        -------
        wait_per_command : float
            amount of time to wait between events
        """
        return self.wait_per_command

    def set_wait_per_command(self, wait):
        """
        Changes the value of wait_per_command to a new value.

        Parameters
        ----------
        wait : float
            new wait_per_command value
        """
        self.wait_per_command = wait

    def get_raw_commands(self):
        """
        Returns the list of raw commands.

        Returns
        -------
        raw_commands : list of strings
            raw event commands
        """
        return self.raw_commands

    def set_raw_commands(self, commands):
        """
        Changes the list of raw commands to the specified value.

        Parameters
        ----------
        commands : list of strings
            new raw_commands 
        """
        self.raw_commands = commands

    def __str__(self):
        event = self.event_label + ": "
        if self.event_label == "DELAY":
            event += str(self.pause_duration)
        else:
            event += ("start_loc = " + str([str(loc) for loc in self.start_loc])  + ", end_loc = "
                      + str([str(loc) for loc in self.end_loc]))
        return event
