import argparse
import socket
import _thread
import json
import threading
import time

targets = []


def recv(sc):
    while True:
        msg, addr = sc.recvfrom(2048)
        cnt = json.loads(msg.decode("utf-8"))
        if cnt["cmd"] == 2:
            dest = tuple(cnt['msg'])
            k = "{}:{}".format(dest[0], dest[1])
            print("{}:{}".format("Device joined", k))
            targets.append(dest)
            sc.sendto('{"cmd":0}'.encode('utf-8'), dest)
        if cnt["cmd"] == 3:
            print("Found other devices: " + ",".join(cnt['msg'].keys()))
            for k, v in cnt['msg'].items():
                targets.append(tuple(v))
                sc.sendto('{"cmd":0}'.encode('utf-8'), tuple(v))
        if cnt["cmd"] == 4:
            print("{}:{}".format(addr, cnt['msg']))

def send(sc):
    while True:
        for x in targets:
            sc.sendto(json.dumps({"cmd":4, "msg": "ping"}).encode("utf-8"), x)
        time.sleep(500)

def run(port, s_host, s_port):
    peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    peer.bind(("0.0.0.0", port))

    msg = {"cmd":1, "msg": "registry"}
    peer.sendto(json.dumps(msg).encode("utf-8"), (s_host, s_port))

    _thread.start_new_thread(send, (peer, ))

    recv(peer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default='15100', help="the peer port")
    parser.add_argument("--server", type=str, default='127.0.0.1:7711', help="the server address")
    args = parser.parse_args()

    port = args.port
    s_host = args.server.split(":")[0]
    s_port = int(args.server.split(":")[1])
    run(port, s_host, s_port)