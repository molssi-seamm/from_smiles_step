# -*- coding: utf-8 -*-
"""Control parameters for generating a structure from SMILES
"""

import logging
import seamm

logger = logging.getLogger(__name__)


class FromSMILESParameters(seamm.Parameters):
    """The control parameters for creating a structure from SMILES"""

    parameters = {
        "smiles string": {
            "default": "",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "s",
            "description": "SMILES:",
            "help_text": ("The SMILES string for the structure."),
        },
        "handling": {
            "default": "Overwrite the current configuration",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "Overwrite the current configuration",
                "Create a new configuration",
                "Create a new system and configuration",
            ),
            "format_string": "s",
            "description": "",
            "help_text": "Whether to overwrite or create a new system or configuration",
        },
        "system name": {
            "default": "use SMILES string",
            "kind": "string",
            "default_units": "",
            "enumeration": (
                "keep current name",
                "use SMILES string",
                "use Canonical SMILES string",
            ),
            "format_string": "s",
            "description": "System name:",
            "help_text": "The name for the new system",
        },
        "configuration name": {
            "default": "use SMILES string",
            "kind": "string",
            "default_units": "",
            "enumeration": (
                "keep current name",
                "use SMILES string",
                "use Canonical SMILES string",
            ),
            "format_string": "s",
            "description": "Configuration name:",
            "help_text": "The name for the new configuration",
        },
    }

    def __init__(self, defaults={}, data=None):
        """Initialize the instance, by default from the default
        parameters given in the class"""

        super().__init__(
            defaults={**FromSMILESParameters.parameters, **defaults}, data=data
        )
