# -*- coding: utf-8 -*-
"""Control parameters for generating a structure from SMILES
"""

import logging
import molssi_workflow
import pprint

logger = logging.getLogger(__name__)


class FromSMILES_Parameters(molssi_workflow.Parameters):
    """The control parameters for creating a structure from SMILES"""

    parameters = {
        "smiles string": {
            "default": "",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "s",
            "description": "SMILES:",
            "help_text": ("The SMILES string for the structure.")
        },
        "minimize": {
            "default": "no",
            "kind": "boelan",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "s",
            "description": "Minimize the structure:",
            "help_text": ("Whether to minimize the structure using one "
                          "of the forcefields supported by OpenBabel.")
        },
        "forcefield": {
            "default": "UFF",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": ("UFF", "GAFF", "MMFF94", "MMFF94s", "Ghemical"),
            "format_string": "s",
            "description": "Forcefield:",
            "help_text": ("The forcefield to use when minimizing the "
                          "structure.")
        },
    }

    def __init__(self, data=parameters):
        """Initialize the instance, by default from the default
        parameters given in the class"""

        logger.debug('FromSMILES_Parameters.__init__')

        super().__init__()

        logger.debug("Initializing FromSMILES_Parameters object:")
        logger.debug("\n{}\n".format(pprint.pformat(data)))

        self.update(data)
