import random
import time
import ctypes
import os
import time
from vulkan import *
import json

import my_gui as gui
import math
import os
import traceback
import ctypes

import Network as N
import PyChat



def load_config():
    try:
        with open("conf.json", "r") as conf:
            config_ = json.loads(conf.read())
        config = {}
        config["scale"] = config_["scale"]
        config["current_w"], config["current_h"] = config_["screen size"]
        config["screen mode"] = config_["screen mode"]
        config['main_display'] = config_["main_display"]
        config['theme'] = config_["theme"]
        config["volume"] = config_["volume"]
        config["target_fps"] = config_["target_fps"]
        return config
    except:
        config = {}
        config["current_w"], config["current_h"] = 1920,1080
        config["scale"] = 2
        config["screen mode"] = "Windowed"
        config['main_display'] = 0
        config['theme'] = "Default theme"
        config["volume"] = 100
        config["target_fps"] = 20
        return config

class user_class:
    def __init__(self):
        self.name = "No Name"
        self.position = 0
        self.color1 = (255, 0, 0)
        self.color2 = (0, 255, 0)
        self.color3 = (0, 0, 255)
        self.highScores = {}
        self.playTime = {}
        self.currentGames = {}

    def load_user(self,player):
        with open(f"playerdata/{player}.json","r") as player_info:
            player_info = json.loads(player_info.read())
        self.name = player_info["name"]
        self.position = player_info["position"]
        self.color1 = player_info["color1"]
        self.color2 = player_info["color2"]
        self.color3 = player_info["color3"]
        self.highScores = player_info["scores"]
        self.playTime = player_info["playtime"]

    def save_user(self):
        with open(f"playerdata/{self.name}.json","w") as player_info:
            dict_player = {}
            dict_player["name"] = self.name
            dict_player["position"] = self.position
            dict_player["color1"] = self.color1
            dict_player["color2"] = self.color2
            dict_player["color3"] = self.color3
            dict_player["scores"] = self.highScores
            playtime = {}
            for each in self.playTime:
                playtime[each] = round(self.playTime[each],2)
            dict_player["playtime"] = playtime
            player_info.write(json.dumps(dict_player))


#init pygame
pygame.init()
pygame.mixer.init()
pygame.font.init()

App_Name = "Sbeve chat"

pygame.display.set_caption(App_Name)

#init some vars
p_frame = time.perf_counter()
fps = 0
menu_fps = 20
game_fps = 60
done = False
debug = False
setting = False
reset_screen = False
check_settings = False
resolutions = ("3840x2160","1560x1600","2560x1440","1920x1440","1920x1200","1920x1080","1680x1050","1600x1200","1600x1024","1600x900","1440x900","1366x768","1360x768","1280x1024","1280x960","1280x800","1280x768","1280x720","1152x864","1024x768","800x600")
frame = 0

if __name__ == "__main__":
    try:
         ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

    config = load_config()
    theme = gui.Theme()
    theme.load_Theme(config)
    current_w = config["current_w"]
    current_h = config["current_h"]
    screen_mode = config["screen mode"]
    main_display = config["main_display"]
    volume = config["volume"]
    theme.sounds(volume=volume)
    Renderer = gui.Renderer(theme)
    Input = gui.Input()
    Main_window = gui.Layer(Renderer, Input, set_order=0)
    Debug_window = gui.Layer(Renderer, Input, set_order=-1)


    scale = config["scale"]
    tcolor, bcolor, bgcolor = theme.colors()

    main_screen = ["boot"]
    sub_screen = ["main"]

    if screen_mode == "Fullscreen":
        flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        print("Fullscreen")
    elif screen_mode == "Borderless":
        flags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
        print("Borderless")
    else:
        flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
        print("Windowed")
    display = pygame.display.set_mode((current_w, current_h), flags, vsync=1, display=main_display)
    print(current_w, current_h)
    screen = (current_w / 2, current_h / 2)
    screen_info = (display, screen, scale)
    theme.screen_info(screen_info)
    popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),f"{App_Name}™ © Patent Pending Sbeve Co. Inc LLC")
    volume_gui = gui.Slider(Main_window, (0, 0), (100, 15), "right", Input, volume)

    while not done:
#check if the scale has changed
        if reset_screen:
            reset_screen = False
            if screen_mode == "Fullscreen":
                flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                print("Fullscreen")
            elif screen_mode == "Borderless":
                flags = pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
                print("Borderless")
            else:
                flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
                print("Windowed")
            display = pygame.display.set_mode((current_w, current_h), flags, vsync=1, display=main_display)
            print(current_w, current_h)
            screen = (current_w / 2, current_h / 2)
            screen_info = (display, screen, scale)
            theme.screen_info(screen_info)
            theme.sounds(volume=volume)


    #user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.VIDEORESIZE:
                reset_screen = True
                current_w = event.w
                current_h = event.h

            Input.get_input(event,frame)
        Input.update(frame)

        if main_screen == []:
            main_screen = ["main_menu"]
        if sub_screen == []:
            sub_screen = ["main"]

        for key in Input.keys:
            if key == 27:
                Input.capture_mouse = False
                pygame.mixer.Sound.play(theme.sounds("button"))
                if main_screen[-1] == "main_menu" and main_screen[-1] != "settings":
                    main_screen.append("settings")
                    sub_screen = ["main"]
                else:
                    if sub_screen[-1] != "main":
                        sub_screen.pop()
                    else:
                        main_screen.pop()

            if key == 1073741884:
                if not debug:
                    debug = True
                    gui.LabelValue(Debug_window, (0-current_w/(2*scale), 0-current_h/(2*scale)), "ping=", "no network", center = "top_left", in_box = False)
                    gui.LabelValue(Debug_window, (0-current_w/(2*scale), 15-current_h/(2*scale)), "fps=", f"{round(fps,2)}/{config['target_fps']}", center ="top_left", in_box = False)
                    gui.LabelValue(Debug_window, (0 - current_w / (2 * scale), 30 - current_h / (2 * scale)), "Active Keys=",Input.Keys_pressed,center="top_left", in_box=False)
                    gui.LabelValue(Debug_window, (0 - current_w / (2 * scale), 45 - current_h / (2 * scale)), "Mouse",Input.mouse(),center="top_left", in_box=False)
                    gui.line(Debug_window,"line1", (255, 0, 0), (0, screen[1]), (screen[0] * 2, screen[1]))
                    gui.line(Debug_window,"line2", (255, 0, 0), (screen[0], 0), (screen[0], screen[1] * 2))
                else:
                    debug = False
                    Debug_window.clear()

            if key == 1073741892:
                if screen_mode == "Fullscreen":
                    screen_mode = "Windowed"
                else:
                    screen_mode = "Fullscreen"
                reset_screen = True


#main screen

        display.fill((0, 0, 0))
#main menu
        try:
            match main_screen[-1]:
                case "boot":
                    n = N.Network()
                    n.connect()
                    user = user_class()
                    user.load_user("steve")

                    if n.is_connected():
                        pychat = PyChat.chat(Main_window, n, Input, user)
                        main_screen = ["main_menu"]


                case "main_menu":
                    temp = theme.font
                    theme.font = pygame.font.SysFont("impact", 30 * scale)
                    Title = gui.Label(Main_window, (0, -current_h / (2 * scale) + 50), App_Name, in_box=True, size=(350, 40))
                    Title.render()
                    theme.font = temp
                    match sub_screen[-1]:
                        case "main":
                            if gui.button(Main_window, (0, 75), (100, 20), "Settings", Input):
                                main_screen.append("settings")

                            if gui.button(Main_window, (0, 100), (100, 20), "Quit", Input):
                                done = True
                        case _:
                            pass

