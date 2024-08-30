import process_trajectories
import json 
from src import utils
import numpy as np
from typing import List
import time 

with open("./benchmark_data/benchmark_trajectories_200.json", "r") as f:
    benchmark_200 = json.load(f)

#with open("./benchmark_data/benchmark_trajectories_2000.json", "r") as f:
#    benchmark_2000 = json.load(f)
    
#with open("./benchmark_data/benchmark_trajectories_20000.json", "r") as f:
#    benchmark_20000 = json.load(f)

print("Validating trajectories schema...")
utils.validate_trajectories_schema(benchmark_200)
print("Trajectories schema validation passed.")
benchmark_200_fast = benchmark_200[0:20]

# start_time_python = time.time()
# results_python_snooze = utils.get_metrics(benchmark_200, snooze_window=0.000000001, detection_window=12)
# end_time_python = time.time()
# print(f"Python function execution time: {end_time_python - start_time_python} seconds")

# start_time_python = time.time()
# results_python_snooze_approximate = utils.get_approximate_metrics(benchmark_200, thresholds=np.linspace(0,1, 1000), snooze_window=0.000000001, detection_window=12)
# end_time_python = time.time()
# print(f"Python function execution time: {end_time_python - start_time_python} seconds")


start_time_python = time.time()
results_python = utils.get_metrics(benchmark_200, snooze_window=0, detection_window=12)
end_time_python = time.time()
print(f"Python function_no_snooze_exact execution time: {end_time_python - start_time_python} seconds")


# start_time_python = time.time()
# results_python_no_snooze_approximate = utils.get_approximate_metrics(benchmark_200, thresholds=np.linspace(0,1, 1000), snooze_window=0, detection_window=12)
# end_time_python = time.time()
# print(f"Python function_no_snooze_approximate execution time: {end_time_python - start_time_python} seconds")

start_time_c = time.time()
result_c_no_snooze = process_trajectories.process_trajectories(benchmark_200, 0.0, 12.0)
end_time_c = time.time()
print(f"C function no snooze execution time: {end_time_c - start_time_c} seconds")


start_time_c = time.time()
result_c = process_trajectories.process_trajectories(benchmark_200, 5.0, 12.0)
end_time_c = time.time()
print(f"C function execution time with snooze: {end_time_c - start_time_c} seconds")

if results_python == result_c_no_snooze:
    print("The results from the Python and C functions are the same.")
else:
    print("The results from the Python and C functions are different.")
    print("Python results (first 5 elements):", results_python[0:5])
    print("C results (first 5 elements):", result_c[0:5])
