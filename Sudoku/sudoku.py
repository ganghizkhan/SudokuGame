from random import sample
from numSelect import SelectNumber
from copy import deepcopy

SUB_GRID_SIZE = 3
GRID_SIZE = SUB_GRID_SIZE * SUB_GRID_SIZE

def create_line_coor(cell_size: int) -> list[list[tuple]]:

    points = []
    for y in range(1, 10):
        temp = []
        temp.append((0, y * cell_size))
        temp.append((720, y * cell_size))
        points.append(temp)

    for x in range(1, 10):
        temp = []
        temp.append((x * cell_size, 0))
        temp.append((x * cell_size, 720))
        points.append(temp)
    return points

def pattern(row_num: int, col_num: int) -> int:
    return (SUB_GRID_SIZE * (row_num % SUB_GRID_SIZE) + row_num // SUB_GRID_SIZE + col_num) % GRID_SIZE

def shuffle(samp: range) ->list:
    return sample(samp, len(samp))

def create_grid(sub_grid: int) -> list[list]:
    row_base = range(sub_grid)
    rows = [g * sub_grid + r for g in shuffle(row_base) for r in shuffle(row_base)]
    cols = [g * sub_grid + c for g in shuffle(row_base) for c in shuffle(row_base)]
    nums = shuffle(range(1, sub_grid * sub_grid + 1))
    return [[nums[pattern(r, c)] for c in cols] for r in rows]

def remove_numbers(grid: list[list]) -> None:
    #---- Randomly sets numbers to zeros on the grid ----
    num_of_cells = GRID_SIZE * GRID_SIZE
    empties = num_of_cells * 3 // 7
    for i in sample(range(num_of_cells), empties):
        grid[i // GRID_SIZE][i % GRID_SIZE] = 0

class Grid:
    def __init__(self, pygame, font):
        self.cell_size = 80
        self.num_x_offset = 24
        self.num_y_offset = 5
        self.line_coordinates = create_line_coor(self.cell_size)
        self.grid = create_grid(SUB_GRID_SIZE)
        self.__test_grid = deepcopy(self.grid) # create a copy before removing numbers
        print(self.__test_grid)
        self.win = False

        remove_numbers(self.grid)
        self.occupied_cell_coordinates = self.pre_occupied_cells()
        # print(self.occupied_cell_coordinates)   

        self.strikes = 0
        self.incorrect_cells = []

        self.game_font = font

        self.selection = SelectNumber(pygame, self.game_font)

    def restart(self) -> None:
        self.grid = create_grid(SUB_GRID_SIZE)
        self.__test_grid = deepcopy(self.grid)
        remove_numbers(self.grid)
        self.occupied_cell_coordinates = self.pre_occupied_cells() 
        self.win = False
        self.strikes = 0


    def check_grids(self):
        # Checks if all the cells in the main grid and the test grid are equal
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] != self.__test_grid[y][x]:
                    return False
        return True

    def is_cell_preoccupied(self, x: int, y: int) -> bool:
        # Check for non playable cells - preoccupied/initialized cells
        for cell in self.occupied_cell_coordinates:
            if x == cell[1] and y == cell[0]: # x = column, y = row
                return True
        return False

    def get_mouse_click(self, x: int, y: int) -> None:
        # Sets an empty cell to a selected number
        if x <= 720:
            grid_x, grid_y = x // 80, y // 80
            if not self.is_cell_preoccupied(grid_x, grid_y):
                self.set_cell(grid_x, grid_y, self.selection.selected_number)

                if self.__test_grid[grid_y][grid_x] == self.selection.selected_number:
                    self.set_cell(grid_x, grid_y, self.selection.selected_number)
                else:
                    self.strikes += 1 
        self.selection.button_clicked(x, y)
        if self.check_grids():
            self.win = True

    def pre_occupied_cells(self) -> list[tuple]:
        # Gather the y,x coordinates for all preoccupied/initialized cells
        occupied_cell_coordinates = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.get_cell(x, y) != 0:
                    occupied_cell_coordinates.append((y, x))
        return occupied_cell_coordinates

    def __draw_lines(self, pg, surface) -> None:
        #---- Draw grid lines ----
        bold_line_thickness = 5
        regular_line_thickness = 2
        for index, point in enumerate(self.line_coordinates):
            if index == 2 or index == 5 or index == 11 or index == 14:
                pg.draw.line(surface, (255, 200, 0), point[0], point[1], bold_line_thickness)
            else:
                pg.draw.line(surface, (255, 255, 255), point[0], point[1], regular_line_thickness) 

    def __draw_numbers(self, surface) -> None:
        #---- Draw grid numbers ----
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.get_cell(x, y) != 0:
                    """if (y, x) in self.occupied_cell_coordinates:
                        text_surface = self.game_font.render(str(self.get_cell(x, y)), False , (0, 200, 255))
                    else:
                        text_surface = self.game_font.render(str(self.get_cell(x, y)), False , (0, 255, 0))

                    if self.get_cell(x, y) != self.__test_grid[y][x]:
                        text_surface = self.game_font.render(str(self.get_cell(x, y)), False, (255, 0, 0))"""
                    
                    if (y, x) in self.occupied_cell_coordinates:
                        text_color = (0, 200, 255)  # Pre-filled cells color
                    elif (y, x) in self.incorrect_cells:
                        text_color = (255, 0, 0)  # Incorrect cells color
                    else:
                        text_color = (0, 255, 0)  # Correct cells color

                    text_surface = self.game_font.render(str(self.get_cell(x, y)), False, text_color)
                    surface.blit(text_surface, (x * self.cell_size + self.num_x_offset, y * self.cell_size + self.num_y_offset))

    def draw_all(self, pg, surface):
        self.__draw_lines(pg, surface)
        self.__draw_numbers(surface)
        self.selection.draw(pg, surface)

        strike_surface = self.game_font.render(f"Strikes: {self.strikes}", False, (255, 0, 0))
        surface.blit(strike_surface, (100, 740))

        restart_surface = self.game_font.render(f"Press tab to restart", False, (0, 0, 255))
        surface.blit(restart_surface, (550, 740))

    def get_cell(self, x: int, y: int) -> int:
        return self.grid[y][x]
    
    def set_cell(self, x: int, y: int, value: int) -> None:
        #self.grid[y][x] = value

        if value != 0:
            if value == self.__test_grid[y][x]:
                self.grid[y][x] = value
                if (y, x) in self.incorrect_cells:
                    self.incorrect_cells.remove((y, x))  # Remove from incorrect cells if corrected
            else:
                self.grid[y][x] = value
                if (y, x) not in self.incorrect_cells:
                    self.incorrect_cells.append((y, x))  # Mark cell as incorrect

    def show(self):
        for cell in self.grid:
            print(cell)

if __name__ == "__main__":
    import pygame
    pygame.font.init()
    game_font = pygame.font.SysFont('Comic Sans MS', 45)
    grid = Grid(game_font)
    grid.show()
