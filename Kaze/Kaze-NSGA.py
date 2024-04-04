import numpy as np
from Kaze import Kaze
import xml.etree.ElementTree as ET
import argparse
import os.path
import csv
import math

from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.algorithms.moo.nsga2 import NSGA2

PPRZ_SRC = os.getenv(
    "PAPARAZZI_SRC",
    os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../")
    ),
)
EXEC_PATH = os.getenv(
    "EXEC_PATH",
    os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./")),
)
VAR_PATH = EXEC_PATH + "Kaze/var/"

# Currently hardcoded values
AC_ID = 31
NUM_CPUS = 5
SIM_RUN_TIME = 60
DEFAULT_PPRZ_SIM_SPACE = [[-50, 50], [-50, 50], [0, 100]]
UDALES_PATH = EXEC_PATH + "/u-dales/"
BASE_SIM_TRACE = "/home/rti/kaze/Kaze/input/base_trace/23_02_01__20_35_40.data"


parser = argparse.ArgumentParser()
parser.add_argument("ac", help="Aircraft Name", type=str)
args = parser.parse_args()


class AtmosphereRange:
    def __init__(
        self,
        humid_min,
        humid_max,
        press_min,
        press_max,
        temp_min,
        temp_max,
        rough_min,
        rough_max,
        xwind_min,
        xwind_max,
        ywind_min,
        ywind_max,
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
        ac_id,
        sim_run_time,
        batch_name,
        test_blocks,
        num_cpu,
        udales_path,
        base_sim_trace,
        fp_name,
    ):
        self.sim_space = sim_space
        self.atmosphere = atmosphere
        self.buildings = buildings
        self.fp_vars = fp_vars
        self.ac_name = ac_name
        self.ac_id = ac_id
        self.sim_run_time = sim_run_time
        self.batch_name = batch_name
        self.test_blocks = test_blocks
        self.num_cpu = num_cpu
        self.udales_path = udales_path
        self.base_sim_trace = base_sim_trace
        self.fp_name = fp_name


class KazeInput:
    def __init__(self, atmosphere, fp_vars, sim_num):
        self.atmosphere = atmosphere
        self.fp_vars = fp_vars
        self.sim_num = sim_num


# Find flight plan
tree = ET.parse(PPRZ_SRC + "/conf/conf.xml")
root = tree.getroot()
fp = ""
for i in root:
    if i.attrib["name"] == args.ac:
        fp = i.attrib["flight_plan"]

# Parse blocks to track
tree = ET.parse(PPRZ_SRC + "/conf/" + fp)
root = tree.getroot()
test_blocks = []
block_id = 0
for i in root:
    if i.tag == "blocks":
        for block in i:
            if "objective" in block.attrib:
                if block.attrib["objective"] == "Positive":
                    test_blocks.append([block.attrib["name"], block_id, "p"])
                elif block.attrib["objective"] == "Negative":
                    test_blocks.append([block.attrib["name"], block_id, "n"])
            block_id += 1

print("Objective Space")
for i in test_blocks:
    print("\tName: " + i[0])
    print("\tID: " + str(i[1]))
    print("\tType: " + i[2])

fp_vars = []
for i in root:
    if i.tag == "variables":
        for variable in i:
            if "min" in variable.attrib and "max" in variable.attrib:
                fp_vars.append(
                    [
                        variable.attrib["var"],
                        [float(variable.attrib["min"]), float(variable.attrib["max"])],
                    ]
                )
print("\nFP VARS:")
print(fp_vars)


