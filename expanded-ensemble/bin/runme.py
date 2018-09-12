__author__ = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2018, http://radical.rutgers.edu"
__license__ = "MIT"


from radical.entk import Pipeline, Stage, Task, AppManager
import argparse
import os
import glob


# User settings
ENSEMBLE_SIZE = 2    # Number of ensemble members / pipelines
TOTAL_ITERS = 2       # Number of iterations to run current trial
SEED = 1            # Seed for stage 1
GMX_PATH = '/home/trje3733/pkgs/gromacs/5.1.3.wlmod'
ALCH_ANA_PATH = '/home/vivek91/modules/alchemical-analysis'

# Book to store object names
book = dict()

# Iteration number to start with
cur_iter = [0 for _ in range(ENSEMBLE_SIZE)]


def get_pipeline(instance, iterations):

    def func_condition():

        global cur_iter

        if cur_iter[instance] < iterations:
            cur_iter[instance] += 1
            return True

        return False

    def func_on_true():

        global cur_iter, book

        # Create Stage 2
        s2 = Stage()
        s2.name = 'iter%s-s2' % cur_iter[instance]

        # Create a Task
        t2 = Task()
        t2.name = 'iter%s-s2-t2' % cur_iter[instance]

        t2.pre_exec = ['source %s/bin/GMXRC.bash' % GMX_PATH]
        t2.executable = ['gmx grompp']
        t2.arguments = ['-f', 'CB7G3_run.mdp',
                        '-c', 'CB7G3.gro',
                        '-p', 'CB7G3.top',
                        '-n', 'CB7G3.ndx',
                        '-o', 'CB7G3.tpr',
                        '-maxwarn', '10']
        t2.cores = 1
        t2.copy_input_data = [
            '$SHARED/CB7G3.ndx',
            '$SHARED/CB7G3.top',
            '$SHARED/3atomtypes.itp',
            '$SHARED/3_GMX.itp',
            '$SHARED/cucurbit_7_uril_GMX.itp'
        ]

        if cur_iter[instance] == 1:
            t2.copy_input_data += ['$Pipeline_%s_Stage_%s_Task_%s/CB7G3_run.mdp' % (p.name,
                                                                                    book[p.name]['stages'][-1]['name'],
                                                                                    book[p.name]['stages'][-1]['task']),
                                   '$SHARED/CB7G3.gro']
        else:
            t2.copy_input_data += ['$Pipeline_%s_Stage_%s_Task_%s/CB7G3_run.mdp' % (p.name,
                                                                                    book[p.name]['stages'][-1]['name'],
                                                                                    book[p.name]['stages'][-1]['task']),
                                   '$Pipeline_%s_Stage_%s_Task_%s/CB7G3.gro' % (p.name,
                                                                                book[p.name]['stages'][-2]['name'],
                                                                                book[p.name]['stages'][-2]['task'])]

        # Add the Task to the Stage
        s2.add_tasks(t2)

        # Add current Task and Stage to our book
        book[p.name]['stages'].append({'name': s2.name, 'task': t2.name})

        # Add Stage to the Pipeline
        p.add_stages(s2)

        # Create Stage 3
        s3 = Stage()
        s3.name = 'iter%s-s3' % cur_iter[instance]

        # Create a Task
        t3 = Task()
        t3.name = 'iter%s-s3-t3' % cur_iter[instance]
        t3.pre_exec = ['source %s/bin/GMXRC.bash' % GMX_PATH]
        t3.executable = ['gmx mdrun']
        t3.arguments = ['-nt', 20,
                        '-deffnm', 'CB7G3',
                        '-dhdl', 'CB7G3_dhdl.xvg', ]
        t3.cores = 20
        # t3.mpi = True
        t3.copy_input_data = ['$Pipeline_%s_Stage_%s_Task_%s/CB7G3.tpr' % (p.name,
                                                                           book[p.name]['stages'][-1]['name'],
                                                                           book[p.name]['stages'][-1]['task'])]
        t3.copy_output_data = ['CB7G3_dhdl.xvg > $SHARED/CB7G3_run{1}_gen{0}_dhdl.xvg'.format(cur_iter[instance], instance),
                                'CB7G3_pullf.xvg > $SHARED/CB7G3_run{1}_gen{0}_pullf.xvg'.format(cur_iter[instance], instance),
                                'CB7G3_pullx.xvg > $SHARED/CB7G3_run{1}_gen{0}_pullx.xvg'.format(cur_iter[instance], instance),
                                'CB7G3.log > $SHARED/CB7G3_run{1}_gen{0}.log'.format(cur_iter[instance], instance)
        ]
        t3.download_output_data = ['CB7G3.xtc > ./output/CB7G3_run{1}_gen{0}.xtc'.format(cur_iter[instance], instance),
                                    'CB7G3.log > ./output/CB7G3_run{1}_gen{0}.log'.format(cur_iter[instance], instance),
                                    'CB7G3_dhdl.xvg > ./output/CB7G3_run{1}_gen{0}_dhdl.xvg'.format(cur_iter[instance], instance),
                                    'CB7G3_pullf.xvg > ./output/CB7G3_run{1}_gen{0}_pullf.xvg'.format(cur_iter[instance], instance),
                                    'CB7G3_pullx.xvg > ./output/CB7G3_run{1}_gen{0}_pullx.xvg'.format(cur_iter[instance], instance),
                                    'CB7G3.gro > ./output/CB7G3_run{1}_gen{0}.gro'.format(cur_iter[instance], instance)]

        # Add the Task to the Stage
        s3.add_tasks(t3)

        # Add current Task and Stage to our book
        book[p.name]['stages'].append({'name': s3.name, 'task': t3.name})

        # Add Stage to the Pipeline
        p.add_stages(s3)

        # Create Stage 4
        s4 = Stage()
        s4.name = 'iter%s-s4' % cur_iter[instance]

        # Create a Task
        t4 = Task()
        t4.name = 'iter%s-s4-t4' % cur_iter[instance]
        t4.pre_exec = ['module load python/2.7.7-anaconda',
                       'export PYTHONPATH=%s/alchemical_analysis:$PYTHONPATH' % ALCH_ANA_PATH,
                       'export PYTHONPATH=%s:$PYTHONPATH' % ALCH_ANA_PATH,
                       'export PYTHONPATH=/home/vivek91/.local/lib/python2.7/site-packages:$PYTHONPATH',
                       'ln -s ../staging_area data']
        t4.executable = ['python']
        t4.arguments = ['analysis_2.py',
                        '--newname=CB7G3_run.mdp',
                        '--template=CB7G3_template.mdp',
                        '--dir=./data',
                        # '--prev_data=%s'%DATA_LOC
                        '--gen={0}'.format(cur_iter[instance], instance),
                        '--run={1}'.format(cur_iter[instance], instance)
                        ]
        t4.cores = 1
        t4.copy_input_data = ['$SHARED/analysis_2.py',
                              '$SHARED/alchemical_analysis.py',
                              '$SHARED/CB7G3_template.mdp',
                              ]

        t4.download_output_data = ['analyze_1/results.txt > ./output/results_run{1}_gen{0}.txt'.format(cur_iter[instance], instance),
                                    'STDOUT > ./output/stdout_run{1}_gen{0}'.format(cur_iter[instance], instance),
                                    'STDERR > ./output/stderr_run{1}_gen{0}'.format(cur_iter[instance], instance),
                                    'CB7G3_run.mdp > ./output/CB7G3_run{1}_gen{0}.mdp'.format(cur_iter[instance], instance),
                                    'results_average.txt > ./output/results_average_run{1}_gen{0}.txt'.format(cur_iter[instance], instance)
        ]

        s4.post_exec = {
            'condition': func_condition,
            'on_true': func_on_true,
            'on_false': func_on_false
        }

        # Add the Task to the Stage
        s4.add_tasks(t4)

        # Add current Task and Stage to our book
        book[p.name]['stages'].append({'name': s4.name, 'task': t4.name})

        # Add Stage to the Pipeline
        p.add_stages(s4)

        print book

    def func_on_false():

        print 'All iterations for Pipeline %s done' % instance

    # Create a Pipeline object
    p = Pipeline()
    p.name = 'em-%s' % instance

    # Create Stage 1
    s1 = Stage()
    s1.name = 'iter1-s1'

    # Create a Task
    t1 = Task()
    t1.name = 'iter1-s1-t1'


    global book
    book[p.name] = {
        'stages': [{'name': s1.name,
                    'task': t1.name}]}

    t1.pre_exec = ['module load python/2.7.7-anaconda']
    t1.executable = ['python']
    t1.arguments = ['analysis_1.py',
                    '--template', 'CB7G3_template.mdp',
                    '--newname', 'CB7G3_run.mdp',
                    '--wldelta', '2',
                    '--equilibrated', 'False',
                    '--lambda_state', '0',
                    '--seed', '%s' % SEED]
    t1.cores = 1
    t1.copy_input_data = [
        '$SHARED/CB7G3_template.mdp', '$SHARED/analysis_1.py']

    s1.post_exec = {
        'condition': func_condition,
        'on_true': func_on_true,
        'on_false': func_on_false
    }

    # Add the Task to the Stage
    s1.add_tasks(t1)

    # Add Stage to the Pipeline
    p.add_stages(s1)

    return p


