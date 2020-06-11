import pygame


from ..utils import utils


class AnimatedSpriteSheet:
    '''
    THE SPRITESHEET IMAGES MUST BE PROPORTIONALLY DISTANCED AND OF THE SAME SIZE.
    THE SPRITESHEET IMAGE SHOULD BE ARRANGED AS A MATRIX.

    Load a sprite sheet image and it will be parsed to a list of every frame.\n
    If one of the 2 dimensional parameters (w or h) is set to -1,\n
    the other will be auto-calculated to be proportional to the first.\n

    Call the animation_update() method to move the animations along.\n
    Call the render() method to render the appropriate frame automatically.\n
    '''

    def __init__(self, filename, rows, cols, w, h, animation_speed=10, game_fps=60):
        '''
        Parameters:\n
        filename - spritesheet image path\n
        rows, cols - gives information on how to cut up the matrix (spritesheet)
        w, h - desired sizes for each frame
        animation_fps - what fps does the animation consist of
        game_fps - (default 60), what fps the game the spritesheet will be rendered in use
        '''

        # =============== Frame Data ===============
        original = pygame.image.load(filename)
        sz = original.get_size()
        self.rows = rows
        self.cols = cols
        self.frame_count = rows * cols

        if w == -1 and h > 0:
            h *= rows
            w = utils.get_proportional(sz, h, width=False)  # We are passing Height not Width (and expecting a proportionate width value)
        elif h == -1 and w > 0:
            w *= cols
            h = utils.get_proportional(sz, w, width=True)  # We are passing Width (and expecting a proportionate height value)
        elif w < -1 or h < -1:
            raise ValueError("Either both dimensions are negative or one is less than -1.")
        else:
            w *= cols
            h *= rows

        self.sheet = pygame.transform.scale(original, (w, h))

        self.rect = self.sheet.get_rect()
        self.frame_width = self.rect.width / cols
        self.frame_height = self.rect.height / rows

        self.frames = list([(index % cols * self.frame_width, index % rows * self.frame_height, self.frame_width, self.frame_height)
                            for index in range(self.frame_count)])

        # =============== Animation ===============
        self.anim_speed = animation_speed
        self.anim_current_frame = 0
        self.anim_count = 0
        self.game_fps = game_fps
        self.loops = self.game_fps // self.anim_speed


    def render(self, screen, x, y):
            screen.blit(self.sheet, (x, y), self.frames[self.anim_current_frame])

    def animation_update(self):
        if self.anim_count == self.frame_count * self.loops:
            self.anim_count = 0

        self.anim_current_frame = self.anim_count // self.loops
        self.anim_count += 1

    def setup_animate_once_loop(self):
        self.anim_count = 0
        self.anim_current_frame = 0

    def animate_once_loop(self, screen, x, y):
        self.render(screen, x, y)
        if self.anim_count == self.frame_count * self.loops:
            return True
        return False
