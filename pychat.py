#version 0.0.6
import os.path
import traceback

import Network as N
import my_gui_2 as gui


if __name__ == "__main__":
    app = gui.App("PyChat")
    main_window = app.Main_window
    debug_window = app.Debug_window
    main_screen = ["main_menu"]
    sub_screen = ["main"]
    n = N.Network()
    text = gui.Text(main_window,(0,0),"hello world!",(200,20))
    text2 = gui.Text(main_window, (app.screen[0]/app.config.scale-50,app.screen[1]/app.config.scale-10 ), "Hey Djo!",(100, 20))
    textbox = gui.TextBox(app,main_window, (0,50),(200,20),"",text_center="left",default_text="enter text here")
    button1 = gui.Button(app,main_window,(0,-50),(200,20),"Press me!")

    #debug
    fps_ui = gui.Text(debug_window, (-app.config.current_w / (2 * app.config.scale)
                                              , -app.config.current_h / (2 * app.config.scale) + 10), "fps:", center="left")
    keys_pressed = gui.Text(debug_window, (-app.config.current_w / (2 * app.config.scale)
                                              , -app.config.current_h / (2 * app.config.scale) + 30), "keys:", center="left" )
    mouse_info = gui.Text(debug_window, (-app.config.current_w / (2 * app.config.scale)
                                              , -app.config.current_h / (2 * app.config.scale) + 50), "Mouse Info:",center="left")
    active_elements = gui.Text(debug_window, (-app.config.current_w / (2 * app.config.scale)
                                              , -app.config.current_h / (2 * app.config.scale) + 70), "Active Elements:", center="left" )

    userLogin = False
    sent = False

    while not app.quit:
        app.update()
        try:
            for key in app.Input.keys:
                if key == 1073741884:
                    if not debug_window.show:
                        debug_window.show = True
                    else:
                        debug_window.show = False



            #print(main_screen[-1],sub_screen[-1])
            match main_screen[-1]:
                case "load_user":
                    match sub_screen[-1]:
                        case "main":
                            if os.path.exists("user.txt"):
                                with open("user.txt", "r") as f:
                                    userId = f.readline().split(",")[1]
                                    userPw = f.readline().split(",")[1]
                            else:
                                #with open("user.txt", "w") as f:
                                #    f.writelines("userId,None\n,userPw,None\n")
                                loginWindow = gui.DisplayWindow(app, main_window,(0,0), (200,200),"Login")
                                user_name = gui.TextBox(app, loginWindow, (0,0),(180,20),"He ha",text_center="left")
                                labelThing = gui.Label(app,loginWindow,(0,25),user_name,"hehe",in_box=True,size=(180,20))

                                main_screen = ["login"]

                            text.change_text("Connecting...")
                            if not n.is_connected():
                                n.connect()
                            else:
                                text.change_text("Checking user ID...")
                                sub_screen = ["login"]
                        case "login":
                            if not sent:
                                n.send({"packet": "checkId","userId": userId})
                                sent = True
                            data = n.receive("checkId")
                            if data is not None:
                                sent = False
                                if int(data["status"]) == 0:
                                    text.change_text("Logging in...")
                                    sub_screen = ["password"]
                                if int(data["status"]) != 0:
                                    text.change_text("Bad ID")
                                    main_screen = ["login"]
                        case "password":
                            if not sent:
                                n.send({"packet": "userLogin", "userPw": userPw})
                                sent = True
                            data = n.receive("userLogin")
                            if data is not None:
                                sent = False
                                if data["status"] == 0:
                                    userLogin = True
                                    sub_screen = ["main"]
                                    main_screen = ["main_menu"]
                case "login":
                    pass


    
                case "main_menu":
                    if not userLogin:
                        main_screen = ["load_user"]
                    #main_screen = ["login"]

                case _:
                    pass

            fps_ui.change_text(f"FPS:{app.fps}")
            keys_pressed.change_text(f"Keys:{app.Input.keys_pressed_raw()}")
            mouse_info.change_text(f"Mouse Info:{app.Input.mouse_info}")
            active_elements.change_text(f"Active Elements:{app.render()}")

        except Exception as e:
            traceback.print_exc()
            text.change_text("error")

    app.Quit()
    print("done")