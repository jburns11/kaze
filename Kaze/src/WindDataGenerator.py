import subprocess
import os

from src import Common as com


class WindDataGenerator:
    """Class to generate wind data using U-Dales."""

    def __init__(self, kaze_input, kaze_config, sim_num, building_vars):
        """
        Initialize WindDataGenerator.

        Parameters:
        - kaze_input: Input configuration for wind data generation.
        - kaze_config: Configuration for wind data generation.
        - sim_num: Simulation number.
        - building_vars: Variables related to buildings.
        """
        self.kaze_input = kaze_input
        self.kaze_config = kaze_config
        self.sim_num = sim_num
        self.building_vars = building_vars
        self.batch_path = com.VAR_PATH + self.kaze_config.batch_name + "/"
        self.batch_in_path = com.VAR_PATH + self.kaze_config.batch_name + "/in/"
        self.batch_out_path = com.VAR_PATH + self.kaze_config.batch_name + "/out/"
        self.udales_input_path = self.batch_in_path + "udales/"
        self.udales_output_path = self.batch_out_path + "udales/"
        self.sim_input_path = self.batch_in_path + "udales/" + sim_num + "/"
        self.sim_output_path = self.batch_out_path + "udales/"
        self.dirs_to_make = [
            self.batch_path,
            self.batch_in_path,
            self.batch_out_path,
            self.udales_input_path,
            self.udales_output_path,
            self.sim_input_path,
            self.sim_output_path,
        ]

    def replace_params(self):
        """Replace parameters in input files."""
        # Create Wind File from base input
        namoptions_mut = open(
            com.EXEC_PATH + "Kaze/input/udales_input_template/namoptions.001", "r"
        ).read()

        # Replace experiemnt number
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_EXPERIMENT_NUMBER}", self.sim_num
        )
        # Replace surface pressure
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SURFACE_PRESSURE}", str(self.kaze_input.atmosphere.pressure)
        )
        # Replace surface roughness
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SURFACE_ROUGHNESS}", str(self.kaze_input.atmosphere.roughness)
        )
        # Replace surface temperature
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SURFACE_TEMP}", str(self.kaze_input.atmosphere.temperature)
        )
        # Replace initial windspeed(x)
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_INITIAL_WIND_SPEED_H}", str(self.kaze_input.atmosphere.xwind)
        )
        # Replace initial windspeed(y)
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_INITIAL_WIND_SPEED_V}", str(self.kaze_input.atmosphere.ywind)
        )
        # Replace surface humidity
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SURFACE_HUMIDITY}", str(self.kaze_input.atmosphere.humidity)
        )
        # Replace simulation time
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SIM_TIME}", str(self.kaze_config.sim_run_time + 1)
        )
        # Replace sim size in x dimension
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SIM_SIZE_X}",
            str(
                int(
                    abs(
                        self.kaze_config.pprz_sim_space[0][0]
                        - self.kaze_config.pprz_sim_space[0][1]
                    )
                )
            ),
        )
        # Replace sim size in y dimension
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SIM_SIZE_Y}",
            str(
                int(
                    abs(
                        self.kaze_config.pprz_sim_space[1][0]
                        - self.kaze_config.pprz_sim_space[1][1]
                    )
                )
            ),
        )
        # Replace sim size in z dimension
        namoptions_mut = namoptions_mut.replace(
            "{KAZE_SIM_SIZE_Z}",
            str(
                int(
                    abs(
                        self.kaze_config.pprz_sim_space[2][0]
                        - self.kaze_config.pprz_sim_space[2][1]
                    )
                )
            ),
        )

        # Write new file to namoptions for current simulation number
        f = open(
            self.sim_input_path + "/namoptions." + self.sim_num,
            "w",
        )
        f.write(namoptions_mut)
        f.close()

        # Create xgrid file depending on x size
        xgrid_mut = open(
            com.EXEC_PATH + "Kaze/input/udales_input_template/xgrid.inp.001", "r"
        ).read()
        for i in range(
            0,
            int(
                abs(
                    self.kaze_config.pprz_sim_space[0][0]
                    - self.kaze_config.pprz_sim_space[0][1]
                )
            ),
        ):
            xgrid_mut += str(i + 0.5) + "\n"
        # Write xgrid file
        f = open(
            self.sim_input_path + "/xgrid.inp." + self.sim_num,
            "w",
        )
        f.write(xgrid_mut)
        f.close()

        # Create ygrid file depending on y size
        ygrid_mut = open(
            com.EXEC_PATH + "Kaze/input/udales_input_template/ygrid.inp.001", "r"
        ).read()
        for i in range(
            0,
            int(
                abs(
                    self.kaze_config.pprz_sim_space[1][0]
                    - self.kaze_config.pprz_sim_space[1][1]
                )
            ),
        ):
            ygrid_mut += str(i + 0.5) + "\n"
        # Write ygrid file
        f = open(
            self.sim_input_path + "/ygrid.inp." + self.sim_num,
            "w",
        )
        f.write(ygrid_mut)
        f.close()

        # Create zgrid file depending on z size
        zgrid_mut = open(
            com.EXEC_PATH + "Kaze/input/udales_input_template/zgrid.inp.001", "r"
        ).read()
        for i in range(
            0,
            int(
                abs(
                    self.kaze_config.pprz_sim_space[2][0]
                    - self.kaze_config.pprz_sim_space[2][1]
                )
            ),
        ):
            zgrid_mut += str(i + 0.5) + "\n"
        # Write zgrid file
        f = open(
            self.sim_input_path + "/zgrid.inp." + self.sim_num,
            "w",
        )
        f.write(zgrid_mut)
        f.close()

        # Create building file from template
        buildings_mut = open(
            com.EXEC_PATH + "Kaze/input/udales_input_template/buildings.001", "r"
        ).read()
        for building in self.building_vars:
            # Set x,y,z max for each building
            x_min = building[0][0] - self.kaze_config.pprz_sim_space[0][0]
            x_max = building[0][1] - self.kaze_config.pprz_sim_space[0][0]
            y_min = building[1][0] - self.kaze_config.pprz_sim_space[1][0]
            y_max = building[1][1] - self.kaze_config.pprz_sim_space[1][0]
            z_min = building[2][0] - self.kaze_config.pprz_sim_space[2][0]
            z_max = building[2][1] - self.kaze_config.pprz_sim_space[2][0]
            # Create building string, and append to file buffer
            buildings_mut += (
                str(x_min)
                + "\t"
                + str(x_max)
                + "\t"
                + str(y_min)
                + "\t"
                + str(y_max)
                + "\t"
                + str(z_min)
                + "\t"
                + str(z_max)
                + "\n"
            )
        # Write new buildings file for current sim number
        f = open(
            self.sim_input_path + "buildings." + self.sim_num,
            "w",
        )
        f.write(buildings_mut)
        f.close()

    def run_udales(self):
        """Builds udales run command from input params"""

        # Create udales wind generation command
        # Define Tools Directory
        command = "export DA_TOOLSDIR=" + com.UDALES_PATH + "/tools"
        # Define Number of CPUs
        command += "; export NCPU=" + str(self.kaze_config.num_cpus)
        # Define uDales build directory
        command += "; export DA_BUILD=" + com.UDALES_PATH + "/build/release/u-dales"
        # Define uDales build directory
        command += "; export DA_WORKDIR=" + self.sim_output_path
        # Define uDales build directory
        command += (
            "; " + com.UDALES_PATH + "/tools/local_execute.sh " + self.sim_input_path
        )
        # os.system(command + " 1,2>/dev/null")
        # print(command)
        os.system(command)

        return True

    def generate_wind(self):
        """Generates wind file for a single simulation depending on input provided in constructor"""
        # Create necessary input/output directories
        for dir in self.dirs_to_make:
            ret = subprocess.run("mkdir " + dir, capture_output=True, shell=True)

        # Copy udales input templates
        dir_list = os.listdir(com.EXEC_PATH + "Kaze/input/udales_input_template/")
        for f in dir_list:
            ret = subprocess.run(
                "cp "
                + com.EXEC_PATH
                + "Kaze/input/udales_input_template/"
                + "/"
                + f
                + " "
                + self.sim_input_path
                + f[:-3]
                + self.sim_num,
                capture_output=True,
                shell=True,
            )

        # Replace params in teplate file with input params
        self.replace_params()

        # return result of running udales
        return self.run_udales()
