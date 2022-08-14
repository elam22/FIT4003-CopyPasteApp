# spatial.py

class Coords():
    """
    Coordinate object.

    Attributes
    ----------
    x : float
        x-coordinate
    y : float
        y-coordinate
    
    Methods
    -------
    get_x()
        Returns x-coordinate.
    get_y()
        Returns y-coordinate.
    """

    def __init__(self, x, y):
        """
        Parameters
        ----------
        x : float
            x-coordinate
        y : float
            y-coordinate
        """
        self.x = x
        self.y = y

    def get_x(self):
        """
        Returns x-coordinate.

        Returns
        -------
        x: float
            x-coordinate
        """
        return self.x

    def get_y(self):
        """
        Returns y-coordinate.

        Returns
        -------
        y : float
            y-coordinate
        """
        return self.y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"
