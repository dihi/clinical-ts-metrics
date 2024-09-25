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