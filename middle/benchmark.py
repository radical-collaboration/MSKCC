#!/bin/env python

"""
Benchmark performance on a kinase:inhibitor system.

"""

from simtk.openmm import app
from simtk import unit, openmm
import time, os, sys

def read_namd_input(prmtop_filename, pdb_filename):
    """
    Read NAMD input files and create an OpenMM Context.

    Parameters
    ----------
    prmtop_filename : str
        AMBER parameter filename
    pdb_filename : str
        PDB filename

    Returns
    -------
    context : simtk.openmm.Context
        OpenMM Context
    integrator : simtk.openmm.Integrator
        OpenMM Integrator
    system : simtk.openmm.System
        OpenMM System

    """

    prmtop = app.AmberPrmtopFile(prmtop_filename)
    system = prmtop.createSystem(nonbondedMethod=app.PME, nonbondedCutoff=10*unit.angstroms, constraints=app.HBonds)
    pdbfile = app.PDBFile(pdb_filename)

    temperature = 300 * unit.kelvin
    collision_rate = 90 / unit.picoseconds
    timestep = 2.0 * unit.femtoseconds

    integrator = openmm.LangevinIntegrator(temperature, collision_rate, timestep)

    context = openmm.Context(system, integrator)
    context.setPositions(pdbfile.getPositions(asNumpy=True))
    context.setVelocitiesToTemperature(temperature)

    # Minimize
    print('Minimizing...')
    openmm.LocalEnergyMinimizer.minimize(context)

    return context, integrator, system


if __name__ == '__main__':
    # Deserialize classes and create a context.
    print('Loading simulation...')
    [context, integrator, system] = read_namd_input('complex.top', 'complex.pdb')
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
