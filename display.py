# Drawing of the splash, config and score screens.
# The layout is designed for 1280x720 and scaled to the real screen size (fonts and logo are created at
# the scaled size once, so nothing is scaled per frame - important for the speed on a Raspberry Pi 3).
import pygame # type: ignore

from game import FOUL_PENALTY, TEAMS

DESIGN_WIDTH, DESIGN_HEIGHT = 1280, 720

# Colors
cyan = (100, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
grey = (100, 100, 100)
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 160, 0)
dark_red = (140, 0, 0)

TimeOutText = ("", "*", "**", "***")
TeamX = {"Home": 200, "Away": 1080}  # horizontal center of each team's column


class Display:
    def __init__(self, resolution, logo_path):
        size = (0, 0) if resolution == "auto" else tuple(int(v) for v in resolution.lower().split("x"))
        self.scr = pygame.display.set_mode(size, pygame.FULLSCREEN)
        pygame.display.set_caption('Basketbal Clock')
        pygame.mouse.set_visible(0)

        width, height = self.scr.get_size()
        self.scale = min(width / DESIGN_WIDTH, height / DESIGN_HEIGHT)
        self.offset = ((width - DESIGN_WIDTH * self.scale) / 2, (height - DESIGN_HEIGHT * self.scale) / 2)

        # Fonts
        self.fontScore = self._font('fonts/LED.ttf', 200)
        self.fontScoreSmall = self._font('fonts/LED.ttf', 90)
        self.fontLabel = self._font('fonts/DejaVuSans-Bold.ttf', 80)
        self.fontLabelSmall = self._font('fonts/DejaVuSans-Bold.ttf', 40)
        self.fontLabelExtraSmall = self._font('fonts/DejaVuSans-Bold.ttf', 30)

        # Images
        self.LogoClub = self._image(logo_path)
        self.Loading1 = self._image('image/loading1.svg')
        self.Loading2 = self._image('image/loading2.svg')

        self._cache = {}

    # --- Scaling helpers: all coordinates below are in the 1280x720 design ---

    def _font(self, path, size):
        return pygame.font.Font(path, max(1, round(size * self.scale)))

    def _image(self, path):
        image = pygame.image.load(path)
        if self.scale == 1:
            return image
        size = (round(image.get_width() * self.scale), round(image.get_height() * self.scale))
        return pygame.transform.smoothscale(image.convert_alpha(), size)

    def pos(self, x, y):
        # Whole pixels: older pygame versions (Debian Bookworm has 2.1.2) do not accept fractions everywhere
        return (round(self.offset[0] + x * self.scale), round(self.offset[1] + y * self.scale))

    def rect(self, x, y, w, h):
        return pygame.Rect(*self.pos(x, y), round(w * self.scale), round(h * self.scale))

    def render(self, font, text, color):
        # Rendering big LED digits is the slowest part of a frame, and most texts do not change: cache them
        key = (id(font), text, color)
        if key not in self._cache:
            if len(self._cache) > 500:
                self._cache.clear()
            self._cache[key] = font.render(text, True, color, black)
        return self._cache[key]

    def text_center(self, font, text, color, x, y):
        surface = self.render(font, text, color)
        self.scr.blit(surface, surface.get_rect(center=self.pos(x, y)))

    def text_at(self, font, text, color, x, y):
        """Draw text with its top left corner at (x, y), returns the x where the text ends."""
        surface = self.render(font, text, color)
        self.scr.blit(surface, self.pos(x, y))
        return x + surface.get_width() / self.scale

    def logo(self):
        self.scr.blit(self.LogoClub, self.pos(350, 330))

    def connection_indicator(self, connected):
        """Small dot in the bottom right corner: green = remote connected, red = no remote connected."""
        pygame.draw.circle(self.scr, green if connected else dark_red, self.pos(1262, 702), max(2, round(8 * self.scale)))

    # --- Screens ---

    def splash(self, step):
        self.scr.fill(black)
        self.logo()
        self.scr.blit(self.Loading1 if step % 2 == 0 else self.Loading2, self.pos(500, 460))
        pygame.display.flip()

    def config_screen(self, period_length, connected):
        self.scr.fill(black)
        self.text_at(self.fontLabel, 'Duration Period', white, 50, 75)
        self.text_at(self.fontLabelSmall, 'Use PERIOD - or + to change value', white, 50, 200)
        self.text_at(self.fontLabelSmall, 'Use START - STOP to confirm', white, 50, 250)
        self.text_center(self.fontScore, str(int(period_length / 60)), yellow, 1000, 100)
        self.logo()
        rows = (('U6:  1 match - ', '8', ' min - continuous clock'),
                ('U8:  8 quarters - ', '6', ' min - continuous clock'),
                ('U10: 8 quarters - ', '5', ' min - cronostop'),
                ('U12 & above: 4 quarters - ', '10', ' min - cronostop'))
        for i, (label, minutes, kind) in enumerate(rows):
            y = 520 + i * 40
            x = self.text_at(self.fontLabelExtraSmall, label, white, 50, y)
            x = self.text_at(self.fontLabelExtraSmall, minutes, yellow, x, y)
            self.text_at(self.fontLabelExtraSmall, kind, white, x, y)
        if connected is not None:
            self.connection_indicator(connected)
        pygame.display.flip()

    def scoreboard(self, game, now, tenths, connected):
        self.scr.fill(black)

        # Fixed text
        self.text_center(self.fontLabel, 'HOME', grey, TeamX["Home"], 50)
        self.text_center(self.fontLabel, 'AWAY', grey, TeamX["Away"], 50)
        self.text_center(self.fontLabel, 'P', grey, 590, 50)

        for team in TEAMS:
            x = TeamX[team]
            self.text_center(self.fontLabel, 'FOULS', grey, x, 480)
            self.text_center(self.fontScore, str(game.score[team]), yellow, x, 200)
            # Put the fouls in red from 4 to indicate free shots
            fouls_color = red if game.fouls[team] >= FOUL_PENALTY else yellow
            self.text_center(self.fontScore, str(game.fouls[team]), fouls_color, x, 600)
            self.text_center(self.fontScore, TimeOutText[min(game.timeouts[team], 3)], yellow, x, 350)
            pygame.draw.rect(self.scr, cyan, self.rect(x - 150, 110, 300, 200), max(1, round(5 * self.scale)))

        self.text_center(self.fontScore, game.clock_text(now, tenths), red, 640, 200)
        self.text_center(self.fontScoreSmall, game.period_text(), yellow, 670, 50)

        # Time-out countdown, or the count-up pause time after the end of a period (same place)
        if game.timeout_running:
            self.text_center(self.fontScore, str(game.timeout_left(now)), yellow, 640, 600)
        pause = game.pause_text(now)
        if pause:
            self.text_center(self.fontScore, pause, yellow, 640, 600)

        self.logo()
        if game.possession == 1:
            pygame.draw.rect(self.scr, red, self.rect(420, 40, 50, 10))
            pygame.draw.polygon(self.scr, red, [self.pos(390, 45), self.pos(420, 75), self.pos(420, 15)])
        if game.possession == 2:
            pygame.draw.rect(self.scr, red, self.rect(810, 40, 50, 10))
            pygame.draw.polygon(self.scr, red, [self.pos(890, 45), self.pos(860, 75), self.pos(860, 15)])
        if connected is not None:
            self.connection_indicator(connected)
        pygame.display.flip()
