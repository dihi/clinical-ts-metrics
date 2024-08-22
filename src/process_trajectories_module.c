#include <Python.h>
#include "process_trajectories.c"

// Helper function to convert Python list or tuple to C array
int convert_to_c_array(PyObject *input, double **output, int *len) {
    // If input is a single Python float, convert it directly
    if (PyFloat_Check(input)) {
        *len = 1;
        *output = (double *)malloc(*len * sizeof(double));
        if (*output == NULL) {
            PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for array");
            return -1;
        }
        (*output)[0] = PyFloat_AsDouble(input);
    } 
    // If input is a list or tuple
    else if (PyList_Check(input) || PyTuple_Check(input)) {
        *len = PySequence_Size(input);
        *output = (double *)malloc(*len * sizeof(double));
        if (*output == NULL) {
            PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for array");
            return -1;
        }
        for (int i = 0; i < *len; i++) {
            PyObject *item = PySequence_GetItem(input, i);
            if (PyFloat_Check(item) || PyLong_Check(item)) {
                (*output)[i] = PyFloat_AsDouble(item);
            } else if (PyDict_Check(item)) {
                PyObject *predicted_risks = PyDict_GetItemString(item, "predicted_risks");
                if (!PyList_Check(predicted_risks)) {
                    PyErr_SetString(PyExc_TypeError, "predicted_risks must be a list");
                    free(*output);
                    *output = NULL;  // Set pointer to NULL after freeing
                    Py_DECREF(item);
                    return -1;
                }
                PyObject *risk_item = PyList_GetItem(predicted_risks, 0);
                if (!PyFloat_Check(risk_item)) {
                    PyErr_SetString(PyExc_TypeError, "All predicted_risks elements must be floats");
                    free(*output);
                    *output = NULL;  // Set pointer to NULL after freeing
                    Py_DECREF(item);
                    return -1;
                }
                (*output)[i] = PyFloat_AsDouble(risk_item);
            } else {
                PyErr_SetString(PyExc_TypeError, "All elements must be floats or dictionaries");
                free(*output);
                *output = NULL;  // Set pointer to NULL after freeing
                Py_DECREF(item);
                return -1;
            }
            Py_DECREF(item);
        }
    } 
    // If input is not a Python number, list, or tuple
    else {
        PyErr_SetString(PyExc_TypeError, "Input must be a float, list, or tuple");
        return -1;
    }
    return 0;
}

// Wrapper function for process_trajectories
static PyObject* py_process_trajectories(PyObject* self, PyObject* args) {
    PyObject *trajectories;
    PyObject *thresholds;
    PyObject *detection_window_obj;
    PyObject *snooze_window_obj;
    double detection_window;
    double snooze_window;

    if (!PyArg_ParseTuple(args, "OOOO", &trajectories, &thresholds, &detection_window_obj, &snooze_window_obj)) {
        return NULL;
    }

    detection_window = PyFloat_AsDouble(detection_window_obj);
    snooze_window = PyFloat_AsDouble(snooze_window_obj);

    PyObject *result_list = PyList_New(0);
    if (result_list == NULL) {
        return PyErr_NoMemory();
    }

    if (process_trajectories(trajectories, thresholds, detection_window, snooze_window, result_list) == -1) {
        Py_DECREF(result_list);
        return NULL;
    }

    return result_list;
}

// Method definitions
static PyMethodDef ProcessTrajectoriesMethods[] = {
    {"process_trajectories", py_process_trajectories, METH_VARARGS, "Process trajectories and calculate metrics"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef process_trajectories_module = {
    PyModuleDef_HEAD_INIT,
    "process_trajectories",
    NULL,
    -1,
    ProcessTrajectoriesMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_process_trajectories(void) {
    return PyModule_Create(&process_trajectories_module);
}