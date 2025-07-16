"""
grid.py

Defines the Grid class, representing a 2D grid for placing track pieces and other objects.
Each cell holds a set of objects (e.g., track pieces, trains, carriages), and provides
utility methods for object management and coordinate conversion.
"""

class Grid:
    """
    Represents a 2D grid for placing track pieces. Each cell holds a set of objects
    (e.g. track_pieces, trains, carriages)
    """

    def __init__(self, rows, cols, cell_size=40):
        """
        Initialise a new grid.

        Arguments:
            rows: Number of grid rows
            cols: Number of grid columns
            cell_size: Pixel size of each cell
        """
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid = [[set() for _ in range(cols)] for _ in range(rows)]

    def in_bounds(self, row, col):
        """
        Check if a cell is within the grid boundaries.

        Arguments:
            row: Row index.
            col: Column index.

        Returns:
            bool: True if the cell is within bounds, False otherwise.
        """
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def add_object(self, row, col, obj):
        """
        Add an object to the specified cell.

        Arguments:
            row: Row index.
            col: Column index.
            obj: Object to add.
        """
        if self.in_bounds(row, col):
            self.grid[row][col].add(obj)

    def remove_object(self, row, col, obj):
        """
        Remove an object from the specified cell, if present.

        Arguments:
            row: Row index.
            col: Column index.
            obj: Object to remove.
        """
        if self.in_bounds(row, col):
            self.grid[row][col].discard(obj)

    def objects_at(self, row, col):
        """
        Return the set of all objects at the specified cell.

        Arguments:
            row: Row index.
            col: Column index.

        Returns:
            set: Set of objects at the cell, or an empty set if out of bounds.
        """
        if self.in_bounds(row, col):
            return self.grid[row][col]
        return set()

    def clear(self):
        """
        Clear all objects from the grid.
        """
        self.grid = [[set() for _ in range(self.cols)] for _ in range(self.rows)]

    def grid_to_screen(self, row, col):
        """
        Convert grid coordinates to pixel (x, y) coordinates at the cell center.

        Arguments:
            row: Row index.
            col: Column index.

        Returns:
            tuple: (x, y) pixel coordinates of the cell center.
        """
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        return x, y

    def screen_to_grid(self, x, y):
        """
        Convert pixel (x, y) coordinates to grid (row, col) coordinates.

        Arguments:
            x: X pixel coordinate.
            y: Y pixel coordinate.

        Returns:
            tuple: (row, col) grid indices.
        """
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        return row, col

    def all_objects(self):
        """
        Yield all objects in the grid with their locations.

        Yields:
            tuple: (row, col, obj) for every object in the grid.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                for obj in self.grid[r][c]:
                    yield (r, c, obj)

    def draw_grid(self, surface, color=(80, 80, 80)):
        """
        Draw grid lines on a pygame surface.

        Arguments:
            surface: Pygame surface to draw on.
            color (tuple): RGB color for grid lines (default: (80, 80, 80)).
        """
        import pygame
        for row in range(self.rows + 1):
            pygame.draw.line(
                surface, color,
                (0, row * self.cell_size),
                (self.cols * self.cell_size, row * self.cell_size)
            )
        for col in range(self.cols + 1):
            pygame.draw.line(
                surface, color,
                (col * self.cell_size, 0),
                (col * self.cell_size, self.rows * self.cell_size)
            )

    def place_piece(self, row, col, piece):
        """
        Place a piece at (row, col), replacing all previous objects in that cell.
        Use add_object if you want to support multiple objects per cell

        Arguments:
            row: Row index.
            col: Column index.
            piece: The piece to place in the cell.
        """
        if self.in_bounds(row, col):
            self.grid[row][col] = set([piece])

    def has_object_of_type(self, row, col, obj_type):
        """
        Check if any object of the given type is present at (row, col).

        Arguments:
            row: Row index.
            col: Column index.
            obj_type: Type or class to check.

        Returns:
            bool: True if an object of obj_type is present, else False.
        """
        return any(isinstance(obj, obj_type) for obj in self.objects_at(row, col))

    def get_objects_of_type(self, row, col, obj_type):
        """
        Get a list of all objects of the given type at (row, col).

        Arguments:
            row: Row index.
            col: Column index.
            obj_type: Type or class to check.

        Returns:
            list: List of objects of the specified type at the cell.
        """
        return [obj for obj in self.objects_at(row, col) if isinstance(obj, obj_type)]
