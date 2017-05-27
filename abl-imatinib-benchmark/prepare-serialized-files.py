#!/bin/env python
"""
Prepare serialized OpenMM System, State, and Integrator for simulating a kinase.

"""
from simtk.openmm import app
from simtk import unit, openmm
import time, os, sys

def serialize_everything(simulation, basename, sysname = '-system.xml', statename='-state.xml', intgname='-integrator.xml'):
    """Serialize the state, system and integrator from a Simulation object."""
    xmls = openmm.XmlSerializer

    box_vectors = simulation.context.getState().getPeriodicBoxVectors()
    simulation.system.setDefaultPeriodicBoxVectors(*box_vectors)

    sysxml = xmls.serialize(simulation.system)
    statexml = xmls.serialize(simulation.context.getState(getPositions=True, getVelocities=True))
    intgxml = xmls.serialize(simulation.integrator)

    with open("{0}{1}".format(basename,sysname),'w') as sysfile:
        sysfile.write(sysxml)

    with open("{0}{1}".format(basename,statename),'w') as statefile:
        statefile.write(statexml)

    with open("{0}{1}".format(basename,intgname),'w') as intgfile:
        intgfile.write(intgxml)


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

class AblImatinibExplicit(object):
    """
    Abl:imatinib in explicit solvent.

    """
    def __init__(self, **kwargs):
        self.temperature = 300 * unit.kelvin
        self.pressure = 1.0 * unit.atmospheres

        padding = 9.0*unit.angstrom
        explicit_solvent_model = 'tip3p'
        setup_path = 'data/abl-imatinib'

        # Create topology, positions, and system.
        gaff_xml_filename = 'data/gaff.xml'
        imatinib_xml_filename = 'data/abl-imatinib/imatinib.xml'
        ffxmls = [gaff_xml_filename, imatinib_xml_filename, 'amber99sbildn.xml', 'tip3p.xml']
        forcefield_kwargs = { 'nonbondedMethod' : app.PME, 'nonbondedCutoff' : 9.0 * unit.angstrom, 'implicitSolvent' : None, 'constraints' : app.HBonds, 'rigidWater' : True }

        # Load topologies and positions for all components
        print('Creating Abl:imatinib test system...')
        forcefield = app.ForceField(*ffxmls)
        from simtk.openmm.app import PDBFile, Modeller
        pdb_filename = os.path.join(setup_path, '%s.pdb' % 'complex')
        pdbfile = PDBFile(pdb_filename)
        modeller = app.Modeller(pdbfile.topology, pdbfile.positions)
        print('Adding solvent...')
        initial_time = time.time()
        modeller.addSolvent(forcefield, model=explicit_solvent_model, padding=padding)
        final_time = time.time()
        elapsed_time = final_time - initial_time
        nadded = (len(modeller.positions) - len(pdbfile.positions)) / 3
        print('Adding solvent took %.3f s (%d molecules added)' % (elapsed_time, nadded))
        self.topology = modeller.getTopology()
        self.positions = modeller.getPositions()
        print('Creating system...')
        self.system = forcefield.createSystem(self.topology, **forcefield_kwargs)

        # Add a barostat
        barostat = openmm.MonteCarloBarostat(self.pressure, self.temperature)
        self.system.addForce(barostat)

        self.alchemical_atoms = range(4266,4335) # Abl:imatinib
        self.description = 'Abl:imatinib in explicit solvent alchemical free energy calculation'

if __name__ == "__main__":

    # Create test system
    testsystem = AblImatinibExplicit()

    # Create integrator.    
    collision_rate = 90 / unit.picoseconds
    timestep = 2.0 * unit.femtoseconds
    nsteps = 10000
    integrator = openmm.LangevinIntegrator(testsystem.temperature, collision_rate, timestep)

    simulation = app.Simulation(testsystem.topology, testsystem.system, integrator)
    simulation.reporters.append(app.StateDataReporter(sys.stdout, 1000, step=True, potentialEnergy=True, temperature=True, volume=True))
    simulation.context.setPositions(testsystem.positions)
    print('Minimizing...')
    simulation.minimizeEnergy()
    print('Equilibrating...')
    simulation.step(nsteps)
    print('Serializing...')
    serialize_everything(simulation, 'serialized/abl-imatinib')

