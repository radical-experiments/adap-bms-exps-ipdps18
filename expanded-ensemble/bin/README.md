# Details


## Requirements

* Requires addwlmod branch of gromacs to be installed on the HPC
* Requires pymbar package to be installed on the HPC as well
* These required packages are installed and shared on Supermic. In my experience, Supermic has had shortest queue times. Might be best to start with the same.

## EnTK, Radical Pilot Installation

First, we need to create a virtual environment. Following uses GCC python:

```
virtualenv $HOME/myenv
source $HOME/myenv/activate/bin/activate
```

Next, we need to install Radical Pilot.

```
pip install radical.pilot
```

Next, we install a specific branch of EnTK.

```
git clone https://github.com/radical-cybertools/radical.ensemblemd.git
cd radical.ensemblemd
git checkout feature/get_unit_path
pip install .
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

Firstly, clone the current repository

```
git clone git@github.com:radical-collaboration/expanded-ensemble.git
cd expanded-ensemble/entk_scripts
```

The ```runme.py``` script contains the information about the application execution
workflow and the associated data movement. Please take a look at all the 
comments to understand the various sections.

In line 241, please add your xsede username. Example: ```username='vivek'```.


Execution command: 
```
RADICAL_ENTK_VERBOSE=info python runme.py --resource xsede.supermic
```


## Note

* Hopefully not, but there might be lingering permission issues which will get detected
once other users start running the code.
* The up-to-date alchemical analysis script is automatically downloaded from the MobleyLab repository and used.
* Previous data is collected and kept at ```/work/02734/vivek91/expanded_ensemble_data``` on Stampede.

