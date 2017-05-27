#!/bin/env python

"""
Benchmark performance on a kinase:inhibitor system.

"""

from simtk.openmm import app
from simtk import unit, openmm
import time, os, sys

def deserialize_simulation(basename, sysname = '-system.xml', statename='-state.xml', intgname='-integrator.xml'):

    xmls = openmm.XmlSerializer

    with open("{0}{1}".format(basename,sysname),'r') as sysfile:
        sysxml = sysfile.read()
        system = xmls.deserialize(sysxml)

    with open("{0}{1}".format(basename,statename),'r') as statefile:
        statexml = statefile.read()
        state = xmls.deserialize(statexml)

    with open("{0}{1}".format(basename,intgname),'r') as intgfile:
        intgxml = intgfile.read()
        integrator = xmls.deserialize(intgxml)

    context = openmm.Context(system, integrator)
    context.setPositions(state.getPositions(asNumpy=True))
    context.setVelocities(state.getVelocities(asNumpy=True))

    return context, integrator, system, state


if __name__ == '__main__':
    # Deserialize classes and create a context.
    print('Deserializing simulation...')
    [context, integrator, system, state] = deserialize_simulation('serialized/abl-imatinib')
    print('System contains %d atoms.' % system.getNumParticles())
    print('Using platform "%s".' % context.getPlatform().getName())    
    print('Initial potential energy is %.3f kcal/mol' % (context.getState(getEnergy=True).getPotentialEnergy() / unit.kilocalories_per_mole))

    # Warm up the integrator to compile kernels, etc
    print('Warming up integrator to trigger kernel compilation...')
    integrator.step(10)

    # Time integration
    print('Benchmarking...')
    nsteps = 5000
    timestep = integrator.getStepSize()
    initial_time = time.time()
    integrator.step(nsteps)
    final_time = time.time()
    elapsed_time = (final_time - initial_time) * unit.seconds
    simulated_time = nsteps * timestep
    performance = (simulated_time / elapsed_time)
    print('completed %8d steps in %8.3f s : performance is %8.3f ns/day' % (nsteps, elapsed_time / unit.seconds, performance / (unit.nanoseconds/unit.day)))
    print('Final potential energy is %.3f kcal/mol' % (context.getState(getEnergy=True).getPotentialEnergy() / unit.kilocalories_per_mole))
