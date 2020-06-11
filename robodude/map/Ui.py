import pygame


class Ui:
    def __init__(self, w, h, player):
        self.player = player
        self.w = w
        self.h = h

        self.color = (15, 15, 15)
        self.border_color = (10, 10, 10)
        self.box = (0, 0, self.w, self.h)

        self.font = pygame.font.Font('freesansbold.ttf', 18)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.box)
        pygame.draw.rect(screen, self.border_color, self.box, 4)

        flex = self.w // 3
        flex_offset = flex // 2

        txt_health = self.font.render(f"Health: {self.player.healthpool} / {self.player.max_health}", True, (255, 255, 255), self.color)
        txt_health_rect = txt_health.get_rect()
        txt_health_rect.center = (flex * 1 - flex_offset , self.h // 2)

        txt_ammo = self.font.render(f"Ammo: {self.player.ammo} / {self.player.max_ammo}", True, (255, 255, 255), self.color)
        txt_ammo_rect = txt_ammo.get_rect()
        txt_ammo_rect.center = (flex * 2 - flex_offset, self.h // 2)

        txt_critical_meter = self.font.render(f"Critical meter: {self.player.critical_meter} / {self.player.critical_meter_max}", True, (255, 255, 255), self.color)
        txt_critical_meter_rect = txt_critical_meter.get_rect()
        txt_critical_meter_rect.center = (flex * 3 - flex_offset, self.h // 2)

        screen.blit(txt_health, txt_health_rect)
        screen.blit(txt_ammo, txt_ammo_rect)
        screen.blit(txt_critical_meter, txt_critical_meter_rect)

    def update_width(self, w):
        self.w = w
        self.box = (0, 0, self.w, self.h)