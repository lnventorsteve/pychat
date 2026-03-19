import json
import math
import os
import time
import pyperclip
import pygame

pygame.init()
default_font = pygame.font.SysFont(pygame.font.get_default_font(), 24)

# lookup tables
shift_table = {
    32: 32,
    33: 33,
    34: 34,
    35: 35,
    36: 36,
    37: 37,
    38: 38,
    39: 34,
    40: 40,
    41: 41,
    42: 42,
    43: 43,
    44: 44,
    45: 95,
    46: 46,
    47: 63,
    48: 41,
    49: 33,
    50: 64,
    51: 35,
    52: 36,
    53: 37,
    54: 94,
    55: 38,
    56: 42,
    57: 40,
    58: 58,
    59: 58,
    60: 60,
    61: 43,
    62: 62,
    63: 63,
    64: 64,
    65: 65,
    66: 66,
    67: 67,
    68: 68,
    69: 69,
    70: 70,
    71: 71,
    72: 72,
    73: 73,
    74: 74,
    75: 75,
    76: 76,
    77: 77,
    78: 78,
    79: 79,
    80: 80,
    81: 81,
    82: 82,
    83: 83,
    84: 84,
    85: 85,
    86: 86,
    87: 87,
    88: 88,
    89: 89,
    90: 90,
    91: 123,
    92: 124,
    93: 125,
    94: 126,
    95: 95,
    96: 126,
    97: 65,
    98: 66,
    99: 67,
    100: 68,
    101: 69,
    102: 70,
    103: 71,
    104: 72,
    105: 73,
    106: 74,
    107: 75,
    108: 76,
    109: 77,
    110: 78,
    111: 79,
    112: 80,
    113: 81,
    114: 82,
    115: 83,
    116: 84,
    117: 85,
    118: 86,
    119: 87,
    120: 88,
    121: 89,
    122: 90,
    123: 91,
    124: 92,
    125: 93,
    126: 126}
resolutions = ("3840x2160", "1560x1600", "2560x1440", "1920x1440", "1920x1200", "1920x1080", "1680x1050",
               "1600x1200", "1600x1024", "1600x900", "1440x900", "1366x768", "1360x768", "1280x1024",
               "1280x960", "1280x800", "1280x768", "1280x720", "1152x864", "1024x768", "800x600")

def active(self):
    if type(self) != list:
        self.isActive = True
    else:
        for each in self:
            each.isActive = True

def get_center(center, scale, pos, tx=0, ty=0, size=(0, 0)):
    x, y = pos
    sx, sy = size
    sx = sx / 2 * scale
    sy = sy / 2 * scale
    if center == "left":
        pos = (x + tx / 2 - sx, y)
    elif center == "right":
        pos = (x - tx / 2 + sx, y)
    elif center == "top":
        pos = (x, y - ty / 2 - sy)
    elif center == "bottom":
        pos = (x, y + ty / 2 + sy)
    elif center == "top_left":
        pos = (x + tx / 2 - sx, y + ty / 2 - sy)
    elif center == "top_right":
        pos = (x - tx / 2 + sx, y + ty / 2 - sy)
    elif center == "bottom_left":
        pos = (x + tx / 2, y - ty / 2 + sy)
    elif center == "bottom_right":
        pos = (x - tx / 2 + sx, y - ty / 2 + sy)
    return pos

class Config:
    def __init__(self):
        self.current_w, self.current_h = 1920, 1080
        self.scale = 2
        self.screen_mode = "Windowed"
        self.main_display = 0
        self.theme = "Default theme"
        self.volume = 100
        self.target_fps = 20
        self.version = 0

    def load(self):
        try:
            with open("conf.json", "r") as conf:
                config_ = json.loads(conf.read())
            self.scale = config_["scale"]
            self.current_w, self.current_h = config_["screen_size"]
            self.screen_mode = config_["screen_mode"]
            self.main_display = config_["main_display"]
            self.theme = config_["theme"]
            self.volume = config_["volume"]
            self.target_fps = config_["target_fps"]
            self.version = config_["version"]
        except Exception as e:
            print("error loading config",e)

    def save(self):
        config_ = {"scale": self.scale,
                   "screen_size": [self.current_w,self.current_h],
                   "screen_mode": self.screen_mode,
                   "main_display": self.main_display,
                   "theme": self.theme,
                   "volume": self.volume,
                   "target_fps": self.target_fps,
                   "version": self.version}
        try:
            with open("conf.json", "w") as conf:
                conf.write(json.dumps(config_))

        except Exception as e:
            print("error saving config",e)

