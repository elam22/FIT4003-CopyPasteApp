# screen.py
from v2s.util.spatial import Coords

class ScreenTap():
    """
    Representation of a detected screen tap within a certain frame.

    Attributes
    ----------
    loc : Coords
        x,y coordinates of tap
    frame : int
        id of frame where tap was detected
    touch_confidence : float
        confidence this is a true tap
    opacity_confidence : float
        probability that this is low opacity; high values mean low opacity, 
        low values mean high opacity
        NOTE : taken from the java code, may need to be changed for readability
    visited : bool
        depiction of visited status for grouping algorithm

    Methods
    -------
    get_x()
        Returns x-coordinate of tap.
    get_y()
        Returns y-coordinate of tap.
    get_frame()
        Returns frame id of tap.
    set_frame(id)
        Changes frame of tap to specified value.
    get_touch_confidence()
        Returns touch_confidence of tap.
    set_touch_confidence(confidence)
        Changes touch_confidence of tap to specified value.
    get_opacity_confidence()
        Returns opacity_confidence of tap.
    set_opacity_confidence(confidence)
        Changes opacity_confidence of tap to specified value.
    is_visited()
        Returns value of visited.
    set_visited(val)
        Changes value of visited to specified value.
    asJson()
        Defines how to output ScreenTap to JSON file.
    """
    def __init__(self, x, y, confidence=None, opacity=None, frame=None):
        """
        Parameters
        ----------
        x : float
            x-coordinate of the tap
        y : float
            y-coordinate of the tap
        confidence : float
            confidence this is a true tap
        opacity : float, optional
            confidence this is not a fading tap (i.e. a real action)
        frame : int, optional
            id of frame where tap was detected
        """
        self.loc = Coords(x, y)
        self.touch_confidence = confidence
        # will be updated correctly once opacity cnn is executed
        self.opacity_confidence = opacity
        self.visited = False
        self.frame = frame

    def get_x(self):
        '''
        Returns x-coordinate of tap.

        Returns
        -------
        x : float
            x-coordinate of tap.
        '''
        return self.loc.get_x()

    def get_y(self):
        '''
        Returns y-coordinate of tap.

        Returns
        -------
        y : float
            y-coordinate of tap
        '''
        return self.loc.get_y()

    def get_frame(self):
        '''
        Returns frame id of tap

        Returns
        -------
        frame : int
            frame id
        '''
        return self.frame

    def set_frame(self, id):
        '''
        Changes frame id to specified value.

        Parameters
        ----------
        id : int
            new frame id
        '''
        self.frame = id

    def get_touch_confidence(self):
        '''
        Returns touch_coordinate of tap.

        Returns
        -------
        touch_confidence : float
            confidence this is a true tap
        '''
        return self.touch_confidence

    def set_touch_confidence(self, confidence):
        '''
        Changes touch confidence to specified value.

        Parameters
        ----------
        confidence : float
            new touch confidence
        '''
        self.touch_confidence = confidence

    def get_opacity_confidence(self):
        '''
        Returns opacity_confidence.

        Returns
        -------
        opacity_confidence : float
            confidence that this is not a fading tap
        '''
        return self.opacity_confidence

    def set_opacity_confidence(self, confidence):
        '''
        Changes opacity confidence to specified value.

        Parameters
        ----------
        confidence : float
            new opacity confidence
        '''
        self.opacity_confidence = confidence

    def is_visited(self):
        '''
        Returns value of visited.

        Returns
        -------
        visited : bool
            depiction of visited status for grouping algorithm
        '''
        return self.visited

    def set_visited(self, val):
        '''
        Changes visited to specified value.

        Parameters
        ----------
        val : bool
            new visited status
        '''
        self.visited = val

    def __str__(self):
        """
        Defines the string representation of a ScreenTap.

        Returns
        -------
        string : string
            string rep
        """
        return ("tap{" + "x=" + str(self.get_x()) + 
                ", y=" + str(self.get_y()) + 
                "}")

    def __eq__(self, other):
        """
        Two screen taps are considered equal if they have the same x and y 
        coordinates.
        """
        if self is other:
            return True
        if other is None or type(self) != type(other):
            return False;
        return other.get_x() == self.loc.get_x() and other.get_y() == self.loc.get_y()

    def __hash__(self):
        return hash(self.x)
    
    def asJson(self):
        """
        Defines how to output ScreenTap information to JSON file. Outputs
        important information into a dictionary.
        """
        return dict(x=self.loc.get_x(), y=self.loc.get_y(), confidence=self.touch_confidence,\
                    confidenceOpacity=self.opacity_confidence, frame=self.frame)

class Frame():
    """
    Video frame container. Allows for the grouping of ScreenTaps detected based
    on frame groupings.

    Attributes
    ----------
    id : int
        frame id
    screen_taps : list of ScreenTaps
        list of ScreenTaps detected in the corresponding frame

    Methods
    -------
    get_id()
        Returns the id of the frame.
    set_id(id)
        Changes frame id to specified value.
    get_screen_taps()
        Returns list of ScreenTaps.
    set_screen_taps(taps)
        Changes screen tap list to specified value.
    add_tap(tap)
        Appends a new ScreenTap to the list of screen taps corresponding to this
        frame.
    asJson()
        Defines how to output Frame to JSON file.
    """
    def __init__(self, id):
        """
        Parameters
        ----------
        id : int
            frame id
        """
        self.id = id
        self.screen_taps = []

    def get_id(self):
        """
        Returns the id of the frame.

        Returns
        -------
        id : int
            frame id
        """
        return self.id
        
    def set_id(self, id):
        """
        Changes frame id to specified value.

        Parameters
        ----------
        id : int
            frame id
        """
        self.id = id
        
    def get_screen_taps(self):
        """
        Returns list of ScreenTaps.

        Returns
        -------
        screen_taps : list of ScreenTaps
            taps associated with this frame
        """
        return self.screen_taps

    def set_screen_taps(self, taps):
        """
        Changes screen tap list to specified value.  

        Parameters
        ----------
        taps : list of ScreenTaps
            new list of ScreenTaps 
        """
        self.screen_taps = taps

    def add_tap(self, tap):
        """
        Adds a new ScreenTap to end of the current list of taps in this Frame.

        Parameters
        ----------
        tap : ScreenTap
            tap to add to the list
        """
        self.screen_taps.append(tap)

    def __str__(self):
        """
        Defines the string representation of a Frame.
        
        Returns
        -------
        string : string
            string rep
        """
        return ("frame{" + "id=" + str(self.id) +
               ", taps=" + str([str(tap) for tap in self.screen_taps]) + "}")

    def asJson(self):
        """
        Defines how to output Frame information to JSON file. Outputs
        important information into a dictionary.
        """
        return dict(screenId=self.id, screenTap=self.screen_taps)
