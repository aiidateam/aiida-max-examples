#!/usr/bin/env runaiida
"""Run aiida examples

usage: ./run.py -c <aiida-code> -s <structure-label>
"""
from config import group_name
from aiida.common.exceptions import NotExistent


def load_example_structures():
    """ Read input structures into the database

    Structures are read from subfolder "example-structures"
    and stored in the group "example-structures".

    :return: group of available structures
    """
    from aiida.orm.group import Group
    
    try:
        group = Group.get(name=group_name)

    except NotExistent:
        import glob
        import os
        from ase.io import read
        from aiida.orm.data.structure import StructureData

        paths = glob.glob(group_name + '/*.cif')

        structure_nodes = []
        for path in paths:
            fname = os.path.basename(path)
            name = os.path.splitext(fname)[0]

            structure = StructureData(ase=read(path))
            if "ML" in name:
                # surface normal of monolayers should be oriented along z
                structure.set_pbc([True,True,False])
            else:
                structure.set_pbc([True,True,True])
            structure.label = name
            print("Storing {} in database".format(name))
            structure.store()
            structure_nodes.append(structure)
    
        group = Group(name=group_name)
        group.store()
        group.description = "\
        Set of atomic structures used by examples for AiiDA plugins of different codes"
        group.add_nodes(structure_nodes)
    
    return group



def parser_setup():
    """Set up parser for command line arguments.
    """
    import argparse
    parser = argparse.ArgumentParser(
        description='Run an example structure with a specified code',
    )

    parser.add_argument(
        '-c', type=str, required=True, dest='codename',
        help='name of AiiDA code to run'
    )

    group = load_example_structures()
    available_structures = ", ".join([n.label for n in group.nodes])
    parser.add_argument(
        '-s', default='TiO2', dest='structure',
        help='The structure to run. Available: {}'.format(available_structures),
    )

    parser.add_argument(
        '-k', nargs=3, type=int, default=[4, 4, 4], dest='kpoints', metavar='NK',
        help='define the k-point mesh. (default: %(default)s)'
    )

    #parser.add_argument(
    #    '-p', type=str, required=True, dest='pseudo_family',
    #    help='the name of pseudo family to use'
    #)

    parser.add_argument(
        '-w', type=int, default=1800, dest='max_wallclock_seconds', metavar='SEC',
        help='maximum wallclock time in seconds (default: %(default)d)'
    )

    return parser


def execute(args):
    """Check arguments and run code

    Determines which aiida plugin to use from the code specified.
    """
    from aiida.work.run import run
    from aiida.common.exceptions import NotExistent
    from aiida.orm.data.base import Int, Float, Str
    StructureData = DataFactory('structure')
    ParameterData = DataFactory('parameter')
    KpointsData = DataFactory('array.kpoints')

    # Get structure
    group = load_example_structures()
    labels = [ n.label for n in group.nodes]
    nodes = [ n for n in group.nodes]
    try:
        structure = nodes[ labels.index(args.structure) ]
    except ValueError:
        raise ValueError("Structure {} not found. Available structures: {}"\
            .format(args.structure, " , ".join(labels)))
    if not isinstance(structure, StructureData):
        raise ValueError("Node {} is not of type StructureData".format(structure.pk))
    print("Running example '{}'".format(args.structure))

    # Get k-points
    kpoints = KpointsData()
    kpoints.set_kpoints_mesh(args.kpoints)

    bandskpoints = KpointsData()
    bandskpoints.set_cell(structure.cell, structure.pbc)
    bandskpoints.set_kpoints_path(kpoint_distance = 0.05)
    bandskpoints.set_kpoints_path([
        ('G', 'X', 21),
        ('X', 'R', 31),
        ('R', 'Z', 21),
        ('Z', 'G', 31),
        ('G', 'M', 31),
        ('M', 'A', 31),
        ('A', 'Z', 31),
    ])

    # options
    options  = ParameterData(dict={
        'resources': {
            'num_machines': 1,
            "num_mpiprocs_per_machine": 1,
        },
        'max_wallclock_seconds': args.max_wallclock_seconds,
    })

    # Get aiida code
    code = Code.get_from_string(args.codename)
    print("Running code '{}'".format(args.codename))

    # Determine aiida plugin
    input_plugin = code.get_input_plugin_name()
    if 'siesta' in input_plugin:
        from siesta_input import workchain, kwargs
        
        kwargs.update({'structure' : structure,
                       'code' : code, 
                       'kpoints' : kpoints, 
                       'options' : options, 
                       'bandskpoints' : bandskpoints})

    elif 'fleur.fleur' in input_plugin:
        from fleur_input import workchain, prepare_scf_input
        
        kwargs = prepare_scf_input(kmesh=args.kpoints, options=options)
        kwargs.update({'fleur' : code, 
                       'inpgen' : Code.get_from_string('fleur-0.27-inpgen@localhost'),
                       'structure' : structure})
    else:
        print('The code you want to run is currently not supported by this script, sorry')
        return

    # newer aiida_core version needed for new verdi work list command
    # but at least that can be seen on the node level
    label = "{} on {}".format(workchain().__class__.__name__, structure.get_formula())
    description = "{} run with code {} on {}".format(
                        workchain().__class__.__name__, code.label, structure.get_formula())
    
    result = run(
        # general inputs
        workchain,
        _label=label,
        _description=description,
        **kwargs
    )

    return result



def cli():
    """Run command line interface
    """
    parser = parser_setup()
    args   = parser.parse_args()
    result = execute(args)


if __name__ == "__main__":
    cli()
