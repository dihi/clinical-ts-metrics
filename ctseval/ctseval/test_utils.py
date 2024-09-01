from .utils import validate_trajectories_schema
def get_valid_times(predicted_times, predicted_risks, threshold, snooze_window):

    result = []
    snooze_boundary = -1.0
    for time, risk in zip(predicted_times, predicted_risks):
        if time > snooze_boundary and risk > threshold:
            result.append(time)
            snooze_boundary = time + snooze_window
    return result

def get_prediction_level_metrics(positive_prediction_times, detection_window, event_time):
    num_tp = sum(1 for p in positive_prediction_times if event_time - detection_window <= p < event_time)
    num_fp = len(positive_prediction_times) - num_tp
    return num_tp, num_fp

def calculate_metrics(trajectory_list, threshold, snooze_window, detection_window):
    episode_tp = episode_fp = episode_fn = episode_tn = 0
    prediction_tp = prediction_fp = 0

    for traj in trajectory_list:
        positive_predictions = get_valid_times(traj['predicted_times'], traj['predicted_risks'], threshold, snooze_window)
        if traj['event_occurred']:
            num_tp, num_fp = get_prediction_level_metrics(positive_predictions, detection_window, traj['event_time'])
            episode_tp += (num_tp > 0)
            episode_fn += (num_tp == 0)
            prediction_tp += num_tp
            prediction_fp += num_fp
        else:
            episode_fp += (len(positive_predictions) > 0)
            episode_tn += (len(positive_predictions) == 0)
            prediction_fp += len(positive_predictions)

    return {
        'threshold': threshold,
        'episode_tp': episode_tp,
        'episode_fp': episode_fp,
        'episode_tn': episode_tn,
        'episode_fn': episode_fn,
        'prediction_tp': prediction_tp,
        'prediction_fp': prediction_fp
    }

def get_metrics(trajectory_list, snooze_window, detection_window):
    validate_trajectories_schema(trajectory_list)  # Validate trajectories
    if snooze_window == 0:
        return get_metrics_no_snooze(trajectory_list, detection_window)
    
    risk_scores = sorted({risk for traj in trajectory_list for risk in traj['predicted_risks']}, reverse=True)
    return [calculate_metrics(trajectory_list, th, snooze_window, detection_window) for th in risk_scores]

def get_approximate_metrics(trajectory_list, thresholds, snooze_window, detection_window):
    validate_trajectories_schema(trajectory_list)  # Validate trajectories
    if snooze_window == 0:
        print("Warning: Snooze window is set to 0. Using get_metrics instead for better performance and accuracy.")
        return get_metrics(trajectory_list, snooze_window, detection_window)
    return [calculate_metrics(trajectory_list, th, snooze_window, detection_window) for th in thresholds]

def get_metrics_no_snooze(trajectories, detection_window=24):
    validate_trajectories_schema(trajectories)  # Validate trajectories
    event_occurs_episodes = set()
    all_episodes = set()
    risk_scores = {}

    for i, traj in enumerate(trajectories):
        traj['id'] = i
        all_episodes.add(i)
        if traj['event_occurred']:
            event_occurs_episodes.add(i)
            within_detection_window = [(traj['event_time'] - t) <= detection_window for t in traj['predicted_times']]
        else:
            within_detection_window = [False] * len(traj['predicted_times'])
        
        for risk, within_window in zip(traj['predicted_risks'], within_detection_window):
            risk_scores.setdefault(risk, []).append((within_window, i))

    sorted_risk_scores = sorted(risk_scores.keys(), reverse=True)
    positive_prediction_episodes = set()
    negative_prediction_episodes = set()
    episode_tp = episode_fp = episode_fn = episode_tn = 0
    prediction_tp = prediction_fp = 0
    
    output_metrics = []
    for score in sorted_risk_scores:
        for det_window, ep_id in risk_scores[score]:
            if det_window:
                prediction_tp += 1
                if ep_id not in positive_prediction_episodes:
                    positive_prediction_episodes.add(ep_id)
                    episode_tp += (ep_id in event_occurs_episodes)
            else:
                prediction_fp += 1
                if ep_id not in negative_prediction_episodes:
                    negative_prediction_episodes.add(ep_id)
                    episode_fp += (ep_id not in event_occurs_episodes)

        episode_fn = len(event_occurs_episodes) - episode_tp
        episode_tn = len(all_episodes) - len(event_occurs_episodes) - episode_fp

        output_metrics.append({
            "threshold": score,
            "episode_tp": episode_tp,
            "episode_fp": episode_fp,
            "episode_tn": episode_tn,
            "episode_fn": episode_fn,
            "prediction_tp": prediction_tp,
            "prediction_fp": prediction_fp
        })

    return output_metrics
