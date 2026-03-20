import subprocess
import Network as N
import my_gui_2 as gui
from my_gui_2 import active

if __name__ == "__main__":
    app = gui.App("PyChat")
    main_window = app.Main_window
    main_screen = ["main_menu"]
    sub_screen = ["main"]
    n = N.Network()
    text = gui.Text(main_window,(0,0),"hello world!",in_box=True,size=(200,20))
    text2 = gui.Text(main_window, (app.screen[0]/app.config.scale-50,app.screen[1]/app.config.scale-10 ), "Hey Djo!", in_box=True, size=(100, 20))
    textbox = gui.TextBox(main_window,app.Input, (0,50),(200,20),"",text_center="left",default_text="enter text here")
    button1 = gui.Button(main_window,app.Input,(0,-50),(200,20),"Press me!")
    with open("user.txt","r") as f:
        userId = f.readline().split(",")[1]
        userPw = f.readline().split(",")[1]

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



    
                case "main_menu":
                    if not userLogin:
                        main_screen = ["load_user"]

                case _:
                    pass

            app.render()
        except:
            pass

    app.Quit()
    print("done")