class App():
    def __init__(self, appname):
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        pygame.display.set_caption(appname)
        self.display = None
        self.screen = None
        self.screen_info = None
        self.name = appname
        self.config = Config()
        self.config.load()
        self.theme = Theme()
        self.theme.load_Theme(self.config)
        self.theme.sounds(volume=self.config.volume)
        self.p_frame = time.perf_counter()
        self.fps = 0
        self.menu_fps = 60
        self.game_fps = 60
        self.done = False
        self.debug = False
        self.setting = False
        self.reset_screen = False
        self.resizing = False
        self.check_settings = False
        self.user_login = False
        self.frame = 0
        self.quit = False

        self.Renderer = Renderer()
        self.Input = Input()

        self.Main_window = Layer(self, set_order=0)
        self.Debug_window = Layer(self, set_order=-1)
        self.Renderer.add_window(self.Main_window)
        self.Renderer.add_window(self.Debug_window)
        self.load_window()

    def load_window(self):
        if self.config.screen_mode == "Fullscreen":
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
            print("Fullscreen")
        elif self.config.screen_mode == "Borderless":
            flags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
            print("Borderless")
        else:
            flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
            print("Windowed")
        self.display = pygame.display.set_mode((self.config.current_w, self.config.current_h), flags, vsync=1,
                                          display=self.config.main_display)
        print(self.config.current_w, self.config.current_h)
        self.screen = (self.config.current_w / 2, self.config.current_h / 2)
        self.screen_info = (self.display, self.screen, self.config.scale)
        self.theme.screen_info(self.screen_info)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True

            if event.type == pygame.VIDEORESIZE:
                self.config.current_w = event.w
                self.config.current_h = event.h
                self.screen = (self.config.current_w / 2, self.config.current_h / 2)
                self.screen_info = (self.display, self.screen, self.config.scale)
                self.theme.screen_info(self.screen_info)


            self.Input.get_input(event,self.frame)
        self.Input.update(self.frame)

    def render(self):
        self.display.fill(self.theme.basecolor)
        self.Renderer.render()
        pygame.display.update()
        self.frame += 1

    def Quit(self):
        pygame.quit()
        self.config.save()

class Input:
    def __init__(self):
        self.Keys_pressed = {}  # raw key info
        self.keys = []  # key info with filter for button input
        self.unicode = []  # key info with filter for text input
        self.cursor_state = False
        self.mouse_info = (0, 0, 0)
        self.mouse_button = 0
        self.mouse_position = (0, 0)
        self.p_mouse_position = (0, 0)
        self.c_time = 0
        self.scroll_amount = 0
        self.mods = []
        self.CAPS = False
        self.looked_x = 0
        self.looked_y = 0
        self.capture_mouse = False
        self.nubClicks = 0
        self.last_mouse_button = 0
        self.last_click = 0

    def get_input(self, event, frame):
        if event.type == pygame.MOUSEMOTION:
            mx, my = self.mouse_position = event.pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.button , self.last_mouse_button,self.nubClicks)
            if event.button == self.last_mouse_button:
                print(time.perf_counter()+0.5,self.last_click)
                if time.perf_counter()+0.5>self.last_click:
                    self.nubClicks+=1
                else:
                    self.nubClicks = 0
                self.last_mouse_button = event.button
                self.last_click = time.perf_counter()
            self.mouse_button = event.button

        if event.type == pygame.MOUSEBUTTONUP:
            self.last_mouse_button = abs(self.mouse_button)
            self.mouse_button = 0
            mb = event.button
            scroll = mb
            if mb > 7:
                if mb % 2 == 0:
                    scroll -= 3
                    self.scroll_amount = -scroll
                else:
                    scroll -= 7
                    self.scroll_amount = scroll
            else:
                if mb == 4:
                    self.scroll_amount = -1
                if mb == 5:
                    self.scroll_amount = 1

        if event.type == pygame.KEYDOWN:
            key = event.key
            self.Keys_pressed[key] = [frame, time.perf_counter() + 0.5]
            if key > 1000000000:
                if key == 1073742049:
                    self.mods.append("SHIFT")
                elif key == 1073742048:
                    self.mods.append("CTRL")
                elif key == 1073742050:
                    self.mods.append("ALT")
                elif key == 1073742051:
                    self.mods.append("WIN")
                elif key == 1073742053:
                    self.mods.append("SHIFT")
                elif key == 1073742054:
                    self.mods.append("ALT")
                elif key == 1073742052:
                    self.mods.append("CTRL")
                elif key == 1073742881:
                    if "Caps" in self.mods:
                        self.mods.remove("Caps")
                    else:
                        self.mods.append("Caps")

        if event.type == pygame.KEYUP:
            key = event.key
            self.Keys_pressed.pop(key)

            if key > 1000000000:
                if key == 1073742049:
                    self.mods.remove("SHIFT")
                elif key == 1073742048:
                    self.mods.remove("CTRL")
                elif key == 1073742050:
                    self.mods.remove("ALT")
                elif key == 1073742051:
                    self.mods.remove("WIN")
                elif key == 1073742053:
                    self.mods.remove("SHIFT")
                elif key == 1073742054:
                    self.mods.remove("ALT")
                elif key == 1073742052:
                    self.mods.remove("CTRL")

    def update(self, frame):

        self.mouse_info = (self.mouse_position[0], self.mouse_position[1], self.mouse_button)
        if self.capture_mouse:
            pygame.mouse.set_visible(False)
            self.looked_x = self.p_mouse_position[0] - self.mouse_position[0]
            self.looked_y = self.p_mouse_position[1] - self.mouse_position[1]
            self.p_mouse_position = self.mouse_position
        else:
            pygame.mouse.set_visible(True)

        ct = time.perf_counter()
        self.keys = []
        for key in self.Keys_pressed:
            kf, kt = self.Keys_pressed[key]
            if kf == frame:
                self.keys.append(key)
            if ct > kt:
                self.keys.append(key)
                self.Keys_pressed[key] = [kf, kt + 0.05]
        self.unicode = []
        for key in self.keys:
            if key in shift_table:
                if "SHIFT" in self.mods or "CAPS" in self.mods:
                    self.unicode.append(chr(shift_table[key]))
                else:
                    self.unicode.append(chr(key))

    def cursor(self):
        if time.perf_counter() >= self.c_time:
            self.c_time = time.perf_counter() + 0.5
            self.cursor_state = not self.cursor_state
        return self.cursor_state

    def Keys_pressedraw(self):
        return self.Keys_pressed

    def mouse(self):
        return self.mouse_info

    def clicked(self):
        self.mouse_button = -abs(self.mouse_button)
        mx, my = self.mouse_position
        self.mouse_info = (mx, my, self.mouse_button)

    def scroll(self):
        scroll_amount = self.scroll_amount
        self.scroll_amount = 0
        return scroll_amount

