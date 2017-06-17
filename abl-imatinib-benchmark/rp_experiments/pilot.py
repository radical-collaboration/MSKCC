#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import sys

verbose  = os.environ.get('RADICAL_PILOT_VERBOSE', 'REPORT')
os.environ['RADICAL_PILOT_VERBOSE'] = verbose

import radical.pilot as rp
import radical.utils as ru


# ------------------------------------------------------------------------------
#
# READ the RADICAL-Pilot documentation: http://radicalpilot.readthedocs.org/
#
# ------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # we use a reporter class for nicer output
    report = ru.LogReporter(name='radical.pilot', level=verbose)
    report.title('Getting Started (RP version %s)' % rp.version)

    # use the resource specified as argument, fall back to localhost
    if   len(sys.argv)  > 2: report.exit('Usage:\t%s [resource]\n\n' % sys.argv[0])
    elif len(sys.argv) == 2: resource = sys.argv[1]
    else                   : resource = 'local.localhost'

    # Create a new session. No need to try/except this: if session creation
    # fails, there is not much we can do anyways...
    session = rp.Session()

    # all other pilot code is now tried/excepted.  If an exception is caught, we
    # can rely on the session object to exist and be valid, and we can thus tear
    # the whole RP stack down via a 'session.close()' call in the 'finally'
    # clause...
    try:

        report.header('submit pilots')

        # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
        pmgr = rp.PilotManager(session=session)

        # Define an [n]-core local pilot that runs for [x] minutes
        # Here we use a dict to initialize the description object
        pd_init = {
                'resource'      : "ornl.titan_ortelib",
                'runtime'       : 15,  # pilot runtime (min)
                'exit_on_error' : True,
                'project'       : "CSC230",
                'queue'         : "debug",
                'access_schema' : "local",
                'cores'         : 16,
                }
        pdesc = rp.ComputePilotDescription(pd_init)

        # Launch the pilot.
        pilot = pmgr.submit_pilots(pdesc)


        # Synchronously stage the data to the pilot
        report.info('stage shared data')
        pilot.stage_in({'source': 'client:///benchmark.py',
                        'target': 'pilot:///benchmark.py',
                        'action': rp.TRANSFER})
        report.ok('>>ok\n')


        report.header('submit units')

        # Register the ComputePilot in a UnitManager object.
        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n = 10   # number of units to run
        report.info('create %d unit description(s)\n\t' % n)

        cuds = list()
        for i in range(0, n):

            # create a new CU description, and fill it.
            # Here we don't use dict initialization.
            cud = rp.ComputeUnitDescription()
            cud.executable     = "python"
            cud.pre_exec       = ["module load python_anaconda","module load cudatoolkit","export PATH=/ccs/proj/csc230/mskcc/miniconda/bin:$PATH","export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/ccs/proj/csc230/mskcc/miniconda/lib","export PYTHONPATH=$PYTHONPATH:/ccs/proj/csc230/mskcc/miniconda/lib/python2.7/site-packages/","PYTHONPATH=$PYTHONPATH:/sw/xk6/python_anaconda/2.3.0/sles11.3_gnu4.8.2/lib/python2.7/site-packages/","export OPENMM_CUDA_COMPILER=/opt/nvidia/cudatoolkit7.5/7.5.18-1.0502.10743.2.1/bin/nvcc","source /ccs/proj/csc230/mskcc/miniconda/envs/venv/bin/activate"]

            cud.arguments      = ["benchmark.py"]
            cud.input_staging  = {'source': 'pilot:///benchmark.py', 
                                  'target': 'unit:///benchmark.py',
                                  'action': rp.LINK}
            cuds.append(cud)
            report.progress()
        report.ok('>>ok\n')

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        units = umgr.submit_units(cuds)

        # Wait for all compute units to reach a final state (DONE, CANCELED or FAILED).
        report.header('gather results')
        umgr.wait_units()
    
        report.info('\n')
        for unit in units:
            report.plain('  * %s: %s, exit: %3s, out: %s\n' \
                    % (unit.uid, unit.state[:4], 
                        unit.exit_code, unit.stdout.strip()[:35]))
    


  # except Exception as e:
  #     # Something unexpected happened in the pilot code above
  #     report.error('caught Exception: %s\n' % e)
  #     raise 
  #
  # except (KeyboardInterrupt, SystemExit) as e:
  #     # the callback called sys.exit(), and we can here catch the
  #     # corresponding KeyboardInterrupt exception for shutdown.  We also catch
  #     # SystemExit (which gets raised if the main threads exits for some other
  #     # reason).
  #     report.warn('exit requested\n')

    finally:
        # always clean up the session, no matter if we caught an exception or
        # not.  This will kill all remaining pilots.
        report.header('finalize')
        session.close()

    report.header()

