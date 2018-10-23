"""
.. module:: Template
   :synopsis: This module implements the Template class.
"""

# Third-party modules
import numpy as np


class Template:
    """
    .. class:: Template

      This class groups informations about a template sequence/structure.

    Attributes:
        name: Name of the template
        residues: Template's sequence of residues as list of Residues objects
        pdb: PDB filename of the template
    """

    def __init__(self, name, residues):
        self.name = name
        self.residues = residues
        self.pdb = None

    def set_pdb_name(self, metafold_dict):
        """
            Get the PDB file name of the current template from the template's name.

            Args:
                self: The current alignment's template.
                dictionary: A dictionary with key = template name and value = pdb file

            Returns:
                void
        """
        self.pdb = metafold_dict[self.name]

    def parse_pdb(self):
        """
            Parse the pdb file and set the CA coordinates.

            Args:
                void

            Returns:
                void

        """
        res_num = 0
        nb_gap = 0
        with open("data/pdb/" + self.name + "/" + self.pdb, 'r') as file:
            for line in file:
                line_type = line[0:6].strip()
                name_at = line[12:16].strip()
                if line_type == "ATOM" and name_at == "CA":
                    x_coord = float(line[30:38].strip())
                    y_coord = float(line[38:46].strip())
                    z_coord = float(line[46:54].strip())
                    # Skip gaps in the template
                    if res_num > len(self.residues):
                        break
                    while self.residues[res_num].name == "-":
                        nb_gap += 1
                        res_num += 1
                    self.residues[res_num].set_ca_coords(np.array([x_coord, y_coord, z_coord]))
                    res_num += 1
