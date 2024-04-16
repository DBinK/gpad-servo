import keyboard

def on_key_press(event):
    if event.name == 'a':
        # 按下a键执行的程序
        print("按下了a键")
    elif event.name == 'b':
        # 按下b键执行的程序
        print("按下了b键")

keyboard.on_press(on_key_press)
keyboard.wait()