import os
import socket
import flask
import requests
import threading
import tkinter as tk

# 全局变量
SF_LID = os.environ["SF_LID"]
SF_HOSTNAME = os.environ["SF_HOSTNAME"]

# 定义窗口
win = tk.Tk()
win.title("SFChat 客户端")
win.geometry("600x500")
win.resizable(False, False)

# 定义服务器
app = flask.Flask(__name__)

# 定义区域
top_frame = tk.Frame(win)
center_frame = tk.Frame(win)
left_frame = tk.Frame(center_frame)
right_frame = tk.Frame(center_frame)

top_frame.place(width=600, height=100, x=0, y=0)
center_frame.place(width=600, height=400, x=0, y=100)
left_frame.place(width=200, height=400, x=0, y=0)
right_frame.place(width=400, height=400, x=200, y=0)

top_frame.rowconfigure(0, minsize=50)
top_frame.rowconfigure(1, minsize=50)


# top_frame (function)
def connect_backend():
    print(backend_name.get())


# top_frame
top_row1_wrapper = tk.Frame(top_frame)
top_row2_wrapper = tk.Frame(top_frame)

top_row1_wrapper.grid(row=0, column=0, padx=10, sticky="nsew")
top_row2_wrapper.grid(row=1, column=0, padx=10, sticky="nsew")

top_row1_wrapper.rowconfigure(0, minsize=50)
top_row2_wrapper.rowconfigure(0, minsize=50)

backend_name = tk.StringVar()
backend_url = tk.StringVar()
is_connected = tk.StringVar()

backend_url.set("未连接")
is_connected.set("无法获取")

tk.Label(top_row1_wrapper, text="客户机:").grid(row=0, column=0)
tk.Label(top_row1_wrapper, text=SF_HOSTNAME, bg="gray").grid(row=0, column=1)
tk.Label(top_row1_wrapper, text="主机:").grid(row=0, column=2)
tk.Entry(top_row1_wrapper, textvariable=backend_name).grid(row=0, column=3)
tk.Button(top_row1_wrapper, text="连接", command=connect_backend).grid(row=0, column=4)

tk.Label(top_row2_wrapper, text="状态:").grid(row=0, column=0)
tk.Label(top_row2_wrapper, textvariable=is_connected, bg="gray").grid(row=0, column=1)
tk.Label(top_row2_wrapper, text="后端地址:").grid(row=0, column=2)
tk.Label(top_row2_wrapper, textvariable=backend_url, bg="gray").grid(row=0, column=3)

# left_frame
onlineList = tk.Variable()
onlineList.set([])

onlines = tk.Listbox(left_frame)
onlines.place(width=200, height=400, x=0, y=0)


# left_frame (function)
def update_onlines(*args):
    onlines.delete(0, "end")
    for name in onlineList.get():
        onlines.insert("end", name)


onlineList.trace_add("write", update_onlines)


# right_frame (function)
def to():
    print(input_str.get())


# right_frame
input_str = tk.StringVar()
msgList = tk.Variable()

input_str.set("")
msgList.set([])

msg_box = tk.Text(right_frame, highlightthickness=0)
msg_box.place(width=400, height=350, x=0, y=0)

tk.Entry(right_frame, textvariable=input_str).place(width=350, height=50, x=0, y=350)
tk.Button(right_frame, text="发送", command=to).place(width=50, height=50, x=350, y=350)


# right_frame (function)
def update_msg_box(*args):
    msg_box.delete("1.0", "end")
    for msg in msgList.get():
        msg_box.insert("end", msg + "\n")


msgList.trace_add("write", update_msg_box)


# 随机端口
def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return int(port)


if __name__ == "__main__":
    port = get_free_port()

    os.system(
        "echo '%s:%s' > %s/chat_sub_address "
        % (
            "lg-%s.sf-guest" % SF_LID,
            port,
            "/everyone/" + SF_HOSTNAME,
        )
    )

    # 启动服务器
    threading.Thread(
        target=app.run,
        kwargs={
            "debug": False,
            "host": "0.0.0.0",
            "port": port,
            "threaded": True,
        },
        daemon=True,
    ).start()

    # 显示窗口
    win.mainloop()
