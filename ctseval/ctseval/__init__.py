from .utils import (validate_trajectories_schema, auprc_score, precision_recall_curve, recall_at_fixed_precision, precision_at_fixed_recall, roc_curve, precision_recall_curve, auroc_score)
from ._ctseval import compute_metrics_c

def compute_metrics(trajectories: list[dict], snooze_window: float, detection_window: float, verbosity=1) -> list[dict]:
    """
    Compute metrics for clinical time series predictions.
    
    Args:
    trajectories: List of trajectory dictionaries. Further described in the validate_trajectories_schema function.
    snooze_window (float): The snooze window duration in units of time.
    detection_window (float): The detection window duration in units of time.
    verbosity (int, optional): Verbosity level. Defaults to 1.
    
    Returns:
    results: List of dictionaries with episode-level and prediction-level metrics.
        Each dictionary has the following keys:
            {
                "threshold":,
                "episode_tp",
                "episode_fp",
                "episode_tn",
                "episode_fn",
                "prediction_tp",
                "prediction_fp"
            }
        The returned list should have 1 entry for each possible threshold encountered, along with 1 additional value to make sure that the last threshold is accounted for
    """
    validate_trajectories_schema(trajectories)
    results = compute_metrics_c(trajectories, snooze_window, detection_window, verbosity)
    return results

__all__ = ['compute_metrics', 'validate_trajectories_schema', 'auprc_score', 'precision_recall_curve', 'recall_at_fixed_precision', 'precision_at_fixed_recall', 'roc_curve', 'auroc_score']