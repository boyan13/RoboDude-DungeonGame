import pygame
import sys
from os import listdir
from os.path import isfile, join
from pygame.locals import *
from robodude.characters.Player import Player
from robodude.map.Dungeon import Dungeon


def game(mapfile):
    pygame.init()  # Initialize pygame
    pygame.display.set_caption('RoboDude')  # Set the window name/title

    player = Player('Jimmy', 'The Spelunker')
    dungeon = Dungeon(mapfile, player)
    dungeon.spawn_player()
    # dungeon.outline_solid_collision()
    # dungeon.outline_entity_collision()

    while True:
        # MOVE PLAYER
        if dungeon.player.moving_right:
            dungeon.player.x += dungeon.player.velocity
            if (dungeon.check_for_border_collision() or
                    dungeon.check_for_collision(dungeon.player.hitbox, tile='blocks')):
                dungeon.player.x -= dungeon.player.velocity
        if dungeon.player.moving_left:
            dungeon.player.x -= dungeon.player.velocity
            if (dungeon.check_for_border_collision() or
                    dungeon.check_for_collision(dungeon.player.hitbox, tile='blocks')):
                dungeon.player.x += dungeon.player.velocity
        if dungeon.player.moving_up:
            dungeon.player.y -= dungeon.player.velocity
            if (dungeon.check_for_border_collision() or
                    dungeon.check_for_collision(dungeon.player.hitbox, tile='blocks')):
                dungeon.player.y += dungeon.player.velocity
        if dungeon.player.moving_down:
            dungeon.player.y += dungeon.player.velocity
            if (dungeon.check_for_border_collision() or
                    dungeon.check_for_collision(dungeon.player.hitbox, tile='blocks')):
                dungeon.player.y -= dungeon.player.velocity

        # GET NEXT INPUT
        for event in pygame.event.get():
            if event.type == QUIT:  # Check for window quit (when X is pressed)
                pygame.quit()  # stop pygame
                sys.exit()  # stop the script
            if event.type == KEYDOWN:  # when a key is PRESSED down (not held)
                if event.key == K_RIGHT:
                    dungeon.player.moving_right = True
                if event.key == K_LEFT:
                    dungeon.player.moving_left = True
                if event.key == K_UP:
                    dungeon.player.moving_up = True
                if event.key == K_DOWN:
                    dungeon.player.moving_down = True
            if event.type == KEYUP:  # when a key is released (unpressed)
                if event.key == K_RIGHT:
                    dungeon.player.moving_right = False
                if event.key == K_LEFT:
                    dungeon.player.moving_left = False
                if event.key == K_UP:
                    dungeon.player.moving_up = False
                if event.key == K_DOWN:
                    dungeon.player.moving_down = False

        dungeon.update_interractions()

        # DISPLAY CHANGES
        dungeon.render()
        pygame.display.update()  # Update screen (refresh)
        dungeon.clock.tick(60)  # Framerate


def main():
    if len(sys.argv) == 1:
        maps_path = "maps/"
        maps = [m for m in listdir(maps_path) if isfile(maps_path + m)]
        print("\n====================================================")
        print("Select map to play by typing: ")
        print("\"python main.py <id of map>\"")
        print("\nCurrently available maps:")
        for m in maps:
            print(m)
        print("====================================================")

    if len(sys.argv) > 2:
        print("\n====================================================")
        print("Error. Type \"python main.py\" for help.")
        print("====================================================")

    if len(sys.argv) == 2:
        mapid = sys.argv[1]
        maps_path = "maps/"
        map = [maps_path + m for m in listdir(maps_path) if isfile(maps_path + m) and m.startswith(mapid)][0]
        game(map)


if __name__ == '__main__':
    main()
