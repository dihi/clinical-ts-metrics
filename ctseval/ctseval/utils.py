import numpy as np

def validate_trajectories_schema(trajectories):
    required_keys = {'predicted_times', 'predicted_risks', 'event_occurred', 'event_time'}
    
    for traj in trajectories:
        if not isinstance(traj, dict):
            raise ValueError("Each trajectory must be a dictionary.")
        
        if not required_keys.issubset(traj.keys()):
            raise ValueError(f"Each trajectory must contain the keys: {required_keys}")
        
        if not isinstance(traj['predicted_times'], list) or not all(isinstance(t, (int, float)) for t in traj['predicted_times']):
            raise ValueError("The 'predicted_times' key must be a list of numbers.")
        
        if len(traj['predicted_times']) < 1:
            raise ValueError("The 'predicted_times' list must contain at least one element.")
        
        if not isinstance(traj['predicted_risks'], list) or not all(isinstance(r, (int, float)) for r in traj['predicted_risks']):
            raise ValueError("The 'predicted_risks' key must be a list of numbers.")
        
        if len(traj['predicted_risks']) < 1:
            raise ValueError("The 'predicted_risks' list must contain at least one element.")
        
        if not isinstance(traj['event_occurred'], bool):
            raise ValueError("The 'event_occurred' key must be a boolean.")
        
        if not isinstance(traj['event_time'], (int, float)):
            raise ValueError("The 'event_time' key must be a number.")
        
    return True

def calculate_average_precision(results):
    """
    Calculate the average precision from the results of compute_metrics_c.
    
    Args:
    results (list): List of dictionaries containing metrics at different thresholds.
    
    Returns:
    float: The calculated average precision.
    """
    precisions = []
    recalls = []
    
    for result in results:
        tp = result['episode_tp']
        fp = result['episode_fp']
        fn = result['episode_fn']
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        precisions.append(precision)
        recalls.append(recall)
    
    # Sort by recall
    sorted_pairs = sorted(zip(recalls, precisions), key=lambda x: x[0])
    recalls, precisions = zip(*sorted_pairs)
    
    # Calculate the area under the precision-recall curve
    ap = 0
    prev_recall = 0
    for recall, precision in zip(recalls, precisions):
        ap += precision * (recall - prev_recall)
        prev_recall = recall
    
    return ap