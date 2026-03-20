import os.path
import subprocess
import Network as N
import my_gui_2 as gui
from my_gui_2 import active


def sumfunc(text):
    print(text)


if __name__ == "__main__":
    app = gui.App("PyChat")
    main_window = app.Main_window
    debug_window = app.Debug_window
    main_screen = ["main_menu"]
    sub_screen = ["main"]
    n = N.Network()
    text = gui.Text(main_window,(0,0),"hello world!",in_box=True,size=(200,20))
    text2 = gui.Text(main_window, (app.screen[0]/app.config.scale-50,app.screen[1]/app.config.scale-10 ), "Hey Djo!", in_box=True, size=(100, 20))
    textbox = gui.TextBox(main_window,app.Input, (0,50),(200,20),"",text_center="left",default_text="enter text here")
    button1 = gui.Button(main_window,app.Input,(0,-50),(200,20),"Press me!")


    userLogin = False
    sent = False

    while not app.quit:
        app.update()
        try:
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
                                with open("user.txt", "w") as f:
                                    f.writelines("userId,None\n,userPw,None\n")
                                main_screen = ["login"]
                                loginWindow = gui.DisplayWindow(main_window,(0,0), (200,200))

                            text.change_text("Connecting...")
                            active(text)
                            if not n.is_connected():
                                n.connect()
                            else:
                                text.change_text("Checking user ID...")
                                sub_screen = ["login"]
                        case "login":
                            active(text)
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
                            active(text)
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
                    loginWindow.update()



    
                case "main_menu":
                    if not userLogin:
                        main_screen = ["load_user"]
                    main_screen = ["login"]

                case _:
                    pass

            app.render()
        except:
            pass

    app.Quit()
    print("done")