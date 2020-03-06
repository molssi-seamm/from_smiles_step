# -*- coding: utf-8 -*-

"""The graphical part of a fromSMILES node"""

import from_smiles_step
import seamm
import seamm_widgets as sw
import tkinter as tk


class TkFromSMILES(seamm.TkNode):
    """The graphical part of the From SMILES step
    """

    def __init__(self, canvas=None, x=120, y=20, w=200, h=50):
        """Initialize the From SMILES graphical node.

        Keyword arguments:
        """
        super().__init__(
            canvas=canvas, x=x, y=y, w=w, h=h, title='From SMILES'
        )
        self.parameters = from_smiles_step.FromSMILESParameters()

    @property
    def version(self):
        """The semantic version of this module.
        """
        return from_smiles_step.__version__

    @property
    def git_revision(self):
        """The git version of this module.
        """
        return from_smiles_step.__git_revision__

    def create_dialog(self):
        """Create a dialog for editing the SMILES string
        """
        frame = super().create_dialog('Edit SMILES Step')

        # Create the widgets and grid them in
        P = self.parameters
        row = 0
        widgets = []
        for key in P:
            self[key] = P[key].widget(frame)
            widgets.append(self[key])
            self[key].grid(row=row, column=0, sticky=tk.EW)
            row += 1

        sw.align_labels(widgets)
