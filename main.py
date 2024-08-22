import process_trajectories
import json 
from src import utils
import numpy as np
from typing import List
import time 

with open("./benchmark_data/benchmark_trajectories_200.json", "r") as f:
    benchmark_200 = json.load(f)

with open("./benchmark_data/benchmark_trajectories_2000.json", "r") as f:
    benchmark_2000 = json.load(f)
    
#with open("./benchmark_data/benchmark_trajectories_20000.json", "r") as f:
#    benchmark_20000 = json.load(f)


start_time_python = time.time()
results_python = utils.get_metrics(benchmark_2000, thresholds=np.linspace(0,1, 1000), snooze_window=5, detection_window=12)[0:2]
end_time_python = time.time()
print(f"Python function execution time: {end_time_python - start_time_python} seconds")

start_time_c = time.time()
result_c = process_trajectories.process_trajectories(benchmark_2000, list(np.linspace(0.0,1.0, 1000)), 5.0, 12.0)
end_time_c = time.time()
print(f"C function execution time: {end_time_c - start_time_c} seconds")
