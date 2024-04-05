from src import Kaze
import argparse
import os.path

from src.KazeProblemEW import KazeProblemEW
from src.KazeParser import KazeParser
from src import Common as com


parser = argparse.ArgumentParser()
parser.add_argument("ac", help="Aircraft Name", type=str)
args = parser.parse_args()

kaze_parser = KazeParser(args.ac)
kaze_parser.parse()

# Make dir to save outputs
if not os.path.exists(com.VAR_PATH):
    os.system("mkdir " + com.VAR_PATH)
batch_path = com.VAR_PATH + "/batch_1"
if os.path.exists(batch_path):
    os.system("rm -r " + batch_path)

os.system("mkdir " + batch_path)

kaze = Kaze.Kaze(kaze_parser)

problem = KazeProblemEW(
    kaze, kaze_parser.test_blocks, kaze_parser.atmosphereRange, kaze_parser.fp_vars
)
res = problem.minimize(10, 10)

com.print_results(res, problem)