class Theme:
    def __init__(self, screen_info=(None, (0, 0), 0), font=default_font, font_size=12,
                 font_name=pygame.font.get_default_font(), text_color=(255, 255, 255), border_color=(128, 128, 128),
                 background_color=(64, 64, 64),base_color=(0, 0, 0)):
        self.display = screen_info[0]
        self.screen = screen_info[1]
        self.width = self.screen[0] * 2
        self.height = self.screen[1] * 2
        self.scale = screen_info[2]
        self.font_name = font_name
        self.font = font
        self.font_size = font_size
        self.Colors = {text_color, border_color, background_color,base_color}
        self.tcolor = text_color
        self.bcolor = border_color
        self.bgcolor = background_color
        self.basecolor = base_color
        self.Sounds = {}
        self.sound_info = {}
        self.border = 3
        self.radius = 3
        self.path = str(os.path.dirname(__file__))

    def save_Theme(self):
        Theme = {}
        Theme["Colors"] = self.Colors
        Theme["Sounds"] = self.sound_info
        Theme["Fonts"] = {}
        Theme["Fonts"][self.font_name] = self.font_size
        Theme["Properties"] = {}
        Theme["Properties"]["Border Thickness"] = self.border
        Theme["Properties"]["Radius"] = self.radius
        return Theme

    def load_Theme(self, config, Theme=False):
        if Theme == False:
            file = config.theme
        else:
            file = Theme

        with open(f"{self.path}/Themes/{file}.json", "r") as Theme:
            Theme = json.loads(Theme.read())
            Fonts = []
            for font in Theme["Fonts"]:
                Fonts.append(font)
            self.font = pygame.font.SysFont(Fonts[0], Theme["Fonts"][Fonts[0]] * config.scale)
            self.font_size = Theme["Fonts"][Fonts[0]]
            self.font_name = Fonts[0]
            for sound in Theme["Sounds"]:
                try:
                    self.Sounds[sound] = pygame.mixer.Sound(f"{self.path}/sounds/{Theme['Sounds'][sound]['name']}")
                    self.Sounds[sound].set_volume(Theme["Sounds"][sound]["volume"])
                except:
                    self.Sounds[sound] = []
                    for name in Theme['Sounds'][sound]['names']:
                        temp = pygame.mixer.Sound(f"{self.path}/sounds/{name}")
                        temp.set_volume(Theme["Sounds"][sound]["volume"])
                        self.Sounds[sound].append(temp)
            self.sound_info = Theme["Sounds"]
            self.Colors = Theme["Colors"]
            self.tcolor = Theme["Colors"]['Text color']
            self.bcolor = Theme["Colors"]['Border color']
            self.bgcolor = Theme["Colors"]['Background color']
            self.basecolor = Theme["Colors"]['Base color']
            self.border = Theme["Properties"]["Border Thickness"]
            self.radius = Theme["Properties"]["Radius"]

    def change_Theme(self, new_theme):
        with open(f"{self.path}/Themes/{new_theme}.json", "r") as Theme:
            Theme = json.loads(Theme.read())
            Fonts = []
            for font in Theme["Fonts"]:
                Fonts.append(font)
            self.font = pygame.font.SysFont(Fonts[0], Theme["Fonts"][Fonts[0]] * self.scale)
            self.font_size = Theme["Fonts"][Fonts[0]]
            self.Sounds = {}
            for sound in Theme["Sounds"]:
                try:
                    self.Sounds[sound] = pygame.mixer.Sound(f"{self.path}/sounds/{Theme['Sounds'][sound]['name']}")
                    self.Sounds[sound].set_volume(Theme["Sounds"][sound]["volume"])
                except:
                    self.Sounds[sound] = []
                    for name in Theme['Sounds'][sound]['names']:
                        temp = pygame.mixer.Sound(f"{self.path}/sounds/{name}")
                        temp.set_volume(Theme["Sounds"][sound]["volume"])
                        self.Sounds[sound].append(temp)
            self.sound_info = Theme["Sounds"]
            self.Colors = Theme["Colors"]
            self.tcolor = Theme["Colors"]['Text color']
            self.bcolor = Theme["Colors"]['Border color']
            self.bgcolor = Theme["Colors"]['Background color']
            self.basecolor = Theme["Colors"]['Base color']
            self.border = Theme["Properties"]["Border Thickness"]
            self.radius = Theme["Properties"]["Radius"]

    def fonts(self, font_name=False, font_size=False):
        if font_name != False:
            self.font_name = font_name
        if font_size != False:
            self.font_size = font_size

        if font_name != False or font_size != False:
            self.font = pygame.font.SysFont(self.font_name, self.font_size * self.scale)

        return self.font

    def screen_info(self, screen_info=False, display=False, screen=False, scale=False):
        if screen_info != False:
            self.display = screen_info[0]
            self.screen = screen_info[1]
            self.width = self.screen[0] * 2
            self.height = self.screen[1] * 2
            self.scale = screen_info[2]
            self.font = pygame.font.SysFont(self.font_name, self.font_size * self.scale)
        if display != False:
            self.display = display
        if screen != False:
            self.screen = screen
        if scale != False:
            self.scale = scale
            self.font = pygame.font.SysFont(self.font_name, self.font_size * self.scale)
        return (self.display, self.screen, self.scale)

    def colors(self, colors=False, text_color=False, border_color=False, background_color=False, base_color=False):
        if colors != False:
            self.tcolor = colors[0]
            self.bcolor = colors[1]
            self.bgcolor = colors[2]
            self.basecolor = colors[3]
            self.Colors = {}
            self.Colors["Text color"] = self.tcolor
            self.Colors["Border color"] = self.bcolor
            self.Colors["Background color"] = self.bgcolor
            self.Colors["Base color"] = self.basecolor
        if text_color != False:
            self.tcolor = text_color
            self.Colors["Text color"] = self.tcolor
        if border_color != False:
            self.bcolor = border_color
            self.Colors["Border color"] = self.bcolor
        if background_color != False:
            self.bgcolor = background_color
            self.Colors["Background color"] = self.bgcolor
        if background_color != False:
            self.basecolor = base_color
            self.Colors["Base color"] = self.basecolor

        return (self.tcolor, self.bcolor, self.bgcolor, self.basecolor)

    def sounds(self, name=False, sound=False, volume=False):
        if name != False:
            if name in self.Sounds:
                if sound != False:
                    self.Sounds[name] = pygame.mixer.Sound("sounds/" + sound)
                    self.sound_info[name]["name"] = sound
                if volume != False:
                    if type(self.Sounds[name]) != list:
                        self.Sounds[name].set_volume(volume / 100)
                        self.sound_info[name]["volume"] = volume
                return self.Sounds[name]
        else:
            if volume != False:
                for sound in self.Sounds:
                    if type(self.Sounds[sound]) != list:
                        self.Sounds[sound].set_volume((volume / 100) * (self.sound_info[sound]["volume"] / 100))
            return self.Sounds

