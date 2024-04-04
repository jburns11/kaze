import numpy as np
import matplotlib.pyplot as plt
from src.WindDataParser import WindDataParser

Y = 0
T = 0
inputPath = "./var/batch_1/udales/out/001/fielddump.001.nc"
wind_parser = WindDataParser(inputPath)
z_range = 64

slice_arr = []

for z in range(z_range):
	slice_arr.append([])
	for x in range(-50, 50):
		slice_arr[z].append(wind_parser.get_east_west_wind(T, x, Y, z))
	print(x)

print(slice_arr)
np_slice_arr = np.array(slice_arr)

plt.imshow(np_slice_arr)
plt.show()
