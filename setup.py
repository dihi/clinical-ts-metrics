from setuptools import setup, Extension
import sysconfig

# Compile with optimization flags for performance
extra_compile_args = ['-O3', '-march=native', '-flto']
extra_link_args = ['-flto']

# Define the extension module
process_trajectories_module = Extension(
      'process_trajectories',
      sources=['src/process_trajectories_module.c'],
      include_dirs=[sysconfig.get_path('include')],
      extra_compile_args=extra_compile_args,
      extra_link_args=extra_link_args,
)

# Setup script
setup(
      name='process_trajectories',
      version='1.0',
      description='Process trajectories and calculate metrics',
      ext_modules=[process_trajectories_module],
)