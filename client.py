import sys
import socket
import threading

# PART 全局变量定义
SERVER_NAME = sys.argv[1]
with open(f"/everyone/{SERVER_NAME}/chat_server_address", "r", encoding="utf-8") as f:
    HOST, PORT = f.read().strip().split(":", 1)
STOP_FLAG = threading.Event()
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


# PART 接收消息
def onrecv(client: socket.socket):
    while True:
        msg = recv_all(client)
        print(msg)


# END


# PART 发送消息
def onsend(client: socket.socket):
    while True:
        msg = input("")
        if msg == "EXIT":
            STOP_FLAG.set()
            break
        client.send(msg)


# END

# PART 连接到服务器
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, int(PORT)))
# END

# PART 启动线程
try:
    onrecv_thread = threading.Thread(target=onrecv, args=(client,), daemon=True).start()
    onsend_thread = threading.Thread(target=onsend, args=(client,), daemon=True).start()
    STOP_FLAG.wait()
finally:
    client.close()
# END
