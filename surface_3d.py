from object_3d import Object3D
import numpy as np

class CheckerBoard(Object3D):
    
    def __init__(self, render, board_size, cell_size, cell_color):
        super().__init__(render)

        self.faces_enabled = True

        self.edge_color = cell_color

        self.vertices = np.empty([0, 4])
        self.faces = np.empty([0, 4], dtype=np.int32)

        # Each cell in the checkerboard has 4 vertices and makes up one face.
        # Number of cols per row
        n_rows = int(board_size[0] / cell_size[0])
        # number of columns of cells
        n_cols = int(board_size[1] / cell_size[1])

        # Helps constructing the np.array for the vertice, which is quite verbose
        def cell_vertices(r, c, offsets, cell_size):
            return np.array([(
                (r + offsets[0]) * cell_size[0],
                (c + offsets[1]) * cell_size[1],
                0, 
                1
            )], dtype=np.float64)

        # Assume only even-numbered rows and columns. Create cells in pars (2*2 diagonal)
        for r in range(0, n_rows, 2):
            for c in range(0, n_cols, 2):
                
                cell_offsets = [
                    [(0, 0), (0, 1), (1, 1), (1, 0)],
                    [(1, 1), (1, 2), (2, 2), (2, 1)]
                ]
                for v_offsets in cell_offsets:
                    for v_offset in v_offsets:
                        self.vertices = np.concatenate(
                            (self.vertices, cell_vertices(r, c, v_offset, cell_size))
                        )

                    # Construct a face from the vertix indices of the last cell
                    v_len = len(self.vertices)
                    self.faces = np.concatenate(
                        (self.faces, np.array([(v_len - 4, v_len - 3, v_len - 2, v_len - 1)]))
                        , axis=0
                        )

        self.colors = [self.edge_color] * len(self.faces)
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
