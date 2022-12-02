# About

This repository contains code to generate metrics for clinical time series models at both the *prediction-level* as well as *episode-level* and in the presence of snoozing. The binary produces results up to 30x as fast as the python implementation provided. Due to the increased computation complexity of snoozing, this is often necessary to obtain results in a reasonable amount of time as the number and length of trajectories increases.

# Usage

Once trajectories are formatted according to the standard structure (described below), then download the binary from the releases and call the binary using:

`./process_trajectories -i INPUTFILE -o OUTPUTFILE -n NUMTHRESHOLDS -d DETECTIONWINDOW -s SNOOZEWINDOW`

```
Usage:
   [options] 

Options:
  -h, --help
  -i, --inputfile=INPUTFILE  The location of the input trajectory data
  -o, --outputfile=OUTPUTFILE
                             The location of the output data (default: metrics_output.json)
  -n, --numthresholds=NUMTHRESHOLDS
                             The number of thresholds to consider. Creates an equally-spaced array from 0 to 1. (default: 100)
  -d, --detectionwindow=DETECTIONWINDOW
                             Size of detection window
  -s, --snoozewindow=SNOOZEWINDOW
                             Size of the snoozing window
```


## Structure

All of the code in this repository assumes the following structure for trajectories:

```
[{
        "event_occurred": false,
        "event_time": 0, # ignored
        "predicted_times": [1, 2, 3.5, 20],
        "predicted_risks": [0.1, 0.2, 0.5, 0.8]
    },
    {
        "event_occurred": true,
        "event_time": 20,
        "predicted_times": [1, 17],
        "predicted_risks": [0.8, 0.1]
}]
```

 * `event_occurred` should be a boolean which describes whether or not the event of interest occurred during the current trajectory
 * `event_time` represents the time that the event occurred. If `event_occurred` is false, then this value is ignored
 * `predicted_times` represents an array that contains the times that predictions are generated. This should follow the same units as `event_time`
 * `predicted_risks` represent the values output by the model and should be the same length as the `predicted_times` array

These trajectories are stored in `JSON` format for interoperability purposes.

## Converting from Pandas DataFrames

The `src/create_benchmark_data.py` script has a function `convert_df_to_trajectory_list` which converts a Pandas Dataframe into the above format for downstream processing or writing out to `JSON`. The input Pandas Dataframe should have the following structure:

```
| episode_id | event_occurred | event_time | predicted_times | predicted_risks |
--------------------------------------------------------------------------------
|      1     |      True      |    20      |        7        |     0.2538      |
|      1     |      True      |    20      |        9        |     0.8188      |

...
```

# Compiling the tool yourself
This tool is written in the Nim programming language, which produces native, dependency-free binaries.

If your architecture isn't found in the releases tab, or you want to modify the code, you can compile the script yourself by downloading the dependencies using `nimble` and then running

`nim c process_trajectories.nim -d:release --gc:orc`

The current dependencies are `arraymancer`, `argParse` and `suru`. More details will be provided at a later date
