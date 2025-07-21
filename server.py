import argparse
import json
import os
import signal
import socket
import sys
import threading

peers = {}

def recv(sk):
    while True:
        try:
            msg, addr = sk.recvfrom(2048)
        except socket.error:
            continue
        p_key = "{}:{}".format(addr[0], addr[1])
        cnt = json.loads(msg.decode("utf-8"))
        if cnt["cmd"] == 1:
            if peers:
                for k, peer in peers.items():
                    if k != p_key:
                        sk.sendto(json.dumps({"cmd": 2, "n_peer": addr}).encode("utf-8"), peer)
                msg = {"cmd": 3, "peers": {k: v for k, v in peers.items() if k != p_key}}
                sk.sendto(json.dumps(msg).encode('utf-8'), addr)
            peers[p_key] = addr

def run(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.settimeout(5)
    print("Server listening on port", port)
    recv(server)
    server.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7711, help="Server port")
    args = parser.parse_args()

    run(args.port)
