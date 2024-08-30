from setuptools import setup, Extension

# Define the extension module
process_trajectories_module = Extension(
    'process_trajectories',
    sources=[
        'src/process_trajectories.c',
        'src/process_trajectories_module.c',
    ],
    include_dirs=[
        '/Users/michaelgao/miniconda3/envs/dspy39/include/python3.9',
        'src/include',

    ],
    extra_compile_args=['-O3', '-march=native', '-flto'],
    extra_link_args=['-flto', '-g'],
)

# Setup the package
setup(
    name='clinical_ts_metrics',
    version='1.0',
    ext_modules=[process_trajectories_module]
)