import os
import socket
import threading

# PART 全局变量定义
LOCAL_DOMAIN = "lg-%s.sf-guest" % os.environ["SF_LID"]
SHARE_DIR = "/everyone/%s" % os.environ["SF_HOSTNAME"]
SERVER_PORT = 8503
CLIENTS: dict[str, socket.socket] = {}
# END

# PART 写入当前服务器地址
os.system(f"echo '{LOCAL_DOMAIN}:{SERVER_PORT}' > {SHARE_DIR}/chat_server_address ")
# END


# PART 完全读取用户输入
def recv_all(client: socket.socket) -> str:

    # PART 读取消息长度
    raw_length = client.recv(4)
    if not raw_length:
        raise ConnectionError("不能读取消息长度")
    length = int.from_bytes(raw_length, byteorder="big")
    # END

    # PART 读取消息内容
    msg = client.recv(length)
    if not msg or len(msg) != length:
        raise ConnectionError("不能读取完整消息")
    return msg.decode("utf-8")
    # END


# END


# PART 配套的发送消息
def send_msg(client: socket.socket, msg: str):
    client.sendall(len(msg).to_bytes(4, byteorder="big") + msg.encode("utf-8"))


# END


# PART 转发消息处理
def broadcast(message: str, exclude: list[str] = []):
    for nickname, client in CLIENTS.items():
        if nickname not in exclude:
            send_msg(client, message)


# END


# PART 客户端连接处理
def onconn(client: socket.socket, address):

    # PART 请求用户名称
    while True:
        send_msg(client, "用户名: \n")
        nickname = recv_all(client).strip()
        if nickname not in CLIENTS and len(nickname) > 0 and len(nickname) < 10:
            break
        send_msg(client, "用户名不合法\n")
    # END

    # PART 注册客户端
    CLIENTS[nickname] = client
    broadcast(f"[SYSTEM] {nickname}({address}) 已加入聊天室\n")
    # END

    # PART 进入聊天处理
    onchat(client, nickname)
    # END


# END


# PART 进入聊天处理
def onchat(client: socket.socket, nickname: str):
    while True:
        uinput = recv_all(client)
        broadcast(f"[{nickname}] {uinput}\n")


# END


# PART 客户端断开处理
def onclose(client: socket.socket):
    for nickname, uclient in CLIENTS.items():
        if client == uclient:
            client.close()
            del CLIENTS[nickname]
            broadcast(f"[SYSTEM] {nickname} 已离开聊天室\n")
            break


# END


# PART 初始化服务器
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", SERVER_PORT))
server.listen(4096)
print(f"服务器在 {SERVER_PORT} 端口启动")
# END

# PART 客户端连接处理
while True:
    client, address = server.accept()

    # PART 自动销毁连接
    def autoclose(*args, **kwargs):
        try:
            onconn(*args, **kwargs)
        finally:
            onclose(client)

    # END

    threading.Thread(target=autoclose, args=(client, address), daemon=True).start()
# END
