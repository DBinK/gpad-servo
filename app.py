from flask import Flask
import threading

app = Flask(__name__)
# 在控制台监听按键输入的线程函数
def console_input_thread():

    user_input = input("输入指令: ")
    if user_input.lower() == 'q':
        print("q")
    if user_input.lower() == 'm':
        print("m")

# 启动控制台输入监听线程
input_thread = threading.Thread(target=console_input_thread)
input_thread.start()

# Flask路由
@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()

# 等待控制台输入线程结束
input_thread.join(