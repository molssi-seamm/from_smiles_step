# -*- coding: utf-8 -*-
"""a node to create a structure from a SMILES string"""

import molssi_workflow
import molssi_workflow.data
import json
import logging
import pprint

logger = logging.getLogger(__name__)


class FromSMILES(molssi_workflow.Node):
    def __init__(self, workflow=None, extension=None):
        '''Initialize a specialized start node, which is the
        anchor for the graph.

        Keyword arguments:
        '''
        logger.debug('Creating FromSMILESNode {}'.format(self))

        super().__init__(workflow=workflow, title='from SMILES',
                         extension=extension)

        self.smiles_string = ''

    def run(self):
        """Create 3-D structure from a SMILES string

        The atom ordering is a problem, since SMILES keeps hydrogens
        implicitly, so they tend to be added after the heavy atoms. If
        we keep them explicitly, for instance by tricking SMILES by
        using At for H, then the atom order is changed, which is not
        good.

        To avoid this we will use explict H's (labeled as At's). Since
        OpenBabel will not directly convert SMILES to SMILES with
        explicit H's, we use a molfile as an intermediate.

        Equivalent command line: ::
            echo 'CCO' | obabel --gen3d -ismi -omol | obabel -imol -osmi -xh | obabel --gen3d -ismi -opcjson
        """  # nopep8

        if self.smiles_string is None:
            return None

        # p = subprocess.run(
        #     ['obabel', '--gen3d', '-ismi', '-opcjson'],
        #     input=self.smiles_string,
        #     universal_newlines=True,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE)

        local = molssi_workflow.ExecLocal()

        result = local.run(
            cmd=['obabel', '--gen3d', '-ismi', '-omol'],
            input_data=self.smiles_string
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            molssi_workflow.data.structure = None
            return None

        logger.debug('***Intermediate molfile from obabel')
        logger.debug(result['stdout'])

        molfile = result['stdout']
        result = local.run(
            cmd=['obabel', '-imol', '-osmi', '-xh'],
            input_data=molfile
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            molssi_workflow.data.structure = None
            return None

        smiles = result['stdout']
        logger.debug('***smiles with Hs from obabel')
        logger.debug(smiles)

        result = local.run(
            cmd=['obabel', '--gen3d', '-ismi', '-opcjson'],
            input_data=smiles
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            molssi_workflow.data.structure = None
            return None

        logger.debug('***Structure from obabel')
        logger.debug(result['stdout'])

        tmp_data = json.loads(result['stdout'])
        tmp = tmp_data['PC_Compounds'][0]

        structure = molssi_workflow.data.structure = {}
        structure['periodicity'] = 0
        atoms = structure['atoms'] = {}
        data_in = tmp['atoms']
        atoms['ids'] = data_in['aid']
        elements = atoms['elements'] = []
        for el in data_in['element']:
            elements.append(el.title())

        coordinates = atoms['coordinates'] = []
        data_in = tmp['coords'][0]['conformers'][0]
        for x, y, z in zip(data_in['x'], data_in['y'], data_in['z']):
            coordinates.append((x, y, z))
        units = structure['units'] = {}
        units['coordinates'] = 'angstrom'

        bonds = structure['bonds'] = []
        if 'bonds' in tmp:
            data_in = tmp['bonds']
            for i, j, order in zip(data_in['aid1'], data_in['aid2'],
                                   data_in['order']):
                bonds.append((i, j, order))

        logger.debug('\n***Structure dict')
        logger.debug(pprint.pformat(structure))

        return super().run()
