import argparse
import json
import socket

addrs = {}

def recv(sc):
    while True:
        msg, addr = sc.recvfrom(2048)
        a_key = "{}:{}".format(addr[0], addr[1])
        cnt = json.loads(msg.decode("utf-8"))
        if cnt["cmd"] == 1:
            if addrs:
                for k, v in addrs.items():
                    if k != a_key:
                        jtt = {"cmd": 2, "msg": addr}
                        sc.sendto(json.dumps(jtt).encode("utf-8"), v)
                msg = {"cmd": 3, "msg": {k: v for k, v in addrs.items() if k != a_key}}
                sc.sendto(json.dumps(msg).encode('utf-8'), addr)
            addrs[a_key] = addr

def run(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    print("Server listening on port", port)
    recv(server)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7711, help="Server port")
    args = parser.parse_args()

    run(args.port)
