import os
import numpy as np
import xml.etree.ElementTree as ET

BATCH_NAME = "batch_1"

PPRZ_SRC = os.getenv(
    "PAPARAZZI_SRC",
    os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../")
    ),
)

PPRZ_HOME = PPRZ_SRC

EXEC_PATH = os.getenv(
    "EXEC_PATH",
    os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")),
)

VAR_PATH = EXEC_PATH + "Kaze/var/"

# Currently hardcoded values
AC_ID = 31
NUM_CPUS = 5
SIM_RUN_TIME = 5
DEFAULT_PPRZ_SIM_SPACE = [[-50, 50], [-50, 50], [0, 100]]
UDALES_PATH = EXEC_PATH + "/u-dales/"
BASE_SIM_TRACE = "/home/rti/kaze/Kaze/input/base_trace/23_02_01__20_35_40.data"


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class AtmosphereRange:
    def __init__(
        self,
        humid_min=0,
        humid_max=0,
        press_min=0,
        press_max=0,
        temp_min=0,
        temp_max=0,
        rough_min=0,
        rough_max=0,
        xwind_min=0,
        xwind_max=0,
        ywind_min=0,
        ywind_max=0,
    ):
        self.humid_min = humid_min
        self.humid_max = humid_max
        self.press_min = press_min
        self.press_max = press_max
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.rough_min = rough_min
        self.rough_max = rough_max
        self.xwind_min = xwind_min
        self.xwind_max = xwind_max
        self.ywind_min = ywind_min
        self.ywind_max = ywind_max


class Atmosphere:
    def __init__(self, humidity, pressure, temperature, roughness, xwind, ywind):
        self.humidity = humidity
        self.pressure = pressure
        self.temperature = temperature
        self.roughness = roughness
        self.xwind = xwind
        self.ywind = ywind


class KazeConfig:
    def __init__(
        self,
        sim_space,
        atmosphere,
        buildings,
        fp_vars,
        ac_name,
        sim_run_time,
        batch_name,
        test_blocks,
        num_cpu,
        base_sim_trace,
        fp_name,
    ):
        self.sim_space = sim_space
        self.atmosphere = atmosphere
        self.buildings = buildings
        self.fp_vars = fp_vars
        self.ac_name = ac_name
        self.sim_run_time = sim_run_time
        self.batch_name = batch_name
        self.test_blocks = test_blocks
        self.num_cpu = num_cpu
        self.base_sim_trace = base_sim_trace
        self.fp_name = fp_name


class KazeInput:
    def __init__(self, atmosphere, fp_vars, sim_num):
        self.atmosphere = atmosphere
        self.fp_vars = fp_vars
        self.sim_num = sim_num


def print_results(res, problem):
    np.set_printoptions(threshold=np.inf)
    print("==========Population==========")
    print("[", end="")
    for i in range(len(res.history)):
        print("[", end="")
        for j in range(res.history[i].pop.shape[0]):
            print(list(res.history[i].pop[j].get("X")), end="")
            if j != res.history[i].pop.shape[0] - 1:
                print(",", end="")
        print("]", end="")
        if i != len(res.history) - 1:
            print(",", end="")
    print("]", end="\n\n\n")

    print("==========Fitness==========")
    print("[", end="")
    for i in range(len(res.history)):
        print("[", end="")
        for j in range(res.history[i].pop.shape[0]):
            print(list(res.history[i].pop[j].get("F")), end="")
            if j != res.history[i].pop.shape[0] - 1:
                print(",", end="")
        print("]", end="")
        if i != len(res.history) - 1:
            print(",", end="")
    print("]", end="\n\n\n")

    print("==========Optimal Pop==========")
    print("[", end="")
    for i in range(len(res.history)):
        print("[", end="")
        for j in range(len(res.history[i].opt)):
            print(list(res.history[i].opt[j].get("X")), end="")
            if j != len(res.history[i].opt) - 1:
                print(",", end="")
        print("]", end="")
        if i != len(res.history) - 1:
            print(",", end="")
    print("]", end="\n\n\n")

    print("==========Optimal Fit==========")
    print("[", end="")
    for i in range(len(res.history)):
        print("[", end="")
        for j in range(len(res.history[i].opt)):
            print(list(res.history[i].opt[j].get("F")), end="")
            if j != len(res.history[i].opt) - 1:
                print(",", end="")
        print("]", end="")
        if i != len(res.history) - 1:
            print(",", end="")
    print("]", end="\n\n\n")

    print(res.algorithm.__dir__())
    print(problem.pareto_front())


def get_flight_plan(ac_name):
    # Find flight plan
    tree = ET.parse(PPRZ_SRC + "/conf/conf.xml")
    root = tree.getroot()
    fp = ""
    for i in root:
        if i.attrib["name"] == ac_name:
            return (
                i.attrib["flight_plan"][13:],
                PPRZ_SRC + "/conf/" + i.attrib["flight_plan"],
            )
    return "", ""
