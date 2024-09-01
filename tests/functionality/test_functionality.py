import pytest 
import ctseval
import json

@pytest.fixture
def single_trajectory():
    return [{
        "predicted_times": [1.0, 2.0, 2.1],
        "predicted_risks": [0.1, 0.2, 0.2],
        "event_occurred": True,
        "event_time": 3.0
    }]

@pytest.fixture
def single_trajectory_w_snooze():
    return [{
        "predicted_times": [1.0, 2.0, 3.0, 4.0, 5.2], # If we snooze for 3 seconds, we should have another prediction_tp at 5.2 (if detection window is 8+)
        "predicted_risks": [0.1, 0.2, 0.9, 0.9, 0.2],
        "event_occurred": True,
        "event_time": 10.0
    }]

def test_single_trajectory_no_snooze(single_trajectory):
    result = ctseval.compute_metrics(single_trajectory, snooze_window=0, detection_window=1)
    expected_result = [
        {
            'threshold': 0.2,
            'episode_tp': 1, # this should be 1 because it is detected within 1 of the event time
            'episode_fp': 0,
            'episode_tn': 0, 
            'episode_fn': 0, 
            'prediction_tp': 1, # 1 True Positive at threshold 0.2
            'prediction_fp': 0 # No false positives since the other score is below the threshold
        },
        {
            'threshold': 0.1, 
            'episode_tp': 1, # At least 1 positive prediction within window 
            'episode_fp': 0, 
            'episode_tn': 0, 
            'episode_fn': 0, 
            'prediction_tp': 1, # 1 True Positive at threshold 0.1
            'prediction_fp': 1 # 1 False Positive at threshold 0.1 (the first score)
        }
    ]
    import pdb; pdb.set_trace()
    assert result == expected_result

def test_single_trajectory_w_snooze(single_trajectory_w_snooze):
    result = ctseval.compute_metrics(single_trajectory_w_snooze, snooze_window=3, detection_window=8)
    expected_result = [
        {'threshold': 0.9, 'episode_tp': 0, 'episode_fp': 0, 'episode_tn': 0, 'episode_fn': 1, 'prediction_tp': 0, 'prediction_fp': 0}, 
        {'threshold': 0.9, 'episode_tp': 0, 'episode_fp': 0, 'episode_tn': 0, 'episode_fn': 1, 'prediction_tp': 0, 'prediction_fp': 0}, 
        {'threshold': 0.2, 'episode_tp': 1, 'episode_fp': 0, 'episode_tn': 0, 'episode_fn': 0, 'prediction_tp': 1, 'prediction_fp': 0}, 
        {'threshold': 0.2, 'episode_tp': 1, 'episode_fp': 0, 'episode_tn': 0, 'episode_fn': 0, 'prediction_tp': 1, 'prediction_fp': 0}, 
        {'threshold': 0.1, 'episode_tp': 1, 'episode_fp': 0, 'episode_tn': 0, 'episode_fn': 0, 'prediction_tp': 2, 'prediction_fp': 0}
    ]
    assert result == expected_result