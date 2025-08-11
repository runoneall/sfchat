import os
import socket
import flask
import requests
import concurrent.futures

app = flask.Flask(__name__)
all_sub: list[str] = []


# 广播消息
def broadcast(path: str, message: str):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        # 准备任务
        all_sub_copy = all_sub.copy()
        for sub_name in all_sub_copy:

            def job(sub_name, path, message):

                # 获取订阅链接
                with open(f"/everyone/{sub_name}/chat_sub_address") as f:
                    sub_address = "http://" + f.read().replace("\n", "")

                # 发送消息
                try:
                    requests.post(sub_address + path, data=message)

                # 不能完成消息
                except:
                    all_sub.remove(sub_name)

            futures.append(executor.submit(job, sub_name, path, message))

        # 等待任务完成
        concurrent.futures.wait(futures)

        # 是否有无效的订阅
        if all_sub != all_sub_copy:
            broadcast("/people", "\n".join(all_sub))


# 检查连接
@app.route("/ping")
def on_ping():
    return "pong", 200


# 添加订阅
@app.route("/sub/add", methods=["GET"])
def on_sub_add():

    # 读取SF服务器名
    sf_name = flask.request.args.get("name")
    if not sf_name:
        return "缺少服务器名 ?name=$SF_HOSTNAME", 400

    # 添加到订阅
    if sf_name not in all_sub:
        all_sub.append(sf_name)

    broadcast("/people", "\n".join(all_sub))
    return "添加成功", 200


# 获取订阅列表
@app.route("/sub/list", methods=["GET"])
def on_sub_list():
    return "\n".join(all_sub), 200


# 开始消息
@app.route("/msg", methods=["POST"])
def on_msg():

    # 获取发送者
    sf_name = flask.request.args.get("name")
    if not sf_name:
        return "缺少服务器名 ?name=$SF_HOSTNAME", 400

    # 获取消息内容
    msg_content = flask.request.data.decode("utf-8")

    # 向订阅者发送消息
    broadcast("/", f"[{sf_name}] {msg_content}")

    return "发送成功", 200


# 随机端口
def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return int(port)


# 启动服务
if __name__ == "__main__":
    port = get_free_port()

    os.system(
        "echo '%s:%s' > %s/chat_server_address "
        % (
            "lg-%s.sf-guest" % os.environ["SF_LID"],
            port,
            "/everyone/" + os.environ["SF_HOSTNAME"],
        )
    )
    app.run(debug=False, host="0.0.0.0", port=port, threaded=True)
