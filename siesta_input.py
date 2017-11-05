#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
from aiida.orm import Code, DataFactory
from aiida_siesta.workflows.base import SiestaBaseWorkChain as workchain
import aiida_siesta.data.psf as psf
from aiida.orm.data.base import Int, Str

ParameterData = DataFactory('parameter')
PsfData = DataFactory('siesta.psf')

block_pao_basis_content = """
Ti    5      1.91
n=3    0    1   E     93.95      5.20
5.69946662616249
1.00000000000000
n=3    1    1   E     95.47      5.20
5.69941339465994
1.00000000000000
n=4    0    2   E     96.47      5.60
6.09996398975307        5.09944363262274
1.00000000000000        1.00000000000000
n=3    2    2   E     46.05      4.95
5.94327035784617        4.70009988294302
1.00000000000000        1.00000000000000
n=4    1    1   E      0.50      1.77
3.05365979938936
1.00000000000000
O     3     -0.28
n=2    0    2   E     40.58      3.95
4.95272270428712        3.60331408800389
1.00000000000000        1.00000000000000
n=2    1    2   E     36.78      4.35
4.99990228025066        3.89745395068600
1.00000000000000        1.00000000000000
n=3    2    1   E     21.69      0.93
2.73276990670788
1.00000000000000
"""

parameters = ParameterData(dict= {
    'xc-functional': 'GGA',
    'xc-authors': 'PBE',
    'spin-polarized': False,
    'meshcutoff': '200 Ry',
    'dm-numberpulay': 4,
    'dm-mixingweight': 0.3,
    'dm-tolerance': 1.e-4,
    'electronic-temperature': '25 meV',
    'max-scfiterations': 10,
    'scf-must-converge': True,
    'geometry-must-converge': True,
    'Solution-method': 'diagon',
    'md-maxcgsteps': 8,
    'md-maxcgdispl': '0.1 Ang',
    'md-maxforcetol': '0.02 eV/Ang',
    'writeforces': True,
    'writecoorstep': True,
    'xml:write': True,
})

settings = ParameterData(dict= {})

# default basis
basis = ParameterData(dict={
    # 'pao-energy-shift': '100 meV',
    # '%block pao-basis-sizes': """
    # Si DZP                    """,
    '%block pao-basis': block_pao_basis_content,
})


max_iterations=Int(5)


# upload pseudos
folder = './siesta-files'
pseudo_family = 'example-siesta-pps'
pseudo_family_desc = "Siesta Pseudopotentials for example structures"

files_found, files_uploaded = psf.upload_psf_family(
    folder, pseudo_family, pseudo_family_desc, stop_if_existing=False)
pseudo_family = Str('example-siesta-pps')

print("PSF files found: {}. New files uploaded: {}").format(
    files_found, files_uploaded)

# kwargs
kwargs = {}
for name in ('pseudo_family', 'parameters', 'settings', 'basis'):
    kwargs[name] = locals()[name]
