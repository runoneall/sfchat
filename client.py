import os
import socket
import flask
import requests
import threading
import queue
import tkinter as tk
from tkinter import messagebox

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
    name = backend_name.get()
    server_file = f"/everyone/{name}/chat_server_address"

    backend_url.set("无法获取")
    is_connected.set("未连接")

    if not os.path.exists(server_file):
        messagebox.showerror("后端未开启", f"找不到 {server_file}")
        return

    with open(server_file, "r", encoding="utf-8") as f:
        url = "http://" + f.read().replace("\n", "")

    # 尝试连接
    try:
        resp = requests.get(f"{url}/ping")
        if resp.status_code != 200 or resp.text != "pong":
            messagebox.showerror("后端未开启", f"无法测试连接 {url}/ping")
            return

        resp = requests.get(f"{url}/sub/add?name={SF_HOSTNAME}")
        if resp.status_code != 200:
            messagebox.showerror("无法注册", f"无法注册此客户机 {resp.status_code}")
            return

    # 连接失败
    except:
        messagebox.showerror("后端未开启", f"无法连接到 {url}")
        return

    backend_url.set(url)
    is_connected.set("已连接")


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

backend_url.set("无法获取")
is_connected.set("未连接")

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
all_people: list[str] = []
online_queue = queue.Queue()

onlines = tk.Listbox(left_frame)
onlines.place(width=200, height=400, x=0, y=0)


# 更新在线列表
def update_onlines():
    try:
        online_people = online_queue.get_nowait()
        global all_people
        all_people = online_people
    except queue.Empty:
        pass

    onlines.delete(0, "end")
    for name in all_people:
        onlines.insert("end", name)

    win.after(1000, update_onlines)


update_onlines()


@app.route("/people", methods=["POST"])
def refresh_onlines():
    online_people = flask.request.data.decode("utf-8").split("\n")
    online_queue.put(online_people)

    return "OK", 200


# right_frame (function)
def to(*args):
    def wrapper():
        url = backend_url.get()
        msg = input_str.get()

        # 发送成功
        try:
            resp = requests.post(
                f"{url}/msg?name={SF_HOSTNAME}",
                data=msg.encode("utf-8"),
            )
            if resp.status_code != 200:
                messagebox.showerror("不能发送消息", f"状态码: {resp.status_code}")

        # 发送失败
        except:
            backend_url.set("无法获取")
            is_connected.set("未连接")
            messagebox.showerror("后端未开启", f"无法连接到 {url}")

    threading.Thread(target=wrapper, daemon=True).start()


# right_frame
input_str = tk.StringVar()
input_str.set("")

msg_box = tk.Text(right_frame, highlightthickness=0)
msg_box.place(width=400, height=350, x=0, y=0)

input_widget = tk.Entry(right_frame, textvariable=input_str)
tk.Button(right_frame, text="发送", command=to).place(width=50, height=50, x=350, y=350)

input_widget.place(width=350, height=50, x=0, y=350)
input_widget.bind("<Return>", to)


# 接收消息
@app.route("/", methods=["POST"])
def on_recv():
    msg = flask.request.data.decode("utf-8")
    msg_box.insert("end", msg + "\n")

    msg_box.see("end")
    input_str.set("")

    return "OK", 200


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
