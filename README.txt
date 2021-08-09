Jarvis
======

`Jarvis` is an open source experimental controller for trapped ion QIP platforms. It centralizes communication between all instrumentation in the laboratory, providing access to 
all hardware from one place. It also enables automization of experiments.


Installation
------------

In order to install `Jarvis`, clone the GitHub repository locally with

```shell
git clone git@github.com:iqt/jarvis.git
```

The package requires several drivers to function. Please copy the library `Jarvis/user_lib/atmcd32d.llb` to your
labview installation folder `[Your NI Folder]/LabvVIEW####/user.lib/`.

The user may need to create a new FPGA target if the specifications are different.

After installation is complete, open the main Labview project `jarvis.lvproj`, and run the main VI `jarvis.vi`. 


Requirements
------------

The core of `Jarvis` uses Python and Labview. Additional mathematica scripts are provided for post-processing but are not required.

Please install Python 3.5 along with the following packages: NumPy, MatplotLib, SciPy, H5Py.

Please install Labview Full Development & Professional Development, minimum version 14.0, with the following additional 
packages: FPGA Module, Andor Software Development Kit (SDK), Live HDF5.


Pre-compilation flags
---------------------

Before running the Labview project, several flags can be set to aid development. To access these flags, go to
Project -> Properties -> Conditional Disable Symbols, and set them to TRUE or FALSE.

- FPGA_ENABLED == TRUE : FPGA code is compiled and functionalities enabled

- RUN_SIMULATED == TRUE : The main controller for pulse sequences is replaced by simulated data


                                                   
                                                   
                                                   
                                                   
                                                   