# Parse atmosphere
humid_min = 0
humid_max = 0
press_min = 0
press_max = 0
temp_min = 0
temp_max = 0
rough_min = 0
rough_max = 0
xwind_min = 0
xwind_max = 0
ywind_min = 0
ywind_max = 0
for i in root:
    if i.tag == "atmosphere":
        for att in i:
            if att.tag == "humidity":
                humid_min = float(att.attrib["min"])
                humid_max = float(att.attrib["max"])
            elif att.tag == "pressure":
                press_min = float(att.attrib["min"])
                press_max = float(att.attrib["max"])
            elif att.tag == "temperature":
                temp_min = float(att.attrib["min"])
                temp_max = float(att.attrib["max"])
            elif att.tag == "roughness":
                rough_min = float(att.attrib["min"])
                rough_max = float(att.attrib["max"])
            elif att.tag == "xwind":
                xwind_min = float(att.attrib["min"])
                xwind_max = float(att.attrib["max"])
            elif att.tag == "ywind":
                ywind_min = float(att.attrib["min"])
                ywind_max = float(att.attrib["max"])


pprz_sim_space = DEFAULT_PPRZ_SIM_SPACE
for i in root:
    if i.tag == "sectors":
        for att in i:
            if att.tag == "sector" and att.attrib["name"] == "SIM_SPACE":
                for j in root:
                    if j.tag == "waypoints":
                        for wp in j:
                            if wp.attrib["name"] == att[0].attrib["name"]:
                                pprz_sim_space[0][0] = float(wp.attrib["x"])
                                pprz_sim_space[1][0] = float(wp.attrib["y"])
                                pprz_sim_space[2][0] = float(wp.attrib["height"])
                            elif wp.attrib["name"] == att[1].attrib["name"]:
                                pprz_sim_space[0][1] = float(wp.attrib["x"])
                                pprz_sim_space[1][1] = float(wp.attrib["y"])
                                pprz_sim_space[2][1] = float(wp.attrib["height"])

print("SIM SPACE:")
print("\tX: " + str(pprz_sim_space[0]))
print("\tY: " + str(pprz_sim_space[0]))
print("\tZ: " + str(pprz_sim_space[0]))


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


buildings = [[[0, 0], [0, 0], [0, 0]]]
building_index = 0
for i in root:
    if i.tag == "sectors":
        for att in i:
            if att.tag == "building":
                for j in root:
                    if j.tag == "waypoints":
                        for wp in j:
                            if wp.attrib["name"] == att[0].attrib["name"]:
                                buildings[building_index][0][0] = float(wp.attrib["x"])
                                buildings[building_index][1][0] = float(wp.attrib["y"])
                                buildings[building_index][2][0] = float(
                                    wp.attrib["height"]
                                )
                            elif wp.attrib["name"] == att[1].attrib["name"]:
                                buildings[building_index][0][1] = float(wp.attrib["x"])
                                buildings[building_index][1][1] = float(wp.attrib["y"])
                                if is_float(wp.attrib["height"]):
                                    buildings[building_index][2][1] = float(
                                        wp.attrib["height"]
                                    )
                                else:
                                    buildings[building_index][2][1] = wp.attrib[
                                        "height"
                                    ]
                                buildings.append([[0, 0], [0, 0], [0, 0]])
                                building_index += 1


print("\nBUILDINGS:")
for building in buildings[:-1]:
    print("\t" + str(building))

atmosphereRange = AtmosphereRange(
    humid_min,
    humid_max,
    press_min,
    press_max,
    temp_min,
    temp_max,
    rough_min,
    rough_max,
    xwind_min,
    xwind_max,
    ywind_min,
    ywind_max,
)

print("\nATMOSPHERE RANGE:")
print(
    "\tHUMIDITY: ["
    + str(atmosphereRange.humid_min)
    + ","
    + str(atmosphereRange.humid_max)
    + "]"
)
print(
    "\tPRESSURE: ["
    + str(atmosphereRange.press_min)
    + ","
    + str(atmosphereRange.press_max)
    + "]"
)
print(
    "\tTEMPERATURE: ["
    + str(atmosphereRange.temp_min)
    + ","
    + str(atmosphereRange.temp_max)
    + "]"
)
print(
    "\tROUGHNESS: ["
    + str(atmosphereRange.rough_min)
    + ","
    + str(atmosphereRange.rough_max)
    + "]"
)
print(
    "\tX WIND: ["
    + str(atmosphereRange.xwind_min)
    + ","
    + str(atmosphereRange.xwind_max)
    + "]"
)
print(
    "\tY WIND: ["
    + str(atmosphereRange.ywind_min)
    + ","
    + str(atmosphereRange.ywind_max)
    + "]"
)

