"""
    .. module:: threading
      :synopsis: This module implements all the functions to make the threading of
                 the query sequence on the templates.
"""

# Third-party modules
import numpy as np

def display_matrix(matrix):
    """
        Display the distance matrix in the terminal.

        Args:
            matrix (numpy ndarray): Matrix of shape query_length * query_length
                                    containing distances and gaps represented as
                                    "*".

        Returns:
            void
    """
    rows = matrix.shape[0]
    cols = matrix.shape[1]
    for i in range(0, rows):
        for j in range(0, cols):
            if (matrix[i][j] == "*"):
                print("{:^4s}".format(matrix[i][j]), end="")
            else:
                print("{:4.1f}".format(matrix[i][j]), end="")
        print("\n")
    print("\n\n")


def calc_dist_matrix(query, template, dist_range):
    """
        Calculate the matrix of distances of pair residues of the query sequence,
        using the coordinates of the template sequence: threading of the query
        on the template sequence. The distance calculation is optimized.

        Args:
            query (list of Residue): List of residues of the query sequence
            template (list of Residue): List of residues of the template sequence
            dist_range (list of int): Range of distances in angströms.
                        Distances within this range only are taken into account

        Returns:
            2D numpy matrix: The distance matrix between pairs of residues of the
            query sequence after being threaded on the template sequence.
    """

    query_size = len(query)
    # This matrix holds distances and gaps ("*") for all pairs of residues of
    # the query sequence after being threaded on the template sequence
    matrix = np.full((query_size, query_size), fill_value=np.inf, dtype=object)
    # The distance matrix is symmetric so we make the calculations only for
    # the upper right triangular matrix. This saves have computation time.
    # And we do not calculate distances between bonded residues and between
    # themselves so the 2nd loop starts at i+2
    for i in range(len(query)):
        row_res = query[i]
        if row_res.name == "-" or template[i].name == "-":
            matrix[i, (i+2):] = "*"
            break
        for j in range(i+2, len(query)):
            col_res = query[j]
            # A gap represented by "-" = no distance calculation.
            # The whole line / row in the matrix will necessarily be "*"
            # This saves computation time
            if col_res.name == "-" or template[j].name == "-":
                matrix[:i, j] = "*"
                break
            # One of the most efficient method to calculate the distances.
            # https://stackoverflow.com/a/47775357/6401758
            # distance = sqrt((xa-xb)**2 + (ya-yb)**2 + (za-zb)**2)
            #print(template[i].name,template[i].ca_coords,template[j].ca_coords,template[j].name)
            dist = np.linalg.norm(template[i].ca_coords - template[j].ca_coords)
            # Keep distances only in a defined range because we don't want to
            # take into account directly bonded residues (dist < ~5 A) and too far residues
            if dist_range[0] <= dist <= dist_range[1]:
                matrix[i, j] = dist
    return matrix


    def convert_dist_to_energy(dist_matrix, dist_position_dict, dope_df):
        """
            Convert the distance between residues to energy values based on
            dope score table.

            Args:
                dist_matrix (numpy 2D array): 2D matrix containing distances between
                                              pairs of residues of the query sequence
                                              threaded on the template.

                dist_position_dict (Dictionary): Dictionary containing as key a tuple of coord (i,j)
                                                 describing the coords of residues associated (res1, res2)
                                                 as values.

                dope_df (panda DataFrame):    DataFrame (20x20) containing a list of
                                              30 energy values for 30 interval of
                                              distances between 0.25 to 15 with a step
                                              of 0.50
            Returns:
                numpy 2D array:  2D matrix containing energy between
                                 pairs of residues of the query sequence
                                 threaded on the template.
        """
        #size of the dist_matrix (ncol ~ nrow)
        size = shape(dist_matrix)[0]
        for i in range(size):
            for j in range(size):
                tuple_residues = dist_position_dict[(i,j)]
                round_value = round((dist_matrix[i,j] * 30) / 15)
                dist_matrix[i,j] = dope_df[tuple_residues[0]][tuple_residues[1]][round_value]

        return dist_matrix
