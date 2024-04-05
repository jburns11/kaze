import subprocess

from src import Common as com


class PaparazziHelper:
    """Class to run paparazzi simulations."""

    def __init__(self, ac_name="ardrone2"):
        """
        Initialize PaparazziHelper.

        Parameters:
        - ac_name: Name of the aircraft.
        """
        self.ac_name = ac_name
        self.sim_thread = None
        self.sim_procs = []

    def run_sim(self):
        """Run paparazzi simulation."""
        silence_output = " > /dev/null"
        server_cmd = (
            com.PPRZ_HOME
            + "/sw/ground_segment/tmtc/server  -no_md5_check 1> /dev/null 2> /dev/null"
        )
        link_cmd = (
            com.PPRZ_HOME
            + "/sw/ground_segment/tmtc/link -udp -udp_broadcast 1> /dev/null 2> /dev/null"
        )
        sim_cmd = (
            com.PPRZ_HOME
            + "/sw/simulator/pprzsim-launch -a "
            + self.ac_name
            + " -t nps 1> /dev/null 2> /dev/null"
        )

        self.sim_procs.append(
            subprocess.Popen(server_cmd.split(" "), start_new_session=True)
        )
        self.sim_procs.append(
            subprocess.Popen(link_cmd.split(" "), start_new_session=True)
        )
        self.sim_procs.append(
            subprocess.Popen(sim_cmd.split(" "), start_new_session=True)
        )

    def kill_sim(self):
        """Terminate running paparazzi simulation."""
        for proc in self.sim_procs:
            proc.terminate()