class Renderer:
    def __init__(self):
        self.windows = []
        self.base_window = []

    def add_window(self, window):
        self.windows.append(window)

    def remove_window(self, window):
        print(self.windows.index(window))

    def sort_windows(self, window):
        return window.last_click

    def render(self):
        self.windows.sort(key=self.sort_windows, reverse=True)
        for window in self.windows:
            if window.isActive:
                window.render()

class Layer:
    def __init__(self,app, set_order= False):
        self.app = app
        self.renderer = app.Renderer
        self.theme = app.theme
        self.display = app.theme.display
        self.screen = app.theme.screen
        self.scale = app.theme.scale
        self.Input = app.Input
        self.elements = []
        self.last_click = set_order
        self.isActive = True

        self.renderer.add_window(self)

    def add_element(self, element):
        self.elements.append(element)
        return self.elements.index(element)

    def remove_element(self, index):
        self.elements.pop(index)

    def clear(self):
        self.elements = []

    def update(self):
        for element in self.elements:
            element.update(self)

    def render(self):
        for element in self.elements:
            if element.isActive:
                element.render()
                element.isActive = False

#elements

class Box:
    def __init__(self, layer, pos, size, border_color=False, background_color=False, resize=False):
        self.window = layer
        self.renderer = layer.renderer
        self.theme = layer.theme
        self.display, self.screen, self.scale = self.theme.screen_info()
        self.tcolor, self.bcolor, self.bgcolor = self.theme.colors()[:-1]
        if border_color != False:
            self.bcolor = border_color
        if background_color != False:
            self.bgcolor = background_color

        self.init_pos = pos
        self.resize = resize
        self.isActive = False
        self.sx, self.sy = self.screen
        self.px, self.py = self.pos = pos
        self.x, self.y = self.sx + self.px * self.scale, self.sy + self.py * self.scale
        self.x2, self.y2 = self.size = size
        self.x2, self.y2 = self.x2 * self.scale, self.y2 * self.scale
        self.rect = (self.x - self.x2 / 2, self.y - self.y2 / 2, self.x + self.x2 / 2, self.y + self.y2 / 2)
        self.window.add_element(self)
    def update(self, window):
        self.pos = (self.init_pos[0] + window.pos[0], self.init_pos[1] + window.pos[1])
        if self.resize:
            scale = (window.size[0] / window.init_size[0], window.size[1] / window.init_size[1])
        else:
            scale = (1, 1)

        self.px, self.py = self.pos
        self.x, self.y = self.sx + self.px * self.scale, self.sy + self.py * self.scale
        self.x2, self.y2 = self.size
        self.x2, self.y2 = self.x2 * self.scale * scale[0], self.y2 * self.scale * scale[1]
    def render(self):
        pygame.draw.rect(self.display, self.bcolor, (self.x - self.x2 / 2, self.y - self.y2 / 2, self.x2, self.y2))
        pygame.draw.rect(self.display, self.bgcolor, ((self.x - self.x2 / 2) + self.theme.border,
                                                      (self.y - self.y2 / 2) + self.theme.border,
                                                      self.x2 - self.theme.border * 2, self.y2 - self.theme.border * 2))

