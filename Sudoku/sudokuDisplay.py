import pygame
import os
from sudoku import Grid

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (270,40)

surface = pygame.display.set_mode((1000, 850))
pygame.display.set_caption('This is Sudoku')

pygame.font.init()
game_font = pygame.font.SysFont('Comic Sans MS', 45)
game_font2 = pygame.font.SysFont('Comic Sans MS', 20)

grid = Grid(pygame, game_font)
running = True

player_lost = False

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not (grid.win or player_lost):
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                grid.get_mouse_click(pos[0], pos[1])
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and (grid.win or player_lost):
                grid.restart()
                player_lost = False
            elif event.key == pygame.K_TAB:
                grid.restart()
                player_lost = False

    surface.fill((0, 0, 0))

    grid.draw_all(pygame, surface)

    if grid.strikes == 5:
        player_lost = True

    if player_lost:
        lost_surface = game_font.render("You Lose!", False, (255, 0, 0))
        surface.blit(lost_surface, (760, 560))

        press_space_surf = game_font2.render("Press Space to restart!", False, (255, 0, 0))
        surface.blit(press_space_surf, (750, 640))

    if grid.win:
        won_surface = game_font.render("You Won!", False, (0, 255, 0))
        surface.blit(won_surface, (760, 560))

        press_space_surf = game_font2.render("Press Space to restart!", False, (0, 255, 200))
        surface.blit(press_space_surf, (750, 640))

    

    pygame.display.flip()