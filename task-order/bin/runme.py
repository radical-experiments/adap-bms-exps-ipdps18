from radical.entk import Pipeline, Stage, Task, AppManager
import os, sys
from random import shuffle

# ------------------------------------------------------------------------------
# Set default verbosity

if not os.environ.get('RADICAL_ENTK_VERBOSE'):
    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'


CUR_TASKS=16
CUR_CORES=16
CUR_NEW_STAGE=0
MAX_NEW_STAGE=None
duration=60

def generate_pipeline():

    global CUR_TASKS, CUR_CORES, duration, MAX_NEW_STAGE

    def func_condition():

        global CUR_NEW_STAGE, MAX_NEW_STAGE

        if CUR_NEW_STAGE < MAX_NEW_STAGE:
            return True

        return False

    def func_on_true():

        global CUR_NEW_STAGE
        CUR_NEW_STAGE += 1

        for t in p.stages[CUR_NEW_STAGE].tasks:
            cores = randint(1,16)
            t.arguments = ['-c', str(cores), '-t', str(duration)]

    def func_on_false():
        print 'Done'

    # Create a Pipeline object
    p = Pipeline()

    for s in range(MAX_NEW_STAGE+1):

        # Create a Stage object
        s1 = Stage()

        for i in range(CUR_TASKS):

            t1 = Task()
            t1.pre_exec = ['export PATH=/u/sciteam/balasubr/modules/stress-ng-0.09.34:$PATH']
            t1.executable = ['stress-ng']
            t1.arguments = [ '-c', str(CUR_CORES), '-t', str(duration)]
            t1.cpu_reqs = {
                            'processes': 1,
                            'process_type': '',
                            'threads_per_process': CUR_CORES,
                            'thread_type': ''
                        }

            # Add the Task to the Stage
            s1.add_tasks(t1)

        # Add post-exec to the Stage
        s1.post_exec = {
                           'condition': func_condition,
                           'on_true': func_on_true,
                           'on_false': func_on_false
                       }

        # Add Stage to the Pipeline
        p.add_stages(s1)

    return p

if __name__ == '__main__':

    MAX_NEW_STAGE = int(sys.argv[1])
    print 'MAX STAGE: ',MAX_NEW_STAGE

    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

            'resource': 'ncsa.bw_orte',
            'walltime': MAX_NEW_STAGE+1+30,
            'cpus': CUR_TASKS*CUR_CORES+32,
            'project': 'bamm',
            'queue': 'high',
            'access_schema': 'gsissh',
    }


    # Create Application Manager
    appman = AppManager(port=33154)
    appman.resource_desc = res_dict

    p = generate_pipeline()

    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.workflow = [p]

    # Run the Application Manager
    appman.run()