if __name__ == '__main__':

    pipelines = set()

    for i in range(ENSEMBLE_SIZE):
        pipelines.add(get_pipeline(i, TOTAL_ITERS))

    total_cores = ENSEMBLE_SIZE*20

    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

        'resource': 'xsede.supermic',
        'walltime': 30,
        'cpus': total_cores,
        'project': 'TG-MCB090174',
        'access_schema': 'gsissh'
    }

    # Download analysis file from MobleyLab repo
    os.system('curl -O https://raw.githubusercontent.com/MobleyLab/alchemical-analysis/master/alchemical_analysis/alchemical_analysis.py')

    # Create Application Manager
    amgr = AppManager(port=33231, hostname='two.radical-project.org')
    amgr.resource_desc = res_dict

    # Assign resource manager to the Application Manager
    amgr.shared_data = ['./CB7G3.gro', './CB7G3.ndx', './CB7G3.top',
                        './CB7G3_template.mdp', './analysis_1.py',
                        './analysis_2.py', './determine_convergence.py',
                        './alchemical_analysis.py', './3atomtypes.itp',
                        './3_GMX.itp',
                        './cucurbit_7_uril_GMX.itp']

    # Assign the workflow as a set of Pipelines to the Application Manager
    amgr.workflow = pipelines

    # Run the Application Manager
    amgr.run()
