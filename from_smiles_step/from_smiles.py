# -*- coding: utf-8 -*-
"""a node to create a structure from a SMILES string"""

import molssi_util
import molssi_workflow
import molssi_workflow.data
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
        self.minimize = False
        self.ff = 'UFF'

    def describe(self, indent='', json_dict=None):
        """Write out information about what this node will do
        If json_dict is passed in, add information to that dictionary
        so that it can be written out by the controller as appropriate.
        """

        next_node = super().describe(indent, json_dict)

        indent += '    '
        if self.smiles_string[0] == '$':
            string = indent + (
                "Create the structure from the SMILES in the variable"
                " '{smiles}'"
            )
        else:
            string = indent + (
                "Create the structure from the SMILES '{smiles}'"
            )
            
        self.job_output(
            string.format(
                smiles=self.smiles_string
            )
        )
        self.job_output('')

        return next_node

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

        Equivalent command line is like: ::
            echo 'CCO' | obabel --gen3d -ismi -omol | obabel -imol -osmi -xh\
                  | obabel --gen3d -ismi -opcjson
        """

        next_node = super().run()

        if self.smiles_string is None:
            return None

        local = molssi_workflow.ExecLocal()
        smiles = self.get_value(self.smiles_string)

        # Print what we are doing
        string = (
            "    Creating the structure from the SMILES '{smiles}'"
        )
        self.log(
            string.format(
                smiles=smiles
            )
        )

        result = local.run(
            cmd=['obabel', '--gen3d', '-ismi', '-omol'],
            input_data=smiles
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            molssi_workflow.data.structure = None
            return None

        logger.debug('***Intermediate molfile from obabel')
        logger.debug(result['stdout'])

        mol = result['stdout']
        result = local.run(
            cmd=['obabel', '-imol', '-osmi', '-xh'],
            input_data=mol
        )

        logger.log(0, pprint.pformat(result))

        if int(result['stderr'].split()[0]) == 0:
            molssi_workflow.data.structure = None
            return None

        smiles = result['stdout']
        logger.debug('***smiles with Hs from obabel')
        logger.debug(smiles)

        if self.minimize:
            # from SMILES to mol2
            result = local.run(
                cmd=['obabel', '--gen3d', '-ismi', '-omol2'],
                input_data=smiles
            )

            # logger.log(0, pprint.pformat(result))
            logger.debug('***Intermediate mol2 file from obabel')
            logger.debug(result['stdout'])

            if int(result['stderr'].split()[0]) == 0:
                molssi_workflow.data.structure = None
                return None

            files = {}
            files['input.mol2'] = result['stdout']
            
            # minimize
            result = local.run(
                cmd=['obminimize', '-o', 'mol2',
                     '-ff', self.ff, 'input.mol2'],
                files=files
            )

            # logger.log(0, pprint.pformat(result))
            logger.debug('***Intermediate mol2 from obminimize')
            logger.debug(result['stdout'])
            mol2 = result['stdout']

            result = local.run(
                cmd=['obabel', '-imol2', '-omol', '-x3'],
                input_data=mol2
            )
            if int(result['stderr'].split()[0]) == 0:
                molssi_workflow.data.structure = None
                return None

            structure = molssi_util.molfile.to_molssi(result['stdout'])
        else:
            result = local.run(
                cmd=['obabel', '--gen3d', '-ismi', '-omol', '-x3'],
                input_data=smiles
            )

            logger.log(0, pprint.pformat(result))

            if int(result['stderr'].split()[0]) == 0:
                molssi_workflow.data.structure = None
                return None

            logger.debug('***Structure from obabel')
            logger.debug(result['stdout'])

            structure = molssi_util.molfile.to_molssi(result['stdout'])

        structure['periodicity'] = 0
        # atoms['ids'] = data_in['aid']
        units = structure['units'] = {}
        units['coordinates'] = 'angstrom'

        molssi_workflow.data.structure = structure

        logger.debug('\n***Structure dict')
        logger.debug(pprint.pformat(structure))

        # Finish the output
        string = (
            "    Created a molecular structure with {n_atoms} atoms."
        )
        self.log(
            string.format(
                n_atoms=len(structure['atoms']['elements'])
            )
        )
        
        self.log('')
        return next_node