class RoundBox:
    def __init__(self, layer, pos, size, radius, border_color=False, background_color=False, resize=False):
        self.window = layer
        self.renderer = layer.renderer
        self.theme = layer.theme
        self.display, self.screen, self.scale = self.theme.screen_info()
        self.tcolor, self.bcolor, self.bgcolor = self.theme.colors()[:-1]
        if border_color != False:
            self.bcolor = border_color
        if background_color != False:
            self.bgcolor = background_color

        self.init_pos = pos
        self.radius = radius
        self.resize = False
        self.isActive = False
        self.sx, self.sy = self.screen
        self.px, self.py = self.pos = pos
        self.x, self.y = self.sx + self.px * self.scale, self.sy + self.py * self.scale
        self.x2, self.y2 = self.size = size
        self.x2, self.y2 = self.x2 * self.scale, self.y2 * self.scale
        self.rect = (self.x - self.x2 / 2, self.y - self.y2 / 2, self.x + self.x2 / 2, self.y + self.y2 / 2)
        self.window.add_element(self)
    def update(self, window):
        self.pos = (self.init_pos[0] + window.pos[0], self.init_pos[1] + window.pos[1])
        if self.resize:
            scale = (window.size[0] / window.init_size[0], window.size[1] / window.init_size[1])
        else:
            scale = (1, 1)

        self.px, self.py = self.pos
        self.x, self.y = self.sx + self.px * self.scale, self.sy + self.py * self.scale
        self.x2, self.y2 = self.size
        self.x2, self.y2 = self.x2 * self.scale * scale[0], self.y2 * self.scale * scale[1]
    def render(self):
        radius = self.radius * self.scale
        pygame.draw.circle(self.display, self.bcolor,(self.x - self.x2 / 2 + radius, self.y - self.y2 / 2 + radius),radius)
        pygame.draw.circle(self.display, self.bcolor, (self.x - self.x2 / 2 + radius, self.y + self.y2 / 2 - radius),radius)
        pygame.draw.circle(self.display, self.bcolor, (self.x + self.x2 / 2 - radius, self.y - self.y2 / 2 + radius),radius)
        pygame.draw.circle(self.display, self.bcolor, (self.x + self.x2 / 2 - radius, self.y + self.y2 / 2 - radius),radius)
        pygame.draw.rect(self.display, self.bcolor, (self.x - self.x2 / 2 + radius, self.y - self.y2 / 2, self.x2 - radius*2, self.y2))
        pygame.draw.rect(self.display, self.bcolor, (self.x - self.x2 / 2, self.y - self.y2 / 2 + radius, self.x2, self.y2 - radius*2))
        border = self.theme.border*self.scale
        pygame.draw.circle(self.display, self.bgcolor,(self.x - self.x2 / 2 + radius, self.y - self.y2 / 2 + radius),radius-border)
        pygame.draw.circle(self.display, self.bgcolor, (self.x - self.x2 / 2 + radius, self.y + self.y2 / 2 - radius),radius-border)
        pygame.draw.circle(self.display, self.bgcolor, (self.x + self.x2 / 2 - radius, self.y - self.y2 / 2 + radius),radius-border)
        pygame.draw.circle(self.display, self.bgcolor, (self.x + self.x2 / 2 - radius, self.y + self.y2 / 2 - radius),radius-border)
        pygame.draw.rect(self.display, self.bgcolor, ((self.x - self.x2 / 2) + radius,(self.y - self.y2 / 2) + border, self.x2 - radius * 2 , self.y2 - border * 2))
        pygame.draw.rect(self.display, self.bgcolor, ((self.x - self.x2 / 2) + border,(self.y - self.y2 / 2) + radius, self.x2 - border * 2, self.y2 -  radius * 2))

