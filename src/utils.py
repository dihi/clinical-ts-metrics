"""
Contains the python implementation of code to process trajectories provided in the 
format described in this library
"""


def get_valid_times(predicted_times, predicted_risks, threshold, snooze_window = 2):
    """Returns the times that are not snoozed and above the threshold"""
    assert snooze_window >= 0, "snooze_window must be nonnegative"
    positive_prediction_times = []
    snooze_boundary = -1
    for i in range(len(predicted_times)):
        if predicted_times[i] > snooze_boundary and predicted_risks[i] > threshold:
            positive_prediction_times.append(predicted_times[i])
            snooze_boundary = predicted_times[i] + snooze_window
    return positive_prediction_times           


def get_prediction_level_metrics(positive_prediction_times, detection_window, event_time):
    num_tp = 0
    num_fp = 0
    for p in positive_prediction_times[::-1]:
        if p < event_time and p >= (event_time - detection_window):
            num_tp += 1
        else:
            num_fp += 1
    return num_tp, num_fp


def get_metrics(trajectory_list, thresholds, snooze_window, detection_window):
    """
    Returns
    -------
    result: List[Dict]
        a list of dictionaries with keys corresponding to the counts of each of the component metrics
         - threshold
         - episode_tp
         - episode_fp
         - episode_tn
         - episode_fn
         - prediction_tp
         - prediction_fp
    """
    result_list = []
    for th in thresholds:
        episode_tp = 0
        episode_fp = 0
        episode_fn = 0
        episode_tn = 0
        prediction_tp = 0
        prediction_fp = 0
        for traj in trajectory_list:
            positive_predictions = get_valid_times(predicted_times=traj['predicted_times'],
                                                   predicted_risks=traj['predicted_risks'],
                                                   threshold=th,
                                                   snooze_window=snooze_window)
            if traj['event_occurred']:
                num_tp, num_fp = get_prediction_level_metrics(positive_predictions, detection_window, traj['event_time'])
                
                # Episode-level False Negative if no true positive predictions
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
                    
        result_list.append({
            'threshold': th,
            'episode_tp': episode_tp,
            'episode_fp': episode_fp,
            'episode_tn': episode_tn,
            'episode_fn': episode_fn,
            'prediction_tp': prediction_tp,
            'prediction_fp': prediction_fp
        })
        
    return result_list