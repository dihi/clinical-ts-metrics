from .utils import validate_trajectories_schema, calculate_average_precision
from ._ctseval import compute_metrics_c

def compute_metrics(trajectories, snooze_window, detection_window, verbosity=1):
    """
    Compute metrics for clinical time series predictions.
    
    Args:
    trajectories (list): List of trajectory dictionaries.
    snooze_window (float): The snooze window duration.
    detection_window (float): The detection window duration.
    verbosity (int, optional): Verbosity level. Defaults to 1.
    
    Returns:
    results: List of dictionaries with episode-level and prediction-levelmetrics.
    """
    # Validate the trajectories
    validate_trajectories_schema(trajectories)
    
    # Compute metrics using the C function
    results = compute_metrics_c(trajectories, snooze_window, detection_window, verbosity)
    
    return results

__all__ = ['compute_metrics', 'validate_trajectories_schema', 'calculate_average_precision']