#setting screen
                case "settings":
                    match sub_screen[-1]:
                        case "main":
                            if gui.button(Main_window, (0, 25), (100, 20), "Video Setting", Input):
                                sub_screen.append("Video Setting")
                                scale_box = gui.Label_text(Main_window, (60, 0), (100, 20), "GUI Scale", scale)
                                screen_size = gui.multiple_choice_input(Main_window, (60, -25), (100, 20), 'Resolution', str(current_w) + "x" + str(current_h), resolutions, 5)
                                window_modes = ["Fullscreen", "Windowed", "Borderless"]
                                window_mode = gui.multiple_choice_input(Main_window, (60, 25), (100, 20), 'Window Mode', screen_mode, window_modes, 5)

                            if gui.button(Main_window, (0, 50), (100, 20), "New Theme", Input):
                                sub_screen.append("Edit Theme")
                                name = gui.Label_text(Main_window,(60,-50),(100,20),"Theme Name","Enter Name")
                                t_color = gui.color_picker(Main_window, (60, -25), (100, 20), "Text color", color=tcolor)
                                b_color = gui.color_picker(Main_window, (60, 0), (100, 20), "Text border", color=bcolor)
                                bg_color = gui.color_picker(Main_window, (60, 25), (100, 20), "Text background", color=bgcolor)

                            if gui.button(Main_window, (0, 0), (100, 20), "Manage Themes", Input):
                                sub_screen.append("Themes")

                            if gui.button(Main_window, (0, -25), (100, 20), "Audio Setting", Input):
                                sub_screen.append("audio")

                        case "audio":
                            gui.LabelValue(Main_window,(0,25),"Volume = ", volume,in_box = True,size = (100,20))
                            volume_gui.update()
                            v = int(volume_gui.value*100)
                            theme.sounds(volume=v)
                            volume = v

                        case "Video Setting":
                            gui.Label_text.update(scale_box,Input)
                            screen_size.update(Input)
                            window_mode.update(Input)

                            if gui.button(Main_window, (0, current_h/(2*scale)-65), (100, 20), "Apply", Input):
                                if gui.get_text(scale_box).isnumeric():
                                    if int(gui.get_text(scale_box)) < 10:
                                        scale = int(gui.get_text(scale_box))
                                else:
                                    popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25),(0, -current_h / (2 * scale) + 15), 2, 10, (-1, 15),f"Try again, Djoman")
                                    continue
                                w,h = gui.get_text(screen_size).split("x")
                                current_w, current_h = int(w),int(h)
                                screen_mode = gui.get_text(window_mode)
                                print(screen_mode)
                                reset_screen = True
                                check_settings = True
                                continue

                        case "Themes":
                            path = theme.path
                            Themes = os.listdir(f"{path}/Themes")
                            new_Theme = config["theme"]
                            pos = -math.floor(len(Themes) / 2) * 25
                            for Theme in Themes:
                                Theme = Theme[:-5]
                                theme.change_Theme(Theme)
                                theme.sounds(volume=volume)
                                if gui.button(Main_window, (0, pos), (100, 20), Theme, Input):
                                    config["theme"] = Theme
                                if gui.button(Main_window, (-100, pos), (60, 20), "Edit", Input):
                                    edit_theme = gui.Theme()
                                    edit_theme.load_Theme(config,Theme)
                                    name = gui.Label_text(Main_window,(60,-50),(100,20),"Theme Name",Theme)
                                    t_color = gui.color_picker(Main_window, (60, -25), (100, 20), "Text color", edit_theme.tcolor)
                                    b_color = gui.color_picker(Main_window, (60, 0), (100, 20), "Text border", edit_theme.bcolor)
                                    bg_color = gui.color_picker(Main_window, (60, 25), (100, 20), "Text background", edit_theme.bgcolor)
                                    sub_screen.append("Edit Theme")
                                if gui.button(Main_window, (100, pos), (60, 20), "Remove", Input):
                                    if gui.alert(Main_window, (0, 0), (150, 100), f"Are you sure you want to PERMANENTLY delete {Theme} forever!", "Yes", "No", Input, frame):
                                                popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25),(0, -current_h / (2 * scale) + 15), 2, 3, (300, 15),f"{Theme} has been deleted!")
                                                os.remove(f"{path}/Themes/{Theme}.json")
                                                Themes.remove(f"{Theme}.json")
                                                print(Themes)
                                                config["theme"] = new_Theme = Themes[0][:-5]
                                pos += 25
                            theme.change_Theme(new_Theme)

                        case "Edit Theme":
                            name.update(Input)
                            tcolor = t_color.get_color(Input)
                            bcolor = b_color.get_color(Input)
                            bgcolor = bg_color.get_color(Input)

                            if gui.button(Main_window, (0, 50), (100, 20), "Font", Input):
                                all_fonts = os.listdir(r'C:\Windows\fonts')
                                fonts = []
                                for font in all_fonts:
                                    if font[-3:] == "ttf":
                                        fonts.append(font[:-4])
                                fonts = gui.multiple_choice_input(Main_window,(0,0),(100,20),"font",theme.font_name,fonts,20)
                                font_size = gui.Label_text(Main_window,(0,25),(100,20),"Font Size",12)
                                main_screen.append("fonts")

                            if gui.button(Main_window, (0, current_h / (2 * scale) - 65), (100, 20), "Save Theme", Input):
                                new_theme = gui.Theme()
                                new_theme.screen_info(screen_info)
                                new_theme.colors((tcolor, bcolor, bgcolor))
                                new_theme.sound_info = theme.sound_info
                                new_theme.font_name = theme.font_name
                                new_theme.font_size = theme.font_size
                                try:
                                    with open("Themes//" + str(name.text) + ".json", "w") as file:
                                        file.write(json.dumps(new_theme.save_Theme()))
                                        sub_screen.pop()
                                    reset_screen = True
                                except Exception as e:
                                    traceback.print_exc()
                                    popUp = gui.pop_up(Main_window,(0,-current_h/(2*scale)-25),(0,-current_h/(2*scale)+15),2,3,(300,15),f"Unable to save {name.text}. Error : {e}")
                        case _:
                            pass
                    gui.Label(Main_window, (0, -current_h / (2 * scale) + 75), "Settings", in_box=True, size=(150, 20))

                    if gui.button(Main_window, (0, current_h / (2 * scale) - 40), (100, 20), "Quit To Desktop", Input):
                        done = True

                    if gui.button(Main_window, (0, current_h / (2 * scale) - 15), (100, 20), "Back", Input):
                        if sub_screen[-1] == "main":
                            main_screen.pop()
                        else:
                            sub_screen.pop()
                            theme.sounds(volume=volume)


                case _:
                    if main_screen[-1] != "settings":
                        popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3,
                                           (300, 15), "error 404; " + main_screen[-1] + " not found")
                        main_screen.pop()



        except Exception as e:
            traceback.print_exc()
            if main_screen == []:
                main_screen.append("main_menu")
            elif sub_screen == []:
                sub_screen.append("main")
            else:
                popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 10, (-1, 15),f"Error in {main_screen[-1],sub_screen[-1]}. Error : {e}")
                print(theme.sounds("Errors"))
                if theme.sounds("Errors") != None:
                    pygame.mixer.Sound.play(theme.sounds("Errors")[random.randrange(0,len(theme.sounds("Errors")))])
                if sub_screen == "main":
                    main_screen.pop()
                else:
                    sub_screen.pop()