class Text:
    def __init__(self, layer, pos, text, in_box=False, radius=False, size=(0, 0), text_color=False,
                 border_color=False, background_color=False, center="center",
                 cut_dir=False, resize=False,padding=False):
        self.render_window = layer
        self.renderer = layer.renderer
        self.theme = theme = layer.theme
        self.pos = pos
        self.in_box = in_box
        self.resize = resize
        self.display, self.screen, self.scale = theme.screen_info()
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()[:-1]
        self.radius = self.theme.radius
        self.padding = theme.border + theme.scale*2
        self.font = theme.fonts()
        self.center = center
        self.cut_dir = cut_dir
        self.isActive = False

        if text_color:
            self.tcolor = text_color
        if border_color:
            self.bcolor = border_color
        if background_color:
            self.bgcolor = background_color
        if padding:
            self.padding = padding
        if radius:
            self.radius = radius

        self.size = size
        sx, sy = self.screen
        x, y = self.pos
        self.x, self.y = sx + x * self.scale, sy + y * self.scale
        self.init_pos = (self.x, self.y)
        tx, ty = self.font.size(str(text))


        if in_box:
            print(self.radius)
            if self.radius != 0:
                self.box = RoundBox(self.render_window, self.pos, self.size, self.radius, self.bcolor, self.bgcolor, resize=self.resize)
            else:
                self.box = Box(self.render_window, self.pos, self.size, self.bcolor, self.bgcolor, resize=self.resize)
            while tx > size[0] * self.scale-self.padding*2:
                if cut_dir:
                    text = text[1:]
                else:
                    text = text[:-1]
                tx = self.font.size(str(text))[0]



        self.text = text
        self.text_pos = (tx, ty)
        self.tx, self.ty = tx, ty
        self.text_text = self.font.render(str(text), True, self.tcolor)
        self.textStartPos = get_center(self.center, self.scale,
                   (self.x - self.tx / 2 + self.padding, self.y - self.ty / 2),
                   self.tx, self.ty, self.size)
        self.textEndPos = (self.textStartPos[0]+self.font.size(self.text)[0],self.textStartPos[1]+self.font.size(self.text)[1])


        self.render_window.add_element(self)


    def update(self, window):

        if self.resize:
            scale = (window.size[0] / window.init_size[0], window.size[1] / window.init_size[1])
        else:
            scale = (1, 1)

        if self.in_box and window:
            self.box.update(window)
        #print(scale)

        self.x, self.y = (self.init_pos[0] * scale[0] + window.pos[0] * self.scale,
                          self.init_pos[1] * scale[1] + window.pos[1] * self.scale)


    def change_text(self,text):
        tx, ty = self.font.size(str(text))

        if self.in_box:
            while tx > self.size[0] * self.scale-self.padding*2:
                if self.cut_dir:
                    text = text[1:]
                else:
                    text = text[:-1]
                tx = self.font.size(str(text))[0]

        self.text = text
        self.text_pos = (tx, ty)
        self.tx, self.ty = tx, ty
        self.text_text = self.font.render(str(text), True, self.tcolor)

    def render(self, func = None):
        if self.in_box:
            self.box.render()
        self.textStartPos = get_center(self.center, self.scale,
                   (self.x - self.tx / 2 + self.padding, self.y - self.ty / 2),
                   self.tx, self.ty, self.size)
        self.textEndPos = (self.textStartPos[0]+self.font.size(self.text)[0],self.textStartPos[1]+self.font.size(self.text)[1])

        if func is not None:
            func()

        self.display.blit(self.text_text,self.textStartPos)


