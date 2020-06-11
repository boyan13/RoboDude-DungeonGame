import pygame
import random


from ..map.Battle import Battle
from ..utils.AnimatedSpriteSheet import AnimatedSpriteSheet
from ..utils import utils


class Player:

    """
    Creates a player object

    Parameters:\n
    name (String): the name of the player\n
    title (String): a title to display after the name\n
    base_health (non-negative number): The maximum amount of health points the player has\n
    base_melee_damage (non-negative number): The melee damage the player inflicts\n
    base_ranged_damage (non-negative number): The ranged damage the player inflicts (if the attack does not miss)\n
    base_aim (percentage between 0 and 100): The chance a ranged attack will hit the target (if it misses it deals 0 damage)\n
    base_ammo (non-negative number): The maximum amount of ammo the player can carry. Ranged attacks can be cast only if ammo is > 0\n
    base_crit_chance (percentage between 0 and 100): The chance an attack will deal extra damage\n
    crit_meter (non-negative number): Inflicting damage fills this meter. When full it stores a critical attack that can be activated by the player at will\n
    """

    def __init__(self, name, title, health=100, melee=18,
                 ranged=25, aim=80, ammo=5,
                 melee_crit=35, ranged_crit=25, crit_meter=5, game_fps=60):

        # =============== General ===============
        self.name = name
        self.title = "'" + title + "'"

        # =============== Configs ===============
        self.w = 48
        self.h = 48
        self.hitbox = None
        self.show_collision = False
        self.game_fps = game_fps


        # =============== Images ===============
        icon_right = pygame.image.load('media\\icons01\\player_icon_right_128.png')
        icon_left = pygame.image.load('media\\icons01\\player_icon_left_128.png')
        self.icon_right = pygame.transform.smoothscale(icon_right, (self.w, self.h))
        self.icon_left = pygame.transform.smoothscale(icon_left, (self.w, self.h))

        dead = pygame.image.load('media\\player01\\death_last_frame.png')
        self.dead = pygame.transform.smoothscale(dead, (utils.get_proportional(dead.get_size(), Battle.battle_h556, width=False), Battle.battle_h556))

        self.ss_idle = AnimatedSpriteSheet('media\\player01\\10_idle_right_spritesheet.png', rows=1, cols=10, w=-1, h=Battle.battle_h556, animation_speed=12)
        self.ss_melee = AnimatedSpriteSheet('media\\player01\\8_melee_right_spritesheet.png', rows=1, cols=8, w=-1, h=Battle.battle_h556, animation_speed=5)
        self.ss_ranged = AnimatedSpriteSheet('media\\player01\\4_shoot_right_spritesheet.png', rows=1, cols=4, w=-1, h=Battle.battle_h556, animation_speed=5)
        self.ss_critical_melee = AnimatedSpriteSheet('media\\player01\\14_jump_melee_right_spritesheet.png', rows=1, cols=14, w=-1, h=Battle.battle_h556, animation_speed=4)
        self.ss_critical_ranged = AnimatedSpriteSheet('media\\player01\\4_shoot_right_spritesheet.png', rows=1, cols=4, w=-1, h=Battle.battle_h556, animation_speed=6)
        self.ss_death = AnimatedSpriteSheet('media\\player01\\10_death_right_spritesheet.png', rows=1, cols=10, w=-1, h=Battle.battle_h556, animation_speed=10)


        # =============== Gameplay Configs ===============
        self.melee_critical_damage_multiplier = 2
        self.ranged_critical_damage_multiplier = 3
        self.melee_critical_chance = melee_crit
        self.ranged_critical_chance = ranged_crit
        self.critical_meter_max = crit_meter

        self.max_health = health
        self.max_ammo = ammo

        self.melee_damage = melee
        self.ranged_damage = ranged
        self.aim = aim


        # =============== Dynamic (Update during gameplay)===============
        self.healthpool = health
        self.ammo = ammo
        self.critical_meter = 0
        self.last_direction = self.icon_right


        # =============== Positioning and Movement ===============
        self.loc = {'x': None, 'y': None}

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False
        self.velocity = 5

    @property
    def x(self):
        return self.loc['x']

    @property
    def y(self):
        return self.loc['y']




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Rendering and state updating $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    @x.setter
    def x(self, val):
        self.loc['x'] = val
        self.update_collision()

    @y.setter
    def y(self, val):
        self.loc['y'] = val
        self.update_collision()

    def render(self, screen):
        '''
        You must call the 'spawn' method first,
        before attempting to render the player.
        '''
        if (self.x is not None and
            self.y is not None):

            if self.moving_right:
                screen.blit(self.icon_right, (self.x, self.y))
                self.last_direction = self.icon_right
            elif self.moving_left:
                screen.blit(self.icon_left, (self.x, self.y))
                self.last_direction = self.icon_left
            else:
                screen.blit(self.last_direction, (self.x, self.y))

            if self.show_collision:
                pygame.draw.rect(screen, (0, 255, 0), self.hitbox, 2)

    def animations_update(self):
        '''
        Ticks the animations of every sprite sheet (that is added manually).
        '''

        self.ss_idle.animation_update()
        self.ss_melee.animation_update()
        self.ss_ranged.animation_update()
        self.ss_critical_melee.animation_update()
        self.ss_critical_ranged.animation_update()
        self.ss_death.animation_update()




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Collisions $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def update_collision(self):
        # self.collision_box = pygame.Rect(self.x, self.y, self.w, self.h)
        self.hitbox = (self.x, self.y, self.w, self.h)




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Gameplay Mechanics $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def take_healing(self, amount):
        if self.healthpool + amount > self.max_health:
            self.healthpool = self.max_health
        else:
            self.healthpool += amount

    def take_damage(self, amount):
        if self.healthpool - amount < 0:
            self.healthpool = 0
        else:
            self.healthpool -= amount

    def is_dead(self):
        return self.healthpool == 0

    def has_ammo(self):
        return self.ammo > 0

    def add_ammo(self, amount):
        if self.ammo + amount < self.max_ammo:
            self.ammo += amount
        else:
            self.ammo = self.max_ammo

    def use_ammo(self, amount):
        if self.ammo > 0:
            self.ammo -= 1

    def empty_critical_meter(self):
        self.critical_meter = 0

    def increment_critical_meter(self):
        if self.critical_meter < self.critical_meter_max:
            self.critical_meter += 1

    def deal_melee_damage(self, crit=False):
        '''
        Calculates the melee damage to be dealt.\n
        If passed with crit=True, this attack will deal critical damage.\n
        If passed with crit=False (default), this attack has default chance
        to trigger critical damage.\n

        Returns: tuple ( (float) damage, (boolean) critical? )
        '''

        if crit or random.randint(0,100) < self.melee_critical_chance:
            return (self.melee_damage * self.melee_critical_damage_multiplier, True)
        else:
            return (self.melee_damage, False)

    def deal_ranged_damage(self, crit=False):
        '''
        Calculates the ranged damage to be dealt.\n
        If passed with crit=True, this attack will deal critical damage.\n
        If passed with crit=False (default), this attack has default chance
        to trigger critical damage.\n

        Returns: tuple ( (float) damage, (boolean) critical? )
        '''

        if crit or random.randint(0,100) < self.aim:
            if crit or random.randint(0, 100) < self.melee_critical_chance:
                return (self.ranged_damage * self.ranged_critical_damage_multiplier, True)
            else:
                return (self.ranged_damage, False)
        else:
            return (0, False)  # Missed!




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Debug $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def show_hitbox(self, val=True):
        '''
        Sets the 'show_collision' variable to True (by default) or False,
        which in turn enables the displaying of the player's collision box.
        '''
        self.show_collision = val
