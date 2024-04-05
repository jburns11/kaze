import os.path
import os
import time
import xml.etree.ElementTree as ET

from src.PaparazziHelper import PaparazziHelper
from src.FitnessCalculator import FitnessCalculator
from src.WindDataGenerator import WindDataGenerator
from src.WindDataPlayer import WindDataPlayer
from src import Common as com


class Kaze:
    def __init__(self, kazeConfig):
        self.kazeConfig = kazeConfig
        self.logs_dir = com.PPRZ_SRC + "/var/logs/"
        self.fitness_calculator = FitnessCalculator(
            self.kazeConfig.pprz_base_trace, self.kazeConfig.test_blocks
        )
        self.wind_player = WindDataPlayer(self.kazeConfig.sim_run_time)

    def set_sim_params(self, kazeInput):
        self.kazeInput = kazeInput
        self.sim_num_str = str(kazeInput.sim_num)
        while len(self.sim_num_str) < 3:
            self.sim_num_str = "0" + self.sim_num_str

    def generate_fp(self):
        if len(self.kazeInput.fp_vars) == 0:
            os.system(
                "cp "
                + com.PPRZ_SRC
                + "/conf/flight_plans/"
                + self.kazeConfig.fp_name
                + " "
                + com.PPRZ_SRC
                + "/conf/flight_plans/"
                + self.kazeConfig.fp_name[:-4]
                + self.sim_num_str
                + ".xml"
            )
        else:
            os.system(
                "cp "
                + com.PPRZ_SRC
                + "/conf/flight_plans/"
                + self.kazeConfig.fp_name
                + " "
                + com.PPRZ_SRC
                + "/conf/flight_plans/"
                + self.kazeConfig.fp_name[:-4]
                + self.sim_num_str
                + ".xml"
            )
            input_index = 0
            for var in self.kazeConfig.fp_vars:
                tree = ET.parse(
                    com.PPRZ_SRC
                    + "/conf/flight_plans/"
                    + self.kazeConfig.fp_name[:-4]
                    + self.sim_num_str
                    + ".xml"
                )
                root = tree.getroot()
                for i in root:
                    if i.tag == "variables":
                        for variable in i:
                            if var[0] == variable.attrib["var"]:
                                variable.set(
                                    "init",
                                    str(int(self.kazeInput.fp_vars[input_index])),
                                )
                                variable.attrib.pop("min", None)
                                variable.attrib.pop("max", None)
                                input_index += 1
                tree.write(
                    com.PPRZ_SRC
                    + "/conf/flight_plans/"
                    + self.kazeConfig.fp_name[:-4]
                    + self.sim_num_str
                    + ".xml"
                )

    def generate_conf(self):
        tree = ET.parse(com.PPRZ_SRC + "/conf/conf.xml")
        root = tree.getroot()
        fp = ""
        for i in root:
            if i.attrib["name"] == self.kazeConfig.ac_name:
                i.set(
                    "flight_plan", "flight_plans/udales_sim" + self.sim_num_str + ".xml"
                )
        tree.write(com.PPRZ_SRC + "/conf/conf.xml")
        return

    def parse_buildings(self):
        buildings = [[[0, 0], [0, 0], [0, 0]]]
        i = 0
        var_i = 0
        for building in self.kazeConfig.buildings:
            if not com.is_float(building[0][0]):
                # look up var
                buildings[i][0][0] = float(self.kazeInput.fp_vars[var_i])
                var_i += 1
            else:
                buildings[i][0][0] = float(building[0][0])

            if not com.is_float(building[0][1]):
                # look up var
                buildings[i][0][1] = float(self.kazeInput.fp_vars[var_i])
                var_i += 1
            else:
                buildings[i][0][1] = float(building[0][1])

            if not com.is_float(building[1][0]):
                # look up var
                buildings[i][1][0] = float(self.kazeInput.fp_vars[var_i])
                var_i += 1
            else:
                buildings[i][1][0] = float(building[1][0])

            if not com.is_float(building[1][1]):
                # look up var
                builcom.dings[i][1][1] = float(self.kazeInput.fp_vars[var_i])
                var_i += 1
            else:
                buildings[i][1][1] = float(building[1][1])

            if not com.is_float(building[2][0]):
                # look up var
                buildings[i][2][0] = float(self.kazeInput.fp_vars[var_i])
                var_i += 1
            else:
                buildings[i][2][0] = float(building[2][0])

            if not com.is_float(building[2][1]):
                # look up var
                buildings[i][2][1] = float(self.kazeInput.fp_vars[var_i])
                var_i += 1
            else:
                buildings[i][2][1] = float(building[2][1])
            buildings.append([[0, 0], [0, 0], [0, 0]])
            i += 1
        return buildings[:-1]

    def generate_inputs(self):
        # Create NEW_FP
        self.generate_fp()

        # Edit conf
        self.generate_conf()

        buildings_args = self.parse_buildings()

        # Build current config
        os.system(
            "make -C /home/rti/kaze/paparazzi -f Makefile.ac AIRCRAFT="
            + self.kazeConfig.ac_name
            + " nps.compile"
        )

        self.wind_generator = WindDataGenerator(
            self.kazeInput, self.kazeConfig, self.sim_num_str, buildings_args
        )

        self.wind_generator.generate_wind()

    def calc_fitness(self):
        # Clear logs directory
        os.system("rm -f " + self.logs_dir + "/*")

        # Create wind player
        windfile = ""
        if os.path.exists(
            com.EXEC_PATH
            + "Kaze/var/"
            + self.kazeConfig.batch_name
            + "/"
            + str(self.sim_num_str)
            + "/out/udales/"
            + "fielddump."
            + str(self.sim_num_str)
            + ".nc"
        ):
            windfile = (
                com.EXEC_PATH
                + "Kaze/var/"
                + self.kazeConfig.batch_name
                + "/out/udales/"
                + str(self.sim_num_str)
                + "/"
                + "fielddump."
                + str(self.sim_num_str)
                + ".nc"
            )
        else:
            windfile = (
                com.EXEC_PATH
                + "Kaze/var/"
                + self.kazeConfig.batch_name
                + "/out/udales/"
                + str(self.sim_num_str)
                + "/"
                + "fielddump.000."
                + str(self.sim_num_str)
                + ".nc"
            )

        self.wind_player.set_input_path(windfile)

        # Create pprz simulator
        self.pprz_sim = PaparazziHelper(self.kazeConfig.ac_name)

        # Run simulation
        self.pprz_sim.run_sim()
        # Play wind
        self.wind_player.start()
        time.sleep(self.kazeConfig.sim_run_time)
        self.pprz_sim.kill_sim()
        self.wind_player.kill()

        # self.wind_player = None
        self.pprz_sim = None

        # Parse pprz simulation logs and calc fitness
        dir_list = os.listdir(self.logs_dir)
        new_log = self.logs_dir
        for filename in dir_list:
            if ".data" in filename:
                new_log += filename

        fitness = self.fitness_calculator.calc_pcc_per_block(new_log)

        return fitness

    def clean_pprz(self):
        os.system(
            "mkdir "
            + com.EXEC_PATH
            + "Kaze/var/"
            + self.kazeConfig.batch_name
            + "/"
            + self.sim_num_str
            + "/out/pprz/"
        )

        os.system(
            "cp "
            + self.logs_dir
            + "/* "
            + com.EXEC_PATH
            + "Kaze/var/"
            + self.kazeConfig.batch_name
            + "/"
            + self.sim_num_str
            + "/out/pprz/"
        )

        # Clean Logs
        os.system("rm -f " + self.logs_dir + "/*")
