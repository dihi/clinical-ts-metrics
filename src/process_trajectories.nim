import std/json
import std/lenientops
import std/terminal
import std/sequtils
import times, strutils
import arraymancer
import argParse
import suru

var parser = newParser:
    help("This script generates episode-level and prediction-level metrics used for downstream calculation of metrics such as precision, recall, sensitivity, specificity, etc.")
    option("-i", "--inputfile", help="The location of the input trajectory data")
    option("-o", "--outputfile", help="The location of the output data", default=some("metrics_output.json"))
    option("-n", "--numthresholds", help="The number of thresholds to consider. Creates an equally-spaced array from 0 to 1.", default=some("100"))
    option("-d", "--detectionwindow", help="Size of detection window")
    option("-s", "--snoozewindow", help="Size of the snoozing window")
    flag("-a", "--allthresholds")
    
var inputfile: string
var outputfile: string
var granularity: int
var detectionwindow: float
var snoozewindow: float
var allthresholds: bool

try:
    let opts = parser.parse()
    if opts.inputfile == "":
        raise newException(UsageError, "==== Input File Not found! ====")
    elif opts.detectionwindow == "":
        raise newException(UsageError, "==== Detection Window not found! ====")
    elif opts.snoozewindow == "":
        raise newException(USageError, "==== Snoozing Window not found! ====")
    else:
        echo "Running with the following arguments: \n"
        echo "-------------------------------------"
        stdout.styledWriteLine(fgDefault, "Input file path: ", fgGreen, opts.inputfile)
        stdout.styledWriteLine(fgDefault, "Output file path: ", fgGreen, opts.outputfile)
        stdout.styledWriteLine(fgDefault, "Number of thresholds: ", fgRed, opts.numthresholds)
        stdout.styledWriteLine(fgDefault, "Size of detection window: ", fgRed, opts.detectionwindow)
        stdout.styledWriteLine(fgDefault, "Size of snoozing window: ", fgRed, opts.snoozewindow)
      
        inputfile = opts.inputfile
        outputfile = opts.outputfile
        granularity = parseInt(opts.numthresholds)
        detectionwindow = parseFloat(opts.detectionwindow)
        snoozewindow = parseFloat(opts.snoozewindow)
        allthresholds = opts.allthresholds

except ShortCircuit:
    echo parser.help
    quit(1)
except UsageError:
    echo parser.help
    stderr.writeLine getCurrentExceptionMsg()
    quit(1)

proc get_valid_times(predicted_times: seq[float], predicted_risks: seq[float], threshold: float, snooze_window: float=2): seq[float] =
    var result: seq[float]
    var snooze_boundary = -1.0
    for index, time in predicted_times.pairs:
        if predicted_times[index] > snooze_boundary and predicted_risks[index] > threshold:
            result.add(predicted_times[index])
            snooze_boundary = predicted_times[index] + snooze_window
    return result

proc get_prediction_level_metrics(positive_prediction_times: seq[float], detection_window: float, event_time: float): (int, int) = 
    var num_tp = 0
    var num_fp = 0
    for p in positive_prediction_times:
        if p < event_time and p >= (event_time - detection_window):
            num_tp += 1
        else:
            num_fp += 1
    return (num_tp, num_fp)


let trajectoryDataStr = readFile(inputfile)
type Trajectory = object
    event_occurred: bool
    event_time: float
    predicted_times: seq[float]
    predicted_risks: seq[float]

let trajectoryData = parseJson(trajectoryDataStr)
var trajectories: seq[Trajectory]
var uniqueThresholds: seq[float]
for res in trajectoryData:
    let traj = res.to(Trajectory)
    trajectories.add(traj)
    if allthresholds == true:
        uniqueThresholds.add(traj.predicted_risks)

var THRESHOLDS: seq[float] = @[]
if allthresholds == true:
    sort(uniqueThresholds)
    THRESHOLDS = deduplicate(uniqueThresholds, isSorted=true)
    echo THRESHOLDS.len() 

else:
    THRESHOLDS= linspace(0, 1, granularity).toSeq1D()

# Serialize the result to json
var output: seq[JsonNode]
let time = epochTime()
var bar: SuruBar = initSuruBar()

bar[0].total = len(THRESHOLDS)
bar.setup()

for thresh in THRESHOLDS:
    var prediction_tp = 0
    var episode_tp = 0
    var prediction_fp = 0
    var episode_fp = 0
    var episode_fn = 0
    var episode_tn = 0
    for traj in trajectories:
        var positive_predictions = get_valid_times(traj.predicted_times, traj.predicted_risks, thresh, snoozewindow)  
        if traj.event_occurred:
            var (num_tp, num_fp) = get_prediction_level_metrics(positive_predictions, detectionwindow, traj.event_time)
            if num_tp == 0:
                episode_fn += 1
            else:
                episode_tp += 1
            prediction_tp += num_tp
            prediction_fp += num_fp
        
        else:
            if len(positive_predictions) > 0:
                prediction_fp += len(positive_predictions)
                episode_fp += 1
            else:
                episode_tn += 1   


    output.add( %* {      "threshold" : thresh,
                         "episode_tp" : episode_tp,
                         "episode_fp" : episode_fp,
                         "episode_tn" : episode_tn,
                         "episode_fn" : episode_fn,
                      "prediction_tp" : prediction_tp,
                      "prediction_fp" : prediction_fp
                    })
    inc bar
    bar.update(50_000_000)

    prediction_tp = 0
    episode_tp = 0
    prediction_fp = 0
    episode_fp = 0
    episode_fn = 0
    episode_tn = 0

bar.finish()

let endTime = epochTime() - time
let elapsedTime = endTime.formatFloat(format=ffDecimal, precision=3)
echo "Elapsed time: ", elapsedTime, "s"

writeFile(outputfile, content= pretty(%output))