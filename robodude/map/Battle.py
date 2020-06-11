import pygame
import sys
import random


from pygame.locals import *


class Battle:

    # Recommended height values for rendering full sized characters (to be called in AnimatedSpriteSheet constructor)
    battle_h512 = 512
    battle_h556 = 556




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Setup and Resizing $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def __init__(self, player, ui, enemy, clock, player_vertical_offset, enemy_vertical_offset, fps):
        # =============== Configs ===============
        self.size = (1600, 900)
        self.inputs = {
            0: "quickmode",
            1: "melee",
            2: "ranged",
            3: "crit melee",
            4: "crit ranged",
            5: "inspect"
        }

        self.ENEMY_RESPONSE = pygame.USEREVENT+1
        self.EXIT = pygame.USEREVENT+2

        # Check 'set_state' to view all recognized states
        self._state = "Get Input"

        self._loaded_action = None  # If self.info_and_confirm is true, this holds the index of the action that awaits confirmation

        self.quickmode = False

        # =============== Gameplay ===============
        self.screen = pygame.display.set_mode(self.size, 0, 32)
        self.player = player
        self.enemy = enemy
        self.ui = ui
        self.ui.update_width(self.size[0])
        self.clock = clock
        self.fps = fps
        self.player_position = (200, self.size[1] - player_vertical_offset)
        self.enemy_position = (800, self.size[1] - enemy_vertical_offset)

        # =============== Display and Text ===============
        self.action_caption = f"A battle has begun against {self.enemy.name}"
        self.action_info = None  # Holds a tuple of tuples: (line, positional rect)

        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.small_font = pygame.font.Font('freesansbold.ttf', 18)

        self.background_color = (64, 48, 48)
        self.menu_color = (15, 15 ,15)
        self.caption_color = (5, 5, 5)
        self.menu_background_color = (148, 128, 128)

        # =============== Input UI ===============
        self.txt_activate_quickmode = self.small_font.render("Press [0] to activate QuickMode and skip confirmation from now on.", True, self.menu_color)
        self.txt_deactivate_quickmode = self.small_font.render("Press [0] to deactivate QuickMode and see detailed view from now on.", True, self.menu_color)
        self.txt_inspect_enemy = self.small_font.render(f"Press [i] to inspect your enemy", True, self.menu_color)
        self.txt_melee = self.small_font.render("Press [1] to cast a Melee Attack!", True, self.menu_color)
        self.txt_ranged = self.small_font.render("Press [2] to cast a Ranged Attack (Shoot)!", True, self.menu_color)
        self.txt_crit_melee = self.small_font.render("Press [3] to use a stored Critical Strike on a Melee Attack!", True, self.menu_color)
        self.txt_crit_ranged = self.small_font.render("Press [4] to use a stored Critical Strike on a Ranged Attack!", True, self.menu_color)

        w, h = self.txt_activate_quickmode.get_size()
        self.txt_activate_quickmode_rect = pygame.Rect(5, self.ui.h + 5, w, h)
        w, h = self.txt_deactivate_quickmode.get_size()
        self.txt_deactivate_quickmode_rect = pygame.Rect(5, self.ui.h + 5, w, h)
        self.txt_inspect_enemy_rect = None
        self.txt_melee_rect = None
        self.txt_ranged_rect = None
        self.txt_crit_melee_rect = None
        self.txt_crit_ranged_rect = None

        self.menu_options = [
            self.txt_activate_quickmode,
            self.txt_inspect_enemy,
            self.txt_melee,
            self.txt_ranged,
            self.txt_crit_melee,
            self.txt_crit_ranged,
        ]

        self.menu_positions = [
            self.txt_activate_quickmode_rect,
            self.txt_inspect_enemy_rect,
            self.txt_melee_rect,
            self.txt_ranged_rect,
            self.txt_crit_melee_rect,
            self.txt_crit_ranged_rect
        ]

        for i in range(1, len(self.menu_options)):
            w, h = self.menu_options[i].get_size()
            self.menu_positions[i] = pygame.Rect(5, self.ui.h + 5 + self.small_font.get_linesize() * i, w, h)

        self.menu_background = pygame.Rect(0, self.ui.h, self.size[0], self.ui.h + 5 + self.small_font.get_linesize() * (len(self.menu_options) - 1))




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Gameplay $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def fight(self):
        check_vitals = True

        while (True):
            for event in pygame.event.get():
                if event.type == QUIT:  # Check for window quit (when X is pressed)
                    pygame.quit()  # stop pygame
                    sys.exit()  # stop the script

                elif event.type == self.ENEMY_RESPONSE:
                    pygame.time.set_timer(self.ENEMY_RESPONSE, 0)
                    self.enemy_action_melee()

                elif event.type == self.EXIT:
                    pygame.time.set_timer(self.EXIT, 0)
                    if self.player.is_dead():
                        return False
                    else:
                        return True

                elif self._state == "Get Input":
                    if event.type == KEYDOWN:  # when a key is PRESSED down (not held)
                        if event.key == K_0:
                            self.execute_action(0)

                        elif event.key == K_1:
                            if self.quickmode:
                                self.execute_action(1)
                            else:
                                self.get_info_and_confirm_action(1)

                        elif event.key == K_2 and self.player.has_ammo():
                            if self.quickmode:
                                self.execute_action(2)
                            else:
                                self.get_info_and_confirm_action(2)

                        elif event.key == K_3 and self.player.critical_meter == self.player.critical_meter_max:
                            if self.quickmode:
                                self.execute_action(3)
                            else:
                                self.get_info_and_confirm_action(3)

                        elif event.key == K_4 and self.player.has_ammo() and self.player.critical_meter == self.player.critical_meter_max:
                            if self.quickmode:
                                self.execute_action(4)
                            else:
                                self.get_info_and_confirm_action(4)

                        elif event.key == K_i:
                            self.get_info_and_confirm_action(5)

                elif self._state == "Confirm Action":
                    if event.type == KEYDOWN:  # when a key is PRESSED down (not held)
                        if event.key == K_y:
                            self.execute_action(-1)
                        elif event.key == K_n:
                            self.set_state("Get Input")

            self.render()
            self.clock.tick(self.fps)




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Rendering and State $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def set_state(self, val):
        '''
        CALL THIS METHOD FROM LOW-LEVEL ACTION METHODS.\n
        An action method should optionally setup a state at its first and last line\n
        Recognized States and their purpose:\n
        "Get Input" - render both in idle, prints options menu and waits for user input\n
        "Confirm Action" - render both in idle, waits for confirmation on the loaded action (if not running in quickmode)\n
        "Resolve Action" - render only enemy in idle, ignore inputs\n
        "Downtime" - render both in idle, nothing else happens\n
        "Resolve Response" - render only player in idle, ignore inputs\n
        '''
        if val == "Get Input":
            self._loaded_action = None
            self._state = "Get Input"

        elif val == "Confirm Action":
            self._state = "Confirm Action"

        elif val == "Resolve Action":
            self._state = "Resolve Action"

        elif val == "Downtime":
            self._state = "Downtime"

        elif val == "Resolve Response":
            self._state = "Resolve Response"

        elif val == "Final":
            self._state = "Final"

    def render_player_options(self):
        pygame.draw.rect(self.screen, self.menu_background_color, self.menu_background)
        for i in range(len(self.menu_options)):
            self.screen.blit(self.menu_options[i], self.menu_positions[i])

    def render_info(self, inspect=False):
        pygame.draw.rect(self.screen, self.menu_background_color, self.menu_background)
        for pair in self.action_info:
            line, pos = pair
            self.screen.blit(line, pos)

        if not inspect:
            confirm = self.small_font.render("Confirm this action? Y / N", True, (126, 32, 32))
        else:
            confirm = self.small_font.render("Press N to return to menu.", True, (126, 32, 32))

        confirm_rect = confirm.get_rect()
        confirm_rect.center = (self.size[0] // 2, self.ui.h + 5 + len(self.action_info) * self.small_font.get_linesize())

        self.screen.blit(confirm, confirm_rect)

    def render(self, display_update=True):
        self.screen.fill(self.background_color)
        self.ui.render(self.screen)

        if self._state == "Get Input":
            self.render_player_options()
            self.player.ss_idle.render(self.screen, self.player_position[0], self.player_position[1])
            self.enemy.ss_idle.render(self.screen, self.enemy_position[0], self.enemy_position[1])

        elif self._state == "Confirm Action":
            if self._loaded_action == 5:
                self.render_info(inspect=True)
            else:
                self.render_info()
            self.player.ss_idle.render(self.screen, self.player_position[0], self.player_position[1])
            self.enemy.ss_idle.render(self.screen, self.enemy_position[0], self.enemy_position[1])

        elif self._state == "Resolve Action":
            self.enemy.ss_idle.render(self.screen, self.enemy_position[0], self.enemy_position[1])

        elif self._state == "Downtime":
            self.player.ss_idle.render(self.screen, self.player_position[0], self.player_position[1])
            self.enemy.ss_idle.render(self.screen, self.enemy_position[0], self.enemy_position[1])

        elif self._state == "Resolve Response":
            self.player.ss_idle.render(self.screen, self.player_position[0], self.player_position[1])

        elif self._state == "Final":
            if self.player.is_dead():
                self.enemy.ss_idle.render(self.screen, self.enemy_position[0], self.enemy_position[1])
                self.screen.blit(self.player.dead, (self.player_position[0], self.player_position[1]))
            elif self.enemy.is_dead():
                self.player.ss_idle.render(self.screen, self.player_position[0], self.player_position[1])
                self.screen.blit(self.enemy.dead, (self.enemy_position[0], self.enemy_position[1]))

        txt_enemy_health = self.small_font.render(f"Helath: {self.enemy.healthpool} / {self.enemy.max_health}", True, self.menu_color)
        txt_enemy_health_rect = pygame.Rect(self.enemy_position[0] + self.enemy.ss_idle.frame_width // 2, self.enemy_position[1] - 30, txt_enemy_health.get_size()[0], txt_enemy_health.get_size()[1])

        self.screen.blit(txt_enemy_health, txt_enemy_health_rect)

        caption = self.font.render(self.action_caption, True, self.caption_color)
        caption_rect = caption.get_rect()
        caption_rect.center = (self.size[0] // 2, self.size[1] - 50)

        self.screen.blit(caption, caption_rect)

        self.animations_update()
        if display_update:
            pygame.display.update()

    def animations_update(self):
        self.player.animations_update()
        self.enemy.animations_update()




    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Player Action Logic $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def get_info_and_confirm_action(self, idx):
        self._loaded_action = idx
        index = self.inputs[idx]

        if index == "melee":
            self.detailed_action_melee()

        elif index == "ranged":
            self.detailed_action_ranged()

        elif index == "crit melee":
            self.detailed_action_crit_melee()

        elif index == "crit ranged":
            self.detailed_action_crit_ranged()

        elif index == "inspect":
            self.context_action_inspect()

    def detailed_action_melee(self):
        txt1 = self.small_font.render("You are about to attack with a Melee Strike.", True, self.menu_color)
        txt2 = self.small_font.render(f"This attack deals {self.player.melee_damage} standard damage, and {self.player.melee_damage * self.player.melee_critical_damage_multiplier} crit damage.", True, self.menu_color)
        txt3 = self.small_font.render(f"Your base melee critical chance is {self.player.melee_critical_chance}", True, self.menu_color)

        txt1_pos = None
        txt2_pos = None
        txt3_pos = None

        lines = [txt1, txt2, txt3]
        positions = [txt1_pos, txt2_pos, txt3_pos]
        info = []
        for i in range(len(lines)):
            w, h = lines[i].get_size()
            positions[i] = pygame.Rect(5, self.ui.h + 5 + self.small_font.get_linesize() * i, w, h)
            info.append((lines[i], positions[i]))

        self.action_info = tuple(info)
        self.set_state("Confirm Action")

    def detailed_action_ranged(self):
        txt1 = self.small_font.render("You are about to attack with a Ranged Strike.", True, self.menu_color)
        txt2 = self.small_font.render(f"This attack has {100 - self.player.aim}% chance to miss and deal 0 damage!", True, self.menu_color)
        txt3 = self.small_font.render(f"This attack deals {self.player.ranged_damage} standard damage, and {self.player.ranged_damage * self.player.ranged_critical_damage_multiplier} crit damage.", True, self.menu_color)
        txt4 = self.small_font.render(f"Your base ranged critical chance is {self.player.ranged_critical_chance}", True, self.menu_color)

        txt1_pos = None
        txt2_pos = None
        txt3_pos = None
        txt4_pos = None

        lines = [txt1, txt2, txt3, txt4]
        positions = [txt1_pos, txt2_pos, txt3_pos, txt4_pos]
        info = []
        for i in range(len(lines)):
            w, h = lines[i].get_size()
            positions[i] = pygame.Rect(5, self.ui.h + 5 + self.small_font.get_linesize() * i, w, h)
            info.append((lines[i], positions[i]))

        self.action_info = tuple(info)
        self.set_state("Confirm Action")

    def detailed_action_crit_melee(self):
        txt1 = self.small_font.render("You are about to cast a Critical Melee Strike.", True, self.menu_color)
        txt2 = self.small_font.render(f"This attack will empty your critical meter and deal {self.player.melee_damage * self.player.melee_critical_damage_multiplier} damage.", True, self.menu_color)
        txt3 = self.small_font.render(f"Note: Your base melee critical chance is {self.player.melee_critical_chance}", True, self.menu_color)

        txt1_pos = None
        txt2_pos = None
        txt3_pos = None

        lines = [txt1, txt2, txt3]
        positions = [txt1_pos, txt2_pos, txt3_pos]
        info = []
        for i in range(len(lines)):
            w, h = lines[i].get_size()
            positions[i] = pygame.Rect(5, self.ui.h + 5 + self.small_font.get_linesize() * i, w, h)
            info.append((lines[i], positions[i]))

        self.action_info = tuple(info)
        self.set_state("Confirm Action")

    def detailed_action_crit_ranged(self):
        txt1 = self.small_font.render("You are about to cast a Critical Ranged Strike.", True, self.menu_color)
        txt2 = self.small_font.render(f"This attack will empty your critical meter and deal {self.player.ranged_damage * self.player.ranged_critical_damage_multiplier} damage.", True, self.menu_color)
        txt3 = self.small_font.render("This attack cannot miss.", True, self.menu_color)
        txt4 = self.small_font.render(f"Note: Your base ranged critical chance is {self.player.ranged_critical_chance}", True, self.menu_color)

        txt1_pos = None
        txt2_pos = None
        txt3_pos = None
        txt4_pos = None

        lines = [txt1, txt2, txt3, txt4]
        positions = [txt1_pos, txt2_pos, txt3_pos, txt4_pos]
        info = []
        for i in range(len(lines)):
            w, h = lines[i].get_size()
            positions[i] = pygame.Rect(5, self.ui.h + 5 + self.small_font.get_linesize() * i, w, h)
            info.append((lines[i], positions[i]))

        self.action_info = tuple(info)
        self.set_state("Confirm Action")

    def context_action_inspect(self):
        randomized_line = [
            "Fear thee, for you are facing {}!",
            "Beware, for your every move is anticipated by {}!",
            "You should've chosen another path, because now you face {}!",
            "Will you let your will be crushed by {}!?",
            "Wow, you stare in {}'s eyes and yet you do not tremble!",
            "As you inspect {}, they inspect you. I can feel the tension!"
        ]

        i = random.randint(0, len(randomized_line)-1)
        line = randomized_line[i].format(self.enemy.name)

        txt1 = self.small_font.render(line, True, self.menu_color)
        txt2 = self.small_font.render(f"Max Health: {self.enemy.max_health}", True, self.menu_color)
        txt3 = self.small_font.render(f"Melee Damage: {self.enemy.damage} / Critical Melee Damage: {self.enemy.damage * self.enemy.critical_damage_multiplier}", True, self.menu_color)
        txt4 = self.small_font.render(f"Critical Strike Chance: {self.enemy.critical_chance}", True, self.menu_color)

        txt1_pos = None
        txt2_pos = None
        txt3_pos = None
        txt4_pos = None

        lines = [txt1, txt2, txt3, txt4]
        positions = [txt1_pos, txt2_pos, txt3_pos, txt4_pos]
        info = []
        for i in range(len(lines)):
            w, h = lines[i].get_size()
            positions[i] = pygame.Rect(5, self.ui.h + 5 + self.small_font.get_linesize() * i, w, h)
            info.append((lines[i], positions[i]))

        self.action_info = tuple(info)
        self.set_state("Confirm Action")

    def execute_action(self, idx=-1):
        '''
        Executes the action that corresponds to the index entry in the 'inputs' dict.\n
        If -1 is passed, executes the currently loaded action (if running in detailed mode, (quickmode == False))
        '''

        if idx == -1:
            idx = self._loaded_action

        action = self.inputs[idx]

        if action == "quickmode":
            self.action_toggle_quickmode()
        if action == "melee":
            self.action_attack_melee()
        if action == "ranged":
            self.action_attack_ranged()
        if action == "crit melee":
            self.action_attack_melee_with_crit()
        if action == "crit ranged":
            self.action_attack_ranged_with_crit()

    def action_toggle_quickmode(self):
        if self.quickmode is True:
            self.quickmode = False
            self.menu_options[0] = self.txt_activate_quickmode
            self.menu_positions[0] = self.txt_activate_quickmode_rect

        elif self.quickmode is False:
            self.quickmode = True
            self.menu_options[0] = self.txt_deactivate_quickmode
            self.menu_positions[0] = self.txt_deactivate_quickmode_rect

    def action_attack_melee(self):
        self.set_state("Resolve Action")

        damage, critflag = self.player.deal_melee_damage()

        if critflag is False:
            self.player.ss_melee.setup_animate_once_loop()
            done = False
            while not done:
                self.render(display_update=False)
                done = self.player.ss_melee.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
                pygame.display.update()

        elif critflag is True:
            self.player.ss_critical_melee.setup_animate_once_loop()
            done = False
            while not done:
                self.render(display_update=False)
                done = self.player.ss_critical_melee.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
                pygame.display.update()

        self.enemy.take_damage(damage)
        self.player.increment_critical_meter()

        if critflag:
            self.action_caption = f"{self.player.name} {self.player.title} dealt a Critical Strike to {self.enemy.name} for {damage} damage!"
        else:
            self.action_caption = f"{self.player.name} {self.player.title} hit {self.enemy.name} for {damage} damage!"

        if self.enemy.is_dead():
            self.enemy_action_death()
        else:
            pygame.time.set_timer(self.ENEMY_RESPONSE, 3000)
            self.set_state("Downtime")

    def action_attack_ranged(self):
        self.set_state("Resolve Action")

        damage, critflag = self.player.deal_ranged_damage()

        if critflag is False:
            self.player.ss_ranged.setup_animate_once_loop()
            done = False
            while not done:
                self.render(display_update=False)
                done = self.player.ss_ranged.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
                pygame.display.update()

        elif critflag is True:
            for i in range(3):
                self.player.ss_critical_ranged.setup_animate_once_loop()
                done = False
                while not done:
                    self.render(display_update=False)
                    done = self.player.ss_critical_ranged.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
                    pygame.display.update()

        self.enemy.take_damage(damage)
        self.player.increment_critical_meter()
        self.player.use_ammo(1)

        if damage == 0:
            self.action_caption = f"{self.player.name} {self.player.title} 's attack MISSED!"
        elif critflag:
            self.action_caption = f"{self.player.name} {self.player.title} dealt a Critical Strike to {self.enemy.name} for {damage} damage!"
        else:
            self.action_caption = f"{self.player.name} {self.player.title} hit {self.enemy.name} for {damage} damage!"

        if self.enemy.is_dead():
            self.enemy_action_death()
        else:
            pygame.time.set_timer(self.ENEMY_RESPONSE, 3000)
            self.set_state("Downtime")

    def action_attack_melee_with_crit(self):
        self.set_state("Resolve Action")

        damage, critflag = self.player.deal_melee_damage(crit=True)

        self.player.ss_critical_melee.setup_animate_once_loop()
        done = False
        while not done:
            self.render(display_update=False)
            done = self.player.ss_critical_melee.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
            pygame.display.update()

        self.enemy.take_damage(damage)
        self.player.empty_critical_meter()

        self.action_caption = f"{self.player.name} {self.player.title} dealt a Critical Strike to {self.enemy.name} for {damage} damage!"

        if self.enemy.is_dead():
            self.enemy_action_death()
        else:
            pygame.time.set_timer(self.ENEMY_RESPONSE, 3000)
            self.set_state("Downtime")

    def action_attack_ranged_with_crit(self):
        self.set_state("Resolve Action")

        damage = self.player.deal_ranged_damage(crit=True)[0]

        for i in range(3):
            self.player.ss_critical_ranged.setup_animate_once_loop()
            done = False
            while not done:
                self.render(display_update=False)
                done = self.player.ss_critical_ranged.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
                pygame.display.update()

        self.enemy.take_damage(damage)
        self.player.empty_critical_meter()
        self.player.use_ammo(1)

        self.action_caption = f"{self.player.name} {self.player.title} dealt a Critical Strike to {self.enemy.name} for {damage} damage!"

        if self.enemy.is_dead():
            self.enemy_action_death()
        else:
            pygame.time.set_timer(self.ENEMY_RESPONSE, 3000)
            self.set_state("Downtime")

    def action_death(self):
        self.set_state("Resolve Action")

        self.player.ss_death.setup_animate_once_loop()
        done = False
        while not done:
            self.render(display_update=False)
            done = self.player.ss_death.animate_once_loop(self.screen, self.player_position[0], self.player_position[1])
            pygame.display.update()

        self.action_caption = f"{self.player.name} {self.player.title} has been slain by {self.enemy.name}!"

        pygame.time.set_timer(self.EXIT, 4000)
        self.set_state("Final")

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Enemy Response Logic $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def enemy_action_melee(self):
        self.set_state("Resolve Response")

        damage, critflag = self.enemy.deal_damage()

        if critflag is False:
            self.enemy.ss_melee.setup_animate_once_loop()
            done = False
            while not done:
                self.render(display_update=False)
                done = self.enemy.ss_melee.animate_once_loop(self.screen, self.enemy_position[0], self.enemy_position[1])
                pygame.display.update()

        elif critflag is True:
            self.enemy.ss_critical_melee.setup_animate_once_loop()
            done = False
            while not done:
                self.render(display_update=False)
                done = self.enemy.ss_critical_melee.animate_once_loop(self.screen, self.enemy_position[0], self.enemy_position[1])
                pygame.display.update()

        self.player.take_damage(damage)

        if critflag:
            self.action_caption = f"{self.enemy.name} dealt a Critical Strike to {self.player.name} {self.player.title}  for {damage} damage!"
        else:
            self.action_caption = f"{self.enemy.name} hit {self.player.name} {self.player.title} for {damage} damage!"

        if self.player.is_dead():
            self.action_death()
        else:
            self.set_state("Get Input")

    def enemy_action_death(self):
        self.set_state("Resolve Response")

        self.enemy.ss_death.setup_animate_once_loop()
        done = False
        while not done:
            self.render(display_update=False)
            done = self.enemy.ss_death.animate_once_loop(self.screen, self.enemy_position[0], self.enemy_position[1])
            pygame.display.update()

        self.action_caption = f"{self.enemy.name} has been slain by {self.player.name} {self.player.title}!"

        pygame.time.set_timer(self.EXIT, 4000)
        self.set_state("Final")
