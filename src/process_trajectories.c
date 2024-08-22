#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <Python.h>

// Forward declaration of the function
int convert_to_c_array(PyObject *input, double **output, int *len);

// Define a C structure for trajectory data
typedef struct {
    double *predicted_times;
    double *predicted_risks;
    int len;
    int event_occurred;
    double event_time;
} Trajectory;

// Function to convert Python trajectory to C structure
int convert_to_trajectory(PyObject *traj_obj, Trajectory *traj) {
    PyObject *predicted_times_obj = PyDict_GetItemString(traj_obj, "predicted_times");
    PyObject *predicted_risks_obj = PyDict_GetItemString(traj_obj, "predicted_risks");
    PyObject *event_occurred_obj = PyDict_GetItemString(traj_obj, "event_occurred");
    PyObject *event_time_obj = PyDict_GetItemString(traj_obj, "event_time");

    traj->len = PyList_Size(predicted_times_obj);
    traj->predicted_times = (double *)malloc(traj->len * sizeof(double));
    traj->predicted_risks = (double *)malloc(traj->len * sizeof(double));
    if (traj->predicted_times == NULL || traj->predicted_risks == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for trajectory arrays");
        return -1;
    }

    for (int j = 0; j < traj->len; j++) {
        traj->predicted_times[j] = PyFloat_AsDouble(PyList_GetItem(predicted_times_obj, j));
        traj->predicted_risks[j] = PyFloat_AsDouble(PyList_GetItem(predicted_risks_obj, j));
    }

    traj->event_occurred = PyObject_IsTrue(event_occurred_obj);
    traj->event_time = PyFloat_AsDouble(event_time_obj);

    return 0;
}

// Function to get valid times
void get_valid_times(double *predicted_times, double *predicted_risks, int len, double threshold, double snooze_window, double *result, int *result_len) {
    double snooze_boundary = -1.0;
    int count = 0;

    for (int i = 0; i < len; i++) {
        if (predicted_times[i] > snooze_boundary && predicted_risks[i] > threshold) {
            result[count++] = predicted_times[i];
            snooze_boundary = predicted_times[i] + snooze_window;
        }
    }

    *result_len = count;
}

// Function to get prediction level metrics
void get_prediction_level_metrics(double *positive_prediction_times, int len, double detection_window, double event_time, int *num_tp, int *num_fp) {
    *num_tp = 0;
    *num_fp = 0;

    for (int i = 0; i < len; i++) {
        if (positive_prediction_times[i] < event_time && positive_prediction_times[i] >= (event_time - detection_window)) {
            (*num_tp)++;
        } else {
            (*num_fp)++;
        }
    }
}

// Main function to process trajectories
int process_trajectories(PyObject *trajectories_obj, PyObject *thresholds_obj, double detection_window, double snooze_window, PyObject *result_list) {
    double *thresholds = NULL;
    int num_trajectories, num_thresholds;

    // Convert thresholds to C array
    if (convert_to_c_array(thresholds_obj, &thresholds, &num_thresholds) == -1) {
        return -1;
    }

    num_trajectories = PyList_Size(trajectories_obj);
    Trajectory *trajectories = (Trajectory *)malloc(num_trajectories * sizeof(Trajectory));
    if (trajectories == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for trajectories");
        free(thresholds);
        return -1;
    }

    // Convert each Python trajectory to C structure
    for (int i = 0; i < num_trajectories; i++) {
        PyObject *traj_obj = PyList_GetItem(trajectories_obj, i);
        if (convert_to_trajectory(traj_obj, &trajectories[i]) == -1) {
            for (int j = 0; j < i; j++) {
                free(trajectories[j].predicted_times);
                free(trajectories[j].predicted_risks);
            }
            free(trajectories);
            free(thresholds);
            return -1;
        }
    }

    for (int t = 0; t < num_thresholds; t++) {
        double threshold = thresholds[t];

        int episode_tp = 0;
        int episode_fp = 0;
        int episode_fn = 0;
        int episode_tn = 0;
        int prediction_tp = 0;
        int prediction_fp = 0;

        for (int i = 0; i < num_trajectories; i++) {
            Trajectory *traj = &trajectories[i];

            double positive_predictions[traj->len];
            int positive_len;
            get_valid_times(traj->predicted_times, traj->predicted_risks, traj->len, threshold, snooze_window, positive_predictions, &positive_len);

            if (traj->event_occurred) {
                int num_tp, num_fp;
                get_prediction_level_metrics(positive_predictions, positive_len, detection_window, traj->event_time, &num_tp, &num_fp);

                if (num_tp == 0) {
                    episode_fn++;
                } else {
                    episode_tp++;
                }
                prediction_tp += num_tp;
                prediction_fp += num_fp;
            } else {
                if (positive_len > 0) {
                    prediction_fp += positive_len;
                    episode_fp++;
                } else {
                    episode_tn++;
                }
            }
        }

        PyObject *result_dict = Py_BuildValue("{s:d, s:i, s:i, s:i, s:i, s:i, s:i}",
                                              "threshold", threshold,
                                              "episode_tp", episode_tp,
                                              "episode_fp", episode_fp,
                                              "episode_tn", episode_tn,
                                              "episode_fn", episode_fn,
                                              "prediction_tp", prediction_tp,
                                              "prediction_fp", prediction_fp);
        PyList_Append(result_list, result_dict);
        Py_DECREF(result_dict);
    }

    // Free allocated memory
    for (int i = 0; i < num_trajectories; i++) {
        free(trajectories[i].predicted_times);
        free(trajectories[i].predicted_risks);
    }
    free(trajectories);
    free(thresholds);

    return 0;
}