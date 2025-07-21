import argparse
import signal
import socket
import _thread
import json
import sys
import threading
import time

targets = {}


def recv(sk):
    while True:
        try:
            msg, addr = sk.recvfrom(2048)
        except socket.error:
            continue
        cnt = json.loads(msg.decode("utf-8"))
        if cnt["cmd"] == 2:
            tpr = tuple(cnt["n_peer"])
            k = "{}:{}".format(tpr[0], tpr[1])
            print("{} -> {}".format("New peer joined", k))
            targets[k] = tpr
            sk.sendto(json.dumps({"cmd":0, "msg": "hit"}).encode("utf-8"), targets[k])
        elif cnt["cmd"] == 3:
            if not cnt["peers"]:
                continue
            print("Found other peers -> " + ",".join(cnt["peers"].keys()))
            for k, tpr in cnt['peers'].items():
                targets[k] = tuple(tpr)
                sk.sendto(json.dumps({"cmd":0, "msg": "hit"}).encode("utf-8"), targets[k])
        elif cnt["cmd"] == 4:
            print("from {}:{} -> {}".format(addr[0], addr[1], cnt['msg']))

def send(sk):
    while True:
        for tpr in targets.values():
            sk.sendto(json.dumps({"cmd":4, "msg": "ping"}).encode("utf-8"), tpr)
        time.sleep(5)

def run(port, s_host, s_port):
    peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    peer.bind(("0.0.0.0", port))
    peer.settimeout(3)
    peer.sendto(json.dumps({"cmd": 1, "msg": "registry"}).encode("utf-8"), (s_host, s_port))

    threading.Thread(target=send, args=(peer,)).start()

    recv(peer)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGILL, lambda sig, frame: sys.exit(0))

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default='15100', help="the peer port")
    parser.add_argument("--server", type=str, default='127.0.0.1:7711', help="the server address")
    args = parser.parse_args()

    arg1 = args.port
    arg2 = args.server.split(":")[0]
    arg3 = int(args.server.split(":")[1])
    run(arg1, arg2, arg3)