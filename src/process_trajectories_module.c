#include <Python.h>

// Forward declaration of the process_trajectories function
int process_trajectories(PyObject *trajectories_obj, double snooze_window, double detection_window, PyObject *result_list);

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
        *output = (double *)calloc(*len, sizeof(double));  // Use calloc instead of malloc
        if (*output == NULL) {
            PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for array");
            return -1;
        }
        for (int i = 0; i < *len; i++) {
            PyObject *item = PySequence_GetItem(input, i);
            if (!item) {
                free(*output);
                *output = NULL;
                return -1;
            }
            if (PyFloat_Check(item) || PyLong_Check(item)) {
                (*output)[i] = PyFloat_AsDouble(item);
            } else if (PyDict_Check(item)) {
                PyObject *predicted_risks = PyDict_GetItemString(item, "predicted_risks");
                if (!PyList_Check(predicted_risks)) {
                    PyErr_SetString(PyExc_TypeError, "predicted_risks must be a list");
                    free(*output);
                    *output = NULL;  // Set pointer to NULL after freeing
                    return -1;
                }
                Py_ssize_t predicted_risks_len = PyList_Size(predicted_risks);
                if (predicted_risks_len > 1) {
                    PyErr_SetString(PyExc_ValueError, "predicted_risks list has more than one element");
                    free(*output);
                    *output = NULL;  // Set pointer to NULL after freeing
                    return -1;
                }
                PyObject *risk_item = PyList_GetItem(predicted_risks, 0);
                if (!PyFloat_Check(risk_item)) {
                    PyErr_SetString(PyExc_TypeError, "All predicted_risks elements must be floats");
                    free(*output);
                    *output = NULL;  // Set pointer to NULL after freeing
                    return -1;
                }
                (*output)[i] = PyFloat_AsDouble(risk_item);
            } else {
                PyErr_SetString(PyExc_TypeError, "All elements must be floats or dictionaries");
                free(*output);
                *output = NULL;  // Set pointer to NULL after freeing
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
static PyObject* py_process_trajectories(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject *trajectories;
    PyObject *snooze_window_obj;
    PyObject *detection_window_obj;
    double snooze_window;
    double detection_window;

    static char *kwlist[] = {"trajectories", "snooze_window", "detection_window", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OOO", kwlist, &trajectories, &snooze_window_obj, &detection_window_obj)) {
        return NULL;
    }

    if (!PyFloat_Check(snooze_window_obj) || !PyFloat_Check(detection_window_obj)) {
        PyErr_SetString(PyExc_TypeError, "snooze_window and detection_window must be floats");
        return NULL;
    }

    snooze_window = PyFloat_AsDouble(snooze_window_obj);
    detection_window = PyFloat_AsDouble(detection_window_obj);

    if (PyErr_Occurred()) {
        return NULL;
    }

    PyObject *result_list = PyList_New(0);
    if (result_list == NULL) {
        return PyErr_NoMemory();
    }

    if (process_trajectories(trajectories, snooze_window, detection_window, result_list) == -1) {
        Py_DECREF(result_list);
        return NULL;
    }

    return result_list;
}

// Method definitions
static PyMethodDef ProcessTrajectoriesMethods[] = {
    {"process_trajectories", (PyCFunction)py_process_trajectories, METH_VARARGS | METH_KEYWORDS, "Process trajectories and calculate metrics"},
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
    PyObject *m = PyModule_Create(&process_trajectories_module);
    if (m == NULL) {
        return NULL;
    }
    
    // Initialize Python's threads
    PyEval_InitThreads();
    
    return m;
}
