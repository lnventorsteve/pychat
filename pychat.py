
import Network as N
import my_gui_2 as gui
from my_gui_2 import active

if __name__ == "__main__":
    app = gui.App("PyChat")

    main_window = app.Main_window
    main_screen = ["load_user"]
    sub_screen = ["main"]
    n = N.Network()
    text = gui.Text(main_window,(0,0),"hello world!",in_box=True,size=(200,20))
    text2 = gui.Text(main_window, (app.screen[0]/app.config.scale-50,app.screen[1]/app.config.scale-10 ), "Hey Djo!", in_box=True, size=(100, 20))
    textbox = gui.TextBox(main_window,app.Input, (0,50),(200,20),"",text_center="left",default_text="enter text here")

    user_login = False
    
    
    
    
    
    while not app.quit:
        app.update()
        active(text)
        active(text2)
        textbox.update()
        active(textbox)
        app.render()
        try:
            match main_screen[-1]:
                case "load_user":
                    match sub_screen[-1]:
                        case "main":
                            if not n.is_connected():
                                pass
                                #n.connect()
    
                case "main_menu":
                    pass
        except:
            pass

    app.Quit()
    print("done")