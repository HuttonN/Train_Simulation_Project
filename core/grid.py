class Grid:
    """
    Represents a 2D grid for placing track pieces. Each cell holds a set of objects
    (e.g. track_pieces, trains, carriages)
    """

    def __init__(self, rows, cols, cell_size=40):
        """
        Arguments:
            rows: Number of grid rows
            cols: Number of grid columns
            cell_size: Pixel size of each cell
        """
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        # Initialise 2D grid. Each cell has an empty set
        self.grid = [[set() for _ in range(cols)] for _ in range(rows)]

    def in_bounds(self, row, col):
        """Returns true if the cell (row, col) is within the grid boundaries"""
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def add_object(self, row, col, obj):
        """Add an object (track, train, etc) to the specified cell."""
        if self.in_bounds(row, col):
            self.grid[row][col].add(obj)

    def remove_object(self, row, col, obj):
        """Remove an object from the specified cell (if present)."""
        if self.in_bounds(row, col):
            self.grid[row][col].discard(obj)

    def objects_at(self, row, col):
        """Return the set of all objects at the specified cell."""
        if self.in_bounds(row, col):
            return self.grid[row][col]
        return set()

    def clear(self):
        """Clear all objects from the grid."""
        self.grid = [[set() for _ in range(self.cols)] for _ in range(self.rows)]

    def grid_to_screen(self, row, col):
        """Convert (row, col) grid coords to (x, y) screen coords."""
        x = col * self.cell_size
        y = row * self.cell_size
        return x, y

    def screen_to_grid(self, x, y):
        """Convert (x, y) screen coords to (row, col) grid coords."""
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        return row, col

    def all_objects(self):
        """Yield (row, col, obj) for every object on the grid."""
        for r in range(self.rows):
            for c in range(self.cols):
                for obj in self.grid[r][c]:
                    yield (r, c, obj)

    def draw_grid(self, surface, color=(80, 80, 80)):
        """
        Draws the grid lines on the given pygame surface.
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

    def has_object_of_type(self, row, col, obj_type):
        """Returns True if any object of type obj_type is in cell (row, col)."""
        return any(isinstance(obj, obj_type) for obj in self.objects_at(row, col))

    def get_objects_of_type(self, row, col, obj_type):
        """Returns a list of objects of type obj_type in cell (row, col)."""
        return [obj for obj in self.objects_at(row, col) if isinstance(obj, obj_type)]
