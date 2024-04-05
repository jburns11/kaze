import os.path
import math
import numpy as np
import pymoo.optimize
import pymoo.termination
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2

from src import Common as com


class KazeProblemEW(ElementwiseProblem):
    def __init__(self, kaze, test_blocks, atmosphereRange, fp_vars):
        self.kaze = kaze
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
            os.system("mkdir " + com.VAR_PATH)
        batch_path = com.EXEC_PATH + "Kaze/var/batch_1"
        if os.path.exists(batch_path):
            os.system("rm -r " + batch_path)

        os.system("mkdir " + batch_path)

    def _evaluate(self, x, out, *args, **kwargs):
        atmosphere = com.Atmosphere(x[0], x[1], x[2], x[3], x[4], x[5])
        kazeInput = com.KazeInput(atmosphere, x[6:], self.start_sim_num)
        self.kaze.set_sim_params(kazeInput)
        self.kaze.generate_inputs()
        fitness = self.kaze.calc_fitness()
        self.kaze.clean_pprz()
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

    def minimize(self, n_gen, pop_size):
        termination = pymoo.termination.get_termination("n_gen", 10)

        algorithm = NSGA2(pop_size=10, copy_algorithm=True)

        return pymoo.optimize.minimize(
            self, algorithm, termination, seed=1, save_history=True, verbose=True
        )
