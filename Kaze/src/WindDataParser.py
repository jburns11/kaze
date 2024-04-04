import netCDF4 as nc


class WindDataParser:
    """Class to parse data generated from uDALES simulation."""

    def __init__(self, inputPath):
        """
        Initialize WindDataParser.

        Parameters:
        - inputPath: Path to the input data.
        """
        self.data = nc.Dataset(inputPath)

    def get_east_west_wind(self, t, x, y, z):
        """
        Get the east-to-west wind speed at position (x,y,z) at time t.

        Parameters:
        - t: Time index.
        - x: x-coordinate.
        - y: y-coordinate.
        - z: z-coordinate.

        Returns:
        - East-to-west wind speed.
        """
        try:
            return self.data["u"][t][z][y][x]
        except:
            return 0

    def get_vertical_wind(self, t, x, y, z):
        """
        Get the south-to-north wind speed at position (x,y,z) at time t.

        Parameters:
        - t: Time index.
        - x: x-coordinate.
        - y: y-coordinate.
        - z: z-coordinate.

        Returns:
        - South-to-north wind speed.
        """
        try:
            return self.data["w"][t][z][y][x]
        except:
            return 0

    def get_south_north_wind(self, t, x, y, z):
        """
        Get the vertical wind speed at position (x,y,z) at time t.

        Parameters:
        - t: Time index.
        - x: x-coordinate.
        - y: y-coordinate.
        - z: z-coordinate.

        Returns:
        - Vertical wind speed.
        """
        try:
            return self.data["v"][t][z][y][x]
        except:
            return 0

    def get_wind_vector(self, t, x, y, z):
        """
        Get the full wind speed vector at position (x,y,z) at time t.

        Parameters:
        - t: Time index.
        - x: x-coordinate.
        - y: y-coordinate.
        - z: z-coordinate.

        Returns:
        - List containing east-to-west, south-to-north, and vertical wind speeds.
        """
        return [
            self.get_east_west_wind(t, x, y, z),
            self.get_south_north_wind(t, x, y, z),
            self.get_vertical_wind(t, x, y, z),
        ]
