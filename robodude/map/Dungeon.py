import pygame
import sys
import time
from ..utils.AnimatedSpriteSheet import AnimatedSpriteSheet
from .Ui import Ui
from .Battle import Battle
from ..characters.Battle_Ninja import Battle_Ninja


class Dungeon:
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Static Data $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    # Acceptable keyword arguments the map parser recognizes (all must be specified in the map file)
    parser_index = {
        'dimensions': 0,
        'color': 1,
        'player': 2
    }
    # The number of the parser-specific arguments
    parser_index_size = len(parser_index)




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Setting and Getting $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def __init__(self, mapfile, player, fps=60):
        # =============== Core Data ===============
        # Holds a list with the position of every tile on the map, sorted by type
        self.collision_index = {
            'blocks': [],
            'enemies': [],
            'potions': [],
            'ammo': [],
            'gates': []
        }
        # List that detemines which tile type is considered an entity (interractable object)
        self.interractable_tiles_index = [
            'enemies', 'potions', 'ammo', 'gates'
        ]
        self.clock = pygame.time.Clock()
        self.fps = fps


        # =============== Scale and Postion ==========
        self.map_scale = (50, 50)  # The scale of the map. Entities can have whatever scale, but is used for their positioning
        self.gate_scale = (50, 50)
        self.gate_offset = (0, 0)
        self.potion_scale = (20, 20)
        self.potion_offset = ((self.map_scale[0] - self.potion_scale[0]) // 2, (self.map_scale[1] - self.potion_scale[1]) // 2)
        self.enemy_icon_scale = (50, 50)
        self.enemy_icon_offset = (0, 0)
        self.ammo_scale = (20, 20)
        self.ammo_offset = ((self.map_scale[0] - self.ammo_scale[0]) // 2, (self.map_scale[1] - self.ammo_scale[1]) // 2)
        self.top_bar_height = 40


        # =============== Art Assets ===============
        gate_img = pygame.image.load('media/dungeon01/DoorUnlocked.png')
        block_img = pygame.image.load('media/dungeon01/SolidTile.png')
        potion_img = pygame.image.load('media/consumables01/health_blob.png')
        ammo_img = pygame.image.load('media/consumables01/plasma_blob.png')

        self.block_img = pygame.transform.smoothscale(block_img, self.map_scale)
        self.gate_img = pygame.transform.smoothscale(gate_img, self.gate_scale)
        self.potion_img = pygame.transform.smoothscale(potion_img, self.potion_scale)
        self.ammo_img = pygame.transform.smoothscale(ammo_img, self.ammo_scale)
        self.enemy_icon_idle_sprite = AnimatedSpriteSheet('media/enemy01/10_enemy_icon_idle_left_spritesheet.png', rows=1, cols=10, w=self.map_scale[0], h=self.map_scale[1], animation_speed=12)


        # =============== Animation Config ===============
        self.anim_total_frames = 10  # The number of frames the animation consist of
        self.anim_current_frame = 0  # Index that determines which fram from the spritesheet to be displayed (used in 'animations_update()')
        self.anim_speed = 20  # Speed of the animation(in fps), aka how many times it loops in 60 fps
        self.anim_count = 0  # Counter that determines which frame should display (used in 'animations_update()')


        # =============== Dynamic Data ===============
        self.player = player
        parsed = Dungeon.parse(mapfile)
        self.dimensions = parsed['dimensions']
        self.color = parsed['color']
        player_start_x, player_start_y = self.calc_player_start(parsed['player'])
        self.player_start = (player_start_x, player_start_y + self.top_bar_height)
        self.dungeon = parsed['dungeon']
        self.ui = Ui(w=self.dimensions[1] * self.map_scale[0], h=self.top_bar_height, player=self.player)


        # =============== Debug ===============
        # Debug var - if True, will outline collision boxes for every tile (not performance friendly)
        self.show_solid_collision = False
        self.show_entity_collision = False


        # =============== Final ================
        self.screen = pygame.display.set_mode(self.calc_size(), 0, 32)


        # =============== Autocalls ===============
        # Enables collision of the map when it's first created
        self.init_dungeon()

    def init_dungeon(self):
            '''
            Generates the dungeon by filling the 'collision_index' variable\n
            The 'collision_index' represents the state of the map, while the 'dungeon' variable holds the original state.
            '''

            for i, row in enumerate(self.dungeon):
                i *= self.map_scale[1]
                i += self.top_bar_height
                for j, pos in enumerate(row):
                    j *= self.map_scale[0]

                    if pos == 'B':
                        self.collision_index['blocks'].append(tuple(
                            [j, i, self.map_scale[0], self.map_scale[1]]
                            ))

                    if pos == 'E':
                        self.collision_index['enemies'].append(tuple(
                            [j, i, self.map_scale[0], self.map_scale[1]]
                            ))

                    if pos == 'G':
                        self.collision_index['gates'].append(tuple(
                            [j, i, self.map_scale[0], self.map_scale[1]]
                            ))

                    if pos == 'P':
                        self.collision_index['potions'].append(tuple(
                            [j + self.potion_offset[1], i + self.potion_offset[0], self.potion_scale[0], self.potion_scale[1]]
                        ))

                    if pos == 'A':
                        self.collision_index['ammo'].append(tuple(
                            [j + self.ammo_offset[1], i + self.ammo_offset[0], self.ammo_scale[0], self.ammo_scale[1]]
                        ))




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Rendering and State $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def spawn_player(self):
        '''
        Used to initialize player coordinates and render the player
        for the first time.\n
        '''
        self.player.loc['x'] = self.player_start[0]
        self.player.loc['y'] = self.player_start[1]
        self.player.update_collision()
        self.player.render(self.screen)

    def render(self):
        '''
        Renders the map.\n
        Map is interpreted as follows:

        ' ' = nothing, don't draw a tile\n
        'b' = block (tile)\n
        'g' = gate (exit)\n
        'e' = enemy\n
        'p' = potion\n
        'a' = ammo
        '''

        # Set background color
        self.screen.fill(self.color)

        # Render top bar
        self.ui.render(self.screen)

        for tile in self.collision_index['blocks']:

            j, i = tile[0], tile[1]

            jpos = j * self.map_scale[1]
            ipos = i * self.map_scale[0]
            self.screen.blit(self.block_img, (j, i))

        for tile in self.collision_index['gates']:

            j, i = tile[0], tile[1]

            jpos = j * self.map_scale[1]
            ipos = i * self.map_scale[0]
            self.screen.blit(self.gate_img, (j, i))

        for tile in self.collision_index['enemies']:

            j, i = tile[0], tile[1]

            jpos = j * self.map_scale[1]
            ipos = i * self.map_scale[0]
            self.enemy_icon_idle_sprite.render(self.screen, j, i)

        for tile in self.collision_index['ammo']:

            j, i = tile[0], tile[1]

            jpos = j * self.map_scale[1]
            ipos = i * self.map_scale[0]
            self.screen.blit(self.ammo_img, (j, i))

        for tile in self.collision_index['potions']:

            j, i = tile[0], tile[1]

            jpos = j * self.map_scale[1]
            ipos = i * self.map_scale[0]
            self.screen.blit(self.potion_img, (j, i))

        if self.show_solid_collision:
            for raw_rect in self.collision_index['blocks']:
                pygame.draw.rect(self.screen, (255, 0, 0), raw_rect, 2)

        if self.show_entity_collision:
            for tile_type in self.collision_index:
                if tile_type in self.interractable_tiles_index:
                    for raw_rect in self.collision_index[tile_type]:
                        pygame.draw.rect(self.screen, (0, 255, 0), raw_rect, 2)

        self.player.render(self.screen)
        self.animations_update()

    def animations_update(self):
        '''
        Ticks the animations of every sprite sheet (that is added manually).
        '''

        self.enemy_icon_idle_sprite.animation_update()




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Collisions $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def check_for_collision(self, box, tile):
        '''
        Return true if the provided rect object ('box')
        collides with any tile of type 'tile' (where 'tile' is a string
        present in the collision_index)
        '''

        for raw_rect in self.collision_index[tile]:
            if pygame.Rect(raw_rect).colliderect(box):
                return True

    def check_for_border_collision(self):
        w, h = self.calc_dungeon_size()
        if (self.player.x < 0 or
                self.player.x + self.player.w > w or
                self.player.y < 0 or
                self.player.y + self.player.h > h):
            return True



    
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Entity Interraction $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def update_interractions(self):
        '''
        Check if player collides with entities and call the interraction index function, 
        which in turn redirects to the proper function to execute the interraction.
        '''

        for k, v in self.collision_index.items():

            if k in self.interractable_tiles_index:
                for idx, raw_rect in enumerate(self.collision_index[k]):
                    if pygame.Rect(raw_rect).colliderect(self.player.hitbox):
                        self.execute_interraction_with_player(k, idx)

    def execute_interraction_with_player(self, tile_type, tile_idx):
        '''
        Parameters:
        tile_type - (The key) string to filter the class' collision_index dict
        tile_list_idx - (The value) the index of the specific entity the player is colliding with (also for lookup in the collision_index dict)

        Depending on the key (tile_type), decides which function to call, passing it the value (tile_list_idx)
        '''
        if tile_type == 'ammo':
            self.interraction_pick_up_ammo(tile_idx)
        # elif tile_type == 'enemies':
        #     self.interraction_initiate_fight(tile_list_idx)
        elif tile_type == 'potions':
            self.interraction_pick_up_health_blob(tile_idx)
        elif tile_type == 'gates':
            self.interraction_victory()
        elif tile_type == 'enemies':
            self.begin_battle(tile_idx)

    def interraction_pick_up_ammo(self, idx):
        if self.player.ammo < self.player.max_ammo:
            self.player.add_ammo(1)
            del self.collision_index['ammo'][idx]

    def interraction_pick_up_health_blob(self, idx):
        if self.player.healthpool < self.player.max_health:
            self.player.take_healing(20)
            del self.collision_index['potions'][idx]

    def interraction_victory(self):
        w, h = self.calc_dungeon_size()
        font = pygame.font.Font('freesansbold.ttf', 64)
        text = font.render('Victory!', True, (0, 255, 0), self.color)
        text_rect = text.get_rect()
        text_rect.center = (w // 2, h // 2)

        self.screen.fill(self.color)
        self.screen.blit(text, text_rect)
        pygame.display.update()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    def begin_battle(self, idx):
        # =============== Text ===============
        w, h = self.calc_dungeon_size()
        font = pygame.font.Font('freesansbold.ttf', 64)

        intro_txt = font.render("Prepare to fight!", True, (0, 255, 128))
        defeat_txt = font.render('You were defeated!', True, (255, 0, 0), self.color)

        intro_txt_rect = intro_txt.get_rect()
        defeat_txt_rect = defeat_txt.get_rect()

        intro_txt_w = self.screen.get_size()[0]
        intro_txt_h = intro_txt.get_size()[1]

        intro_txt_background = pygame.Rect(0, 0, intro_txt_w, intro_txt_h + 30)

        intro_txt_background.center = (w // 2, h // 2)
        intro_txt_rect.center = (w // 2, h // 2)
        defeat_txt_rect.center = (w // 2, h // 2)

        pygame.draw.rect(self.screen, (32, 32, 32), intro_txt_background)
        self.screen.blit(intro_txt, intro_txt_rect)
        pygame.display.update()
        time.sleep(1)

        # =============== Logic ===============
        self.player.moving_up = False
        self.player.moving_right = False
        self.player.moving_down = False
        self.player.moving_left = False

        enemy = Battle_Ninja.randomNinja()
        battle = Battle(self.player, self.ui, enemy, self.clock, 630, 600, self.fps)
        player_won = battle.fight()
    
        w, h = self.calc_size()
        pygame.display.set_mode((w, h), 0, 32)

        self.ui.update_width(w)

        if player_won:
            del self.collision_index['enemies'][idx]

        else:
            self.screen.fill(self.color)
            self.screen.blit(defeat_txt, defeat_txt_rect)
            pygame.display.update()

            time.sleep(2)
            pygame.quit()
            sys.exit()




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Computational $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def calc_player_start(self, matrix_pos):
        '''
        Returns the exact position the player should spawn,

        Parameters:
        i (int): matrix coordinate for the row (vertical)
        j (int): matrix coordinate for the colum (horizontal)

        Returns:
        tuple: x, y
        '''
        i, j = matrix_pos
        return (i * self.map_scale[1], j * self.map_scale[0])

    def calc_size(self):
        '''
        Returns the size of the window that should be created to fit the level 
        (including the ui top bar).

        Returns:
        tuple: width, height (in pixels)
        '''
        return (self.map_scale[0] * self.dimensions[1],
                self.map_scale[1] * self.dimensions[0] + self.top_bar_height)

    def calc_dungeon_size(self):
        '''
        Returns the size of the dungeon only.

        Returns:
        tuple: width, height (in pixels)
        '''
        return (self.map_scale[0] * self.dimensions[1],
                self.map_scale[1] * self.dimensions[0])




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Map Parsing $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    @classmethod
    def parse(cls, mapfile):
        '''
        Reads a map file by first parsing all key value pairs
        and then parsing the dungeon.

        The file should have all 'key=value' pairs first, and
        the actual dungeon matrix at the bottom.
        Do not leave empty lines.
        Every 'key=value' pair must be on a new line.
        The dungeon matrix must have each row on a new line.
        '''
        data = dict()
        with open(mapfile, 'r') as f:
            for i in range(cls.parser_index_size):
                param, val = f.readline().split('=')
                data[param] = cls.parse_arg(cls.parser_index[param], val)

            if len(data) != cls.parser_index_size:
                raise ValueError("Parser met duplicating keywords.")

            dungeon = f.readlines()
            data['dungeon'] = cls.parse_dungeon(dungeon)
        return data

    @classmethod
    def parse_arg(cls, param_id, val):
        if param_id == 0:
            return cls.parse_dimensions(val)
        elif param_id == 1:
            return cls.parse_color(val)
        elif param_id == 2:
            return cls.parse_player(val)
        else:
            raise ValueError("param_id did not match any existing sub-parser.")

    @classmethod
    def parse_dimensions(cls, val):
        rows, cols = val.split('x')
        rows.strip()
        cols.strip()
        rows = int(rows)
        cols = int(cols)
        return (rows, cols)

    @classmethod
    def parse_color(cls, val):
        r, g, b = val.split(',')
        r.strip()
        g.strip()
        b.strip()
        r = int(r)
        g = int(g)
        b = int(b)
        return (r, g, b)

    @classmethod
    def parse_player(cls, val):
        player_row, player_col = val.split(',')
        player_row.strip()
        player_col.strip()
        player_row = int(player_row)
        player_col = int(player_col)
        return (player_row, player_col)

    @classmethod
    def parse_dungeon(cls, matrix):
        for idx, line in enumerate(matrix):
            if line == "":
                del matrix[idx]
            else:
                matrix[idx] = list(line.strip())
                if matrix[idx][-1] == '\n':
                    matrix[idx] = matrix[idx][:-1]
        return matrix




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Debugging $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    
    def outline_solid_collision(self, val=True):
        '''
        Sets the 'show_collision' variable to True (by default) or False,
        which enables rendering of the map collisions.
        '''

        self.show_solid_collision = val
    
    def outline_entity_collision(self, val=True):
        '''
        Sets the 'show_collision' variable to True (by default) or False,
        which enables rendering of the map collisions.
        '''

        self.show_entity_collision = val