import xml.etree.ElementTree as ET

from src import Common as com


class KazeParser:
    def __init__(self, ac_name):
        self.ac_name = ac_name
        self.test_blocks = []
        self.fp_vars = []
        self.buildings = [[[0, 0], [0, 0], [0, 0]]]
        self.building_index = 0
        self.num_cpus = ""
        self.start_sim_num = ""
        self.nsga2_pop = ""
        self.nsga2_num_gen = ""
        self.sim_run_time = ""
        self.batch_name = ""
        self.pprz_base_trace = ""
        self.atmosphereRange = com.AtmosphereRange()
        self.pprz_sim_space = com.DEFAULT_PPRZ_SIM_SPACE
        self.fp_name = ""
        self.fp_path = ""
        self.tree = None
        self.root = None

    def parse_test_blocks(self):
        block_id = 0
        for i in self.root:
            if i.tag == "blocks":
                for block in i:
                    if "objective" in block.attrib:
                        if block.attrib["objective"] == "Positive":
                            self.test_blocks.append(
                                [block.attrib["name"], block_id, "p"]
                            )
                        elif block.attrib["objective"] == "Negative":
                            self.test_blocks.append(
                                [block.attrib["name"], block_id, "n"]
                            )
                    block_id += 1

    def parse_fp_vars(self):
        for i in self.root:
            if i.tag == "variables":
                for variable in i:
                    if "min" in variable.attrib and "max" in variable.attrib:
                        self.fp_vars.append(
                            [
                                variable.attrib["var"],
                                [
                                    float(variable.attrib["min"]),
                                    float(variable.attrib["max"]),
                                ],
                            ]
                        )

    def parse_atmospheric_range(self):
        for i in self.root:
            if i.tag == "atmosphere":
                for att in i:
                    if att.tag == "humidity":
                        self.atmosphereRange.humid_min = float(att.attrib["min"])
                        self.atmosphereRange.humid_max = float(att.attrib["max"])
                    elif att.tag == "pressure":
                        self.atmosphereRange.press_min = float(att.attrib["min"])
                        self.atmosphereRange.press_max = float(att.attrib["max"])
                    elif att.tag == "temperature":
                        self.atmosphereRange.temp_min = float(att.attrib["min"])
                        self.atmosphereRange.temp_max = float(att.attrib["max"])
                    elif att.tag == "roughness":
                        self.atmosphereRange.rough_min = float(att.attrib["min"])
                        self.atmosphereRange.rough_max = float(att.attrib["max"])
                    elif att.tag == "xwind":
                        self.atmosphereRange.xwind_min = float(att.attrib["min"])
                        self.atmosphereRange.xwind_max = float(att.attrib["max"])
                    elif att.tag == "ywind":
                        self.atmosphereRange.ywind_min = float(att.attrib["min"])
                        self.atmosphereRange.ywind_max = float(att.attrib["max"])

    def parse_buildings(self):
        building_index = 0
        for i in self.root:
            if i.tag == "sectors":
                for att in i:
                    if att.tag == "building":
                        for j in self.root:
                            if j.tag == "waypoints":
                                for wp in j:
                                    if wp.attrib["name"] == att[0].attrib["name"]:
                                        self.buildings[building_index][0][0] = float(
                                            wp.attrib["x"]
                                        )
                                        self.buildings[building_index][1][0] = float(
                                            wp.attrib["y"]
                                        )
                                        self.buildings[building_index][2][0] = float(
                                            wp.attrib["height"]
                                        )
                                    elif wp.attrib["name"] == att[1].attrib["name"]:
                                        self.buildings[building_index][0][1] = float(
                                            wp.attrib["x"]
                                        )
                                        self.buildings[building_index][1][1] = float(
                                            wp.attrib["y"]
                                        )
                                        if com.is_float(wp.attrib["height"]):
                                            self.buildings[building_index][2][1] = (
                                                float(wp.attrib["height"])
                                            )
                                        else:
                                            self.buildings[building_index][2][1] = (
                                                wp.attrib["height"]
                                            )
                                        self.buildings.append([[0, 0], [0, 0], [0, 0]])
                                        building_index += 1

    def parse_sim_space(self):
        for i in self.root:
            if i.tag == "sectors":
                for att in i:
                    if att.tag == "sector" and att.attrib["name"] == "SIM_SPACE":
                        for j in self.root:
                            if j.tag == "waypoints":
                                for wp in j:
                                    if wp.attrib["name"] == att[0].attrib["name"]:
                                        self.pprz_sim_space[0][0] = float(
                                            wp.attrib["x"]
                                        )
                                        self.pprz_sim_space[1][0] = float(
                                            wp.attrib["y"]
                                        )
                                        self.pprz_sim_space[2][0] = float(
                                            wp.attrib["height"]
                                        )
                                    elif wp.attrib["name"] == att[1].attrib["name"]:
                                        self.pprz_sim_space[0][1] = float(
                                            wp.attrib["x"]
                                        )
                                        self.pprz_sim_space[1][1] = float(
                                            wp.attrib["y"]
                                        )
                                        self.pprz_sim_space[2][1] = float(
                                            wp.attrib["height"]
                                        )

    def parse_optimization(self):
        for i in self.root:
            if i.tag == "optimization":
                self.num_cpus = i.attrib["num_cpus"]
                self.start_sim_num = i.attrib["start_sim_num"]
                self.nsga2_pop = i.attrib["nsga2_pop"]
                self.nsga2_num_gen = i.attrib["nsga2_num_gen"]
                self.sim_run_time = int(i.attrib["sim_run_time"])
                self.batch_name = i.attrib["batch_name"]
                self.pprz_base_trace = i.attrib["pprz_base_trace"]

    def parse_fp(self):
        self.fp_name, self.fp_path = com.get_flight_plan(self.ac_name)
        print(self.fp_name[13:])
        print(self.fp_path)
        self.tree = ET.parse(self.fp_path)
        self.root = self.tree.getroot()

    def parse(self):
        self.parse_fp()
        self.parse_optimization()
        self.parse_test_blocks()
        self.parse_fp_vars()
        self.parse_atmospheric_range()
        self.parse_buildings()
        self.parse_sim_space()
