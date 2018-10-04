# Details


## Requirements

* Requires addwlmod branch of gromacs to be installed on the HPC
* Requires pymbar package to be installed on the HPC as well
* These required packages are installed and shared on Supermic. In my experience, Supermic has had shortest queue times. Might be best to start with the same.

## EnTK Installation

First, we need to create a virtual environment. Following uses GCC python:

```
virtualenv $HOME/myenv
source $HOME/myenv/activate/bin/activate
```

Next, we need to install EnTK.

```
pip install radical.entk
```


## Setting up access to HPCs

Currently, all packages and permissions are setup for SuperMIC. I will verify 
package versions on Comet(!) and Stampede and share with others. First we will start with SuperMIC.

[Supermic](http://www.hpc.lsu.edu/resources/hpc/system.php?system=SuperMIC)
require GSISSH access. Instructions to setup gsissh access for Ubuntu can be 
found [here](https://github.com/vivek-bala/docs/blob/master/misc/gsissh_setup_stampede_ubuntu_xenial.sh/).
Please note that this has been tested only for xenial and trusty (for trusty, simple replace 'xenial'
with 'trusty' in all commands). Even then, there might be some additional steps
to setup gsissh correctly for your system. Happy to help!

As a heads up:

[Comet](http://www.sdsc.edu/support/user_guides/comet.html) requires 
passwordless SSH access. You can find instructions at 
```http://linuxproblem.org/art_9.html```

[Stampede](https://portal.tacc.utexas.edu/user-guides/stampede) also requires 
GSISSH.


## Executing the expanded ensemble scripts

### Repository clone

Firstly, clone the current repository

```
git clone git@github.com:radical-experiments/adaptive-bms-experiments.git
cd adaptive-bms-experiments/expanded-ensemble/bin
```

Note: The up-to-date alchemical analysis script is automatically downloaded from the MobleyLab repository and used.

### User settings 

The ```runme.py``` script contains the information about the application execution
workflow and the associated data movement. Please take a look at all the
comments to understand the various sections.

* Setup user settings in lines 12-17 of runme.py
* Setup resource requirement settings in lines 242-246 of runme.py

### Environment settings

Setup environment:
```
RADICAL_ENTK_VERBOSE=INFO
RADICAL_PILOT_VERBOSE=DEBUG
RADICAL_ENTK_PROFILE=True
RADICAL_PILOT_PROFILE=True
RADICAL_PILOT_DBURL="mongodb://user:user123@ds155252.mlab.com:55252/ipdps-bms-ee"
export SAGA_PTY_SSH_TIMEOUT=300
```

These variables enable verbosity and profiling of all runs.


### Execution

Execution command: 
```
RADICAL_ENTK_VERBOSE=INFO python runme.py
```
Output is produced in the "output" folder located in the current directory (same
as where the script resides).

