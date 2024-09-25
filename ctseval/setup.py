from setuptools import setup, Extension

# Define the extension module
ctseval_module = Extension(
    'ctseval._ctseval',
    sources=[
        'ctseval/ctseval.c',
        'ctseval/_ctseval.c',
    ],
    include_dirs=[
        'ctseval/include',
    ],
)

# Setup the package
setup(
    name='ctseval',
    version='0.1.0',
    packages=['ctseval'],
    ext_modules=[ctseval_module],
    author='Your Name',
    author_email='your.email@example.com',
    description='A package for evaluating clinical time series predictions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ctseval',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)