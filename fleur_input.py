#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
from aiida.orm import Code, DataFactory
from aiida_fleur.workflows.scf import fleur_scf_wc as workchain

ParameterData = DataFactory('parameter')

def prepare_scf_input(kmesh=[4,4,4], options=ParameterData(dict={})):
    """
    prepares the input for fleur scf
    """             
    options_dict = options.get_dict()
    max_wallclock = options_dict.get('max_wallclock_seconds', 600)
    resources = options_dict.get('resources', {"num_machines" : 1})

    wc_parameters = ParameterData(dict={'fleur_runmax': 4, 
                                        'resources' : resources,#{"num_machines": 1},#{"tot_num_mpiprocs": 24},
                                        'walltime_sec':  max_wallclock,
                                        'queue_name' : 'batch',
                                        'serial' : True,
                                        'custom_scheduler_commands' : ''})                                                                                                    
    # we are using the defaults
    calc_para = ParameterData(dict={u'kpt': {u'tkb' : 0.001, 
                                            u'div1' : kmesh[0],
                                            u'div2' :  kmesh[1],
                                            u'div3' : kmesh[2]}})
    '''
    #for TiO2 good parameters, without lda+U are: (with soc)
    ## LDA+U on Ti &ldaU l=2, u=5.5, j=0.5, l_amf=F /

    #ti_o_fleur_parameter 
    calc_para = ParameterData(dict={
        u'comp': {u'kmax': 4.2, u'gmaxxc': 11.5, u'gmax': 13.9}, 
        u'atom': {u'lmax': 8, u'lnonsph': 6, u'jri': 551, u'rmt': 2.2, u'dx': 0.021, 
                  u'element': u'Ti', u'lo': u'2p'}, 
        u'atom2': {u'element': u'O', u'jri': 311, u'dx': 0.033, u'lmax': 6, u'lnonsph': 4,
                   u'rmt': 1.2},
        u'soc' : {'theta' : 0.0, 'phi' : 0.0},
        u'kpt': {u'tkb': 0.001, u'div1' : 4, u'div2' : 4, u'div3' : 2}, 
        u'title': u'TiO2, rutile bulk'})
    
    # for MoS reasonable parameters are: (with soc and magnetism)
    #mos2_fleur_parameter 
    calc_para = ParameterData(dict={
         u'comp': {u'kmax': 3.8, u'gmaxxc': 10.5, u'gmax': 12.6, u'jspins' : 2.0}, 
                   # dvac : 14.05000000 # bohr
         u'atom': {u'lmax': 10, u'lnonsph': 8, u'jri': 803, u'dx': 0.015, u'rmt': 2.43, 
                             u'element': u'Mo'}, 
         u'atom2': {u'element': u'S', u'jri': 629, u'lmax': 8, u'lnonsph': 6,                                          u'rmt': 1.9, u'dx': 0.018}, 
        u'soc' : {'theta' : 0.0, 'phi' : 0.0},
        u'kpt': {u'tkb': 0.001, u'div1' : 4 , u'div2' :  4 , u'div3' : 1}, 
        u'title': u'MoS2, 2L monolayer slab'})
    '''

    input_dict={'wf_parameters' : wc_parameters, 'calc_parameters' : calc_para}
    
    return input_dict
