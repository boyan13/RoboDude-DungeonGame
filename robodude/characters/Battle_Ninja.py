import pygame
import random


from ..map.Battle import Battle
from ..utils.AnimatedSpriteSheet import AnimatedSpriteSheet
from ..utils import utils


class Battle_Ninja:

    names = ["The Gman", "RK900", "David Wallace", "Elder Maxon", "Exodia", "Admiral Kotch", 
            "Lord Baelish", "Tyler Blevins", "He Bo", "Ricardo", "Negan", "Vaas Montenegro",
            "Tywin Lannister", "King Eredin", "Thanos", "Epic Games Representative", "Tod Howard", 
            "Howard the Alien", "SCREAAAAAAAAAAAM", "bitconnect", "Emhyr var Emreis"]

    def __init__(self, health=75, damage=20, crit_chance=30, game_fps=60):
        # =============== General ===============
        self.name = self.__class__.names[random.randint(0, len(Battle_Ninja.names) - 1)]


        # =============== Images ===============
        dead = pygame.image.load('media\\enemy01\\death_last_frame.png')
        self.dead = pygame.transform.smoothscale(dead, (utils.get_proportional(dead.get_size(), Battle.battle_h556, width=False), Battle.battle_h556))

        self.ss_idle = AnimatedSpriteSheet('media\\enemy01\\10_idle_left_spritesheet.png', rows=1, cols=10, w=-1, h=490, animation_speed=12)
        self.ss_melee = AnimatedSpriteSheet('media\\enemy01\\10_attack_left_spritesheet.png', rows=1, cols=10, w=-1, h=Battle.battle_h556, animation_speed=5)
        self.ss_critical_melee = AnimatedSpriteSheet('media\\enemy01\\14jump_melee_left_spritesheet.png', rows=1, cols=14, w=-1, h=Battle.battle_h556, animation_speed=6)
        self.ss_death = AnimatedSpriteSheet('media\\enemy01\\10_death_left_spritesheet.png', rows=1, cols=10, w=-1, h=Battle.battle_h512, animation_speed=10)


        # =============== Gameplay ===============
        self.critical_damage_multiplier = 2
        self.critical_chance = crit_chance

        self.max_health = health
        self.damage = damage

        self.healthpool = health

    @staticmethod
    def randomNinja():
        '''
        Returns a Battle Ninja with randomized stats.
        '''

        health = random.randint(50, 100)
        damage = random.randint(7, 14)
        crit_chance = random.randint(20, 30)

        return Battle_Ninja(health, damage, crit_chance)

    def animations_update(self):
        self.ss_idle.animation_update()
        self.ss_melee.animation_update()
        self.ss_critical_melee.animation_update()
        self.ss_death.animation_update()

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Gameplay $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

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

    def deal_damage(self, crit=False):
        '''
        Calculates the melee damage to be dealt.\n
        If passed with crit=True, this attack will deal critical damage.\n
        If passed with crit=False (default), this attack has default chance
        to trigger critical damage.\n

        Returns: tuple ( (float) damage, (boolean) critical? )
        '''

        if crit or random.randint(0,100) < self.critical_chance:
            return (self.damage * self.critical_damage_multiplier, True)
        else:
            return (self.damage, False)
