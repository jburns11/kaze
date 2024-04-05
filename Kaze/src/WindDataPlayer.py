import sys
import os
import time
from src.WindDataParser import WindDataParser

PPRZ_HOME = os.getenv(
    "PAPARAZZI_HOME",
    os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../")
    ),
)
sys.path.append(PPRZ_HOME + "/sw/ext/pprzlink/lib/v1.0/python")
from ivy.std_api import IvyMainLoop
import ivy.ivy as ivy
from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage

PPRZ_SIM_OFFSET_X = 50  # Relative starting position to 0,0 of udales sim
PPRZ_SIM_OFFSET_Y = 10  # Relative starting position to 0,0 of udales sim


class WindDataPlayer:
    """Class to read generated wind data and send WORLD_ENV messages on the ivy bus.
    This wind sent is the wind in at the uavs current position."""

    def __init__(self, sim_run_time):
        """
        Initialize WindDataPlayer.

        Parameters:
        - sim_run_time: Simulation run time.
        """
        self.sim_run_time = sim_run_time
        self.msg = PprzMessage("ground", "WORLD_ENV")
        self.msg["time_scale"] = 1.0
        self.msg["gps_availability"] = 1  # the value is preset
        self.msg["ir_contrast"] = 400  # the value is user defined
        self.ivy = IvyMessagesInterface(start_ivy=False)

    def set_input_path(self, inputPath):
        """
        Set input path for wind data parser.

        Parameters:
        - inputPath: Path to the wind data.
        """
        self.wind_parser = WindDataParser(inputPath)

    def worldenv_cb(self, _, msg):
        """
        Callback function for world environment.

        Parameters:
        - msg: Message.
        """
        # Must rotate coordinates
        y = int(float(msg["east"])) + PPRZ_SIM_OFFSET_Y
        x = int(float(msg["north"])) + PPRZ_SIM_OFFSET_X
        z = -1 * int(float(msg["up"]))

        wind_east = self.wind_parser.get_east_west_wind(self.time, x, y, z)
        wind_north = self.wind_parser.get_south_north_wind(self.time, x, y, z)
        wind_up = self.wind_parser.get_vertical_wind(self.time, x, y, z)
        self.msg["wind_east"] = wind_east
        self.msg["wind_north"] = wind_north
        self.msg["wind_up"] = wind_up
        self.ivy.send(self.msg, None)

    def start(self):
        """Start wind data simulation."""
        self.time = 1
        self.ivy.subscribe(self.worldenv_cb, "(.* WORLD_ENV_REQ .*)")
        self.ivy.start()

    def kill(self):
        """Shutdown wind data simulation."""
        self.ivy.shutdown()