#debug screen
        if debug:
            Debug_window.elements["fps="].change_value(f"{round(fps,2)}/{config['target_fps']}")
            Debug_window.elements["Active Keys="].change_value(Input.Keys_pressed)
            Debug_window.elements["Mouse"].change_value(Input.mouse())

        # pop ups
        popUp.update()
        Renderer.render()
        try:
            time.sleep((p_frame+1/config["target_fps"])-time.perf_counter())
        except:
            pass
        fps = 1 / (time.perf_counter() - p_frame)
        p_frame = time.perf_counter()
        pygame.display.update()
        frame+=1

# make sure that video setting are usable
        if check_settings:
            check_settings = False
            if gui.alert(Main_window, (0, 0), (150, 100), "Do you want to save these settings?", "Yes", "No", Input, frame, 15):
                config["scale"] = scale
                config["screen size"] = [current_w, current_h]
                with open("conf.json", "w") as conf:
                    conf.write(json.dumps(config))
                popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3,
                                   (300, 15), "Setting Updated")
                sub_screen.pop()
            else:
                config = load_config()
                current_w = config["current_w"]
                current_h = config["current_h"]
                screen_mode = config["screen mode"]
                main_display = config["main_display"]
                scale = config["scale"]
                reset_screen = True
                popUp = gui.pop_up(Main_window, (0, -current_h / (2 * scale) - 25), (0, -current_h / (2 * scale) + 15), 2, 3,
                                   (300, 15), "Setting Reverted")

#exit code
config["screen mode"] = screen_mode
config["scale"] = scale
config["screen size"] = [current_w,current_h]
config.pop("current_w")
config.pop("current_h")
config["volume"] = volume


with open("conf.json", "w") as conf:
    conf.write(json.dumps(config))


pygame.quit()
time.sleep(0.2)
print("done")