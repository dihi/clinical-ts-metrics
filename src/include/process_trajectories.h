#ifndef PROCESS_TRAJECTORIES_H
#define PROCESS_TRAJECTORIES_H

typedef struct {
    int len;
    double *predicted_times;
    double *predicted_risks;
    int event_occurred;
    double event_time;
} Trajectory;

typedef struct {
    double risk;
    int within_window;
    int ep_id;
} RiskScore;

int convert_to_trajectory(PyObject *traj_obj, Trajectory *traj);
int process_trajectories(PyObject *trajectories_obj, double snooze_window, double detection_window, PyObject *result_list, int verbosity);
void get_metrics_no_snooze(Trajectory *trajectories, int num_trajectories, double detection_window, PyObject *result_list);
int compare_risk_scores(const void *a, const void *b);
int convert_to_c_array(PyObject *input, double **output, int *len);

#endif // PROCESS_TRAJECTORIES_H