class TextBox:
    def __init__(self, render_window ,Input, pos, size, text, text_center="center", center="center",
                 in_box=True, default_text="", resizeable=False, maxTextLength=False, window=None, radius=False, padding=False):
        self.render_window = render_window
        self.Input = Input
        self.renderer = render_window.renderer
        self.theme = theme = render_window.theme
        self.tcolor, self.bcolor, self.bgcolor = theme.colors()[:-1]
        self.sound = theme.sounds("button")
        self.screen_info = theme.screen_info()
        self.display, self.screen, self.scale = self.screen_info
        self.in_text = False
        self.name = ""
        self.default_text = default_text
        self.text = str(text)
        self.start_pos = pos
        if window is not None:
            self.pos = window.pos[0] + pos[0], window.pos[1] + pos[1]
        else:
            self.pos = pos
        self.size = size
        self.font = theme.fonts()
        self.pointer = len(text)
        self.highLightStart = 0
        self.highLightEnd = 0
        self.highLighting = False
        self.highLightedText = ""
        self.in_box = in_box
        self.radius = radius
        self.center = center
        self.text_center = text_center
        self.resizeable = resizeable
        self.maxTextLength = maxTextLength
        self.window = window
        self.padding = theme.border + theme.scale*2
        if padding:
            self.padding = padding
        self.isActive = False
        self.cursor = ((0, 0), (0, 0))
        self.guiText = Text(self.render_window, pos, text, self.in_box, radius=self.radius,
             size=self.size, background_color=self.bgcolor,center=self.text_center,padding=self.padding)
        self.render_window.add_element(self)

    def update(self):
        if self.window is not None:
            self.pos = self.window.pos[0] + self.start_pos[0], self.window.pos[1] + self.start_pos[1]

        sound = self.sound
        sx, sy = self.screen
        x, y = self.pos
        x, y = sx + x * self.scale, sy + y * self.scale
        size_x, size_y = self.size
        x2, y2 = size_x * self.scale, size_y * self.scale
        mx, my, mb = self.Input.mouse()
        mods = self.Input.mods
        bgcolor = self.bgcolor
        if x - x2 / 2 < mx < x + x2 / 2 and y - y2 / 2 < my < y + y2 / 2:
            r, g, b = bgcolor
            if r - 16 < 0:
                r = 0
            else:
                r -= 16
            if g - 16 < 0:
                g = 0
            else:
                g -= 16
            if b - 16 < 0:
                b = 0
            else:
                b -= 16
            bgcolor = r, g, b
            if mb == 1:
                if self.text == self.default_text:
                    self.text = ""
                if sound != False:
                    pygame.mixer.Sound.play(sound)
                self.in_text = True

        else:
            if mb == 1:
                self.in_text = False
                if self.text == "":
                    self.text = self.default_text
                self.highLighting = False

        if self.in_text:
            # split text at cursor
            if self.pointer == 0:
                text1 = ""
                text2 = self.text
            else:
                text1 = self.text[:self.pointer]
                text2 = self.text[self.pointer:]
            for key in self.Input.keys:
                # backsapce
                if key == 8:
                    text1 = text1[:-1]
                    self.text = text1 + text2
                    if self.pointer > 0:
                        self.pointer -= 1

                    # print(self.pointer)
                # delete
                elif key == 127:
                    text2 = text2[1:]
                    self.text = text1 + text2
                    max = len(self.text)
                    if self.pointer > max:
                        self.pointer = max
                    # print(self.pointer)
                # enter
                elif key == 13 or key == 27:
                    self.in_text = False
                    if self.text == "":
                        self.text = self.default_text

                # left arrow
                elif key == 1073741904:
                    if self.pointer > 0:
                        self.pointer -= 1

                    # print(self.pointer)
                # right arrow
                elif key == 1073741903:
                    max = len(self.text)
                    self.pointer += 1
                    if self.pointer > max:
                        self.pointer = max
                    # print(self.pointer)
                # ctrl-v
                elif key == 118 and "CTRL" in mods:
                    print("ctrl-v")
                    data = pyperclip.paste()

                    self.text = text1 + data + text2
                    self.pointer = len(text1 + data)
                # ctrl-c
                elif key == 99 and "CTRL" in mods:
                    print("ctrl-c")
                    pyperclip.copy(self.text)
                # ctrl-x
                elif key == 120 and "CTRL" in mods:
                    print("ctrl-x")
                    pyperclip.copy(self.text)
                    self.text = ""
                # ctrl-delete
                elif key == 127 and "CTRL" in mods:
                    self.text = ""

                # add key to text
                else:
                    for key in self.Input.unicode:
                        textX, textY = self.font.size(self.text)
                        if self.maxTextLength != False:
                            if textX + 20 < self.maxTextLength-self.padding*2:
                                text1 = text1 + key
                                textX, textY = self.font.size(text1 + text2)
                                if textX + 10 > self.maxTextLength:
                                    text1 = text1[:-1]
                                self.text = text1 + text2
                        else:
                            self.text = text1 + key + text2
                        self.pointer+=1

            _text = self.text
            textX, textY = self.font.size(_text)
            textOffset = self.font.size(self.text[:-len(_text)])
            self.guiText.pos = self.pos
            self.guiText.change_text(self.text)

            t1x, t1y = self.font.size(text1)
            t1x -= (textX + textOffset[0]) / 2 + textOffset[0] / 2
            if t1x > (self.size[0] * self.scale) / 2 - self.theme.border * self.scale:
                t1x = (self.size[0] * self.scale) / 2 - self.theme.border * self.scale

            t1x = self.guiText.textStartPos[0]+self.font.size(text1)[0]

            self.cursor = ((t1x, y + t1y / 2.5), (t1x, y - t1y / 2.5))

            # set pointer on mouse click
            if x - x2 / 2 < mx < x + x2 / 2 and y - y2 / 2 < my < y + y2 / 2 and mb == 1:
                self.Input.clicked()
                index = 0
                _text = self.text + " "
                startx = self.guiText.textStartPos[0]
                if len(self.text) != 0:
                    while index < len(_text):
                        tx = self.font.size(_text[:index])[0]
                        charRound = self.font.size(_text[index])[0]/2
                        xpos = startx + tx
                        if xpos-charRound < mx < xpos+charRound:
                            self.pointer = index
                            self.highLightStart = index
                        elif index == 0 and mx < xpos+charRound:
                            self.pointer = index
                            self.highLightStart = index
                        elif index == len(_text)-1 and xpos-charRound < mx:
                            self.pointer = index
                            self.highLightStart = index

                        index += 1
            #highlighter
            if x - x2 / 2 < mx < x + x2 / 2 and mb == -1:
                index = 0
                startx = self.guiText.textStartPos[0]
                _text = self.text + " "
                if len(self.text) != 0:
                    while index < len(_text):
                        tx = self.font.size(_text[:index])[0]
                        charRound = self.font.size(_text[index])[0]/2
                        xpos = startx + tx
                        if xpos-charRound < mx < xpos+charRound:
                            if index !=self.pointer:
                                self.highLighting = True
                            self.highLightEnd = index
                            self.pointer = index
                        elif index == 0 and mx < xpos+charRound:
                            if index !=self.pointer:
                                self.highLighting = True
                            self.highLightEnd = index
                            self.pointer = index
                        elif index == len(_text)-1 and xpos-charRound < mx:
                            if index !=self.pointer:
                                self.highLighting = True
                            self.highLightEnd = index
                            self.pointer = index
                        index += 1
            if self.highLightStart<self.highLightEnd:
                self.highLightedText = self.text[self.highLightStart:self.highLightEnd]
            else:
                self.highLightedText = self.text[self.highLightEnd:self.highLightStart]


        else:
            _text = self.text
            tx, ty = self.font.size(_text)
            if self.maxTextLength != False:
                while tx + 10 > x2-self.padding*2:
                    _text = _text[1:]
                    tx, ty = self.font.size(_text)
            self.guiText.change_text(_text)

    def get_text(self):
        return str(self.text)

    def change_text(self, text):
        p_text = self.text
        self.text = str(text)
        self.guiText.change_text(text)
        return str(p_text)

    def highlight(self):
        if self.highLighting and self.highLightStart != self.highLightEnd:
            thickness = self.font.size(self.text)[1]
            startx = self.guiText.textStartPos[0] + self.font.size(self.text[:self.highLightStart])[0]
            endx = self.guiText.textStartPos[0] + self.font.size(self.text[:self.highLightEnd])[0]
            y = self.screen[1] + self.pos[1] * self.scale
            pygame.draw.line(self.display, (33, 66, 131), (startx,y), (endx,y), thickness)

    def render(self):
        self.guiText.render(self.highlight)
        start,end = self.cursor
        if self.Input.cursor() and self.in_text:
            pygame.draw.line(self.display, self.tcolor, start,end,
                             self.scale)