kazeConfig = KazeConfig(
    pprz_sim_space,
    atmosphereRange,
    buildings,
    fp_vars,
    args.ac,
    AC_ID,
    SIM_RUN_TIME,
    "batch_1",
    test_blocks,
    NUM_CPUS,
    UDALES_PATH,
    BASE_SIM_TRACE,
    fp[13:],
)

# Make dir to save outputs
if not os.path.exists(VAR_PATH):
    os.system("mkdir " + VAR_PATH)
batch_path = VAR_PATH + "/batch_1"
if os.path.exists(batch_path):
    os.system("rm -r " + batch_path)

os.system("mkdir " + batch_path)

kaze = Kaze(kazeConfig)


class KazeProblemEW(ElementwiseProblem):
    def __init__(self, test_blocks, atmosphereRange, fp_vars):
        self.atmosphereRange = atmosphereRange
        self.fp_vars = fp_vars
        self.start_sim_num = 1
        self.num_objs = len(test_blocks)
        var_mins = [
            self.atmosphereRange.humid_min,
            self.atmosphereRange.press_min,
            self.atmosphereRange.temp_min,
            self.atmosphereRange.rough_min,
            self.atmosphereRange.xwind_min,
            self.atmosphereRange.ywind_min,
        ]
        for i in fp_vars:
            var_mins.append(i[1][0])

        var_maxs = [
            self.atmosphereRange.humid_max,
            self.atmosphereRange.press_max,
            self.atmosphereRange.temp_max,
            self.atmosphereRange.rough_max,
            self.atmosphereRange.xwind_max,
            self.atmosphereRange.ywind_max,
        ]
        for i in fp_vars:
            var_maxs.append(i[1][1])
        super().__init__(
            n_var=len(var_maxs),
            n_obj=self.num_objs,
            n_ieq_constr=1,
            xl=np.array(var_mins),
            xu=np.array(var_maxs),
        )

        # Make dir to save outputs
        if not os.path.exists("var"):
            os.system("mkdir " + VAR_PATH)
        batch_path = EXEC_PATH + "Kaze/var/batch_1"
        if os.path.exists(batch_path):
            os.system("rm -r " + batch_path)

        os.system("mkdir " + batch_path)

    def _evaluate(self, x, out, *args, **kwargs):
        atmosphere = Atmosphere(x[0], x[1], x[2], x[3], x[4], x[5])
        kazeInput = KazeInput(atmosphere, x[6:], self.start_sim_num)
        kaze.set_sim_params(kazeInput)
        kaze.generate_inputs()
        fitness = kaze.calc_fitness()
        kaze.clean_pprz()
        out["F"] = []
        for i in range(self.num_objs):
            out["F"].append(np.array(fitness[i]))
        out["F"] = np.array(out["F"])

        # Total wind vector must be < KAZE_INIT_WINDSPEED_H_MAX
        out["G"] = (math.sqrt(x[3] ** 2 + x[4] ** 2)) - self.atmosphereRange.xwind_max

        self.start_sim_num += 1
        print("Done Sim #" + str(self.start_sim_num))
        print("Pop: " + str(x))
        print("Fit: " + str(out["F"]))


problem = KazeProblemEW(test_blocks, atmosphereRange, fp_vars)

termination = get_termination("n_gen", 10)

algorithm = NSGA2(pop_size=10, copy_algorithm=True)

res = minimize(problem, algorithm, termination, seed=1, save_history=True, verbose=True)

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
