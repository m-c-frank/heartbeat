from flask import Flask, send_from_directory, request
import time
import os
import dotenv
import threading

dotenv.load_dotenv()
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
TIMEOUT = int(os.getenv('TIMEOUT'))  # in seconds
CHECK_INTERVAL = int(os.getenv('PRUNING_INTERVAL'))  # in seconds


class Node:
    def __init__(self, ip, timestamp):
        self.ip = ip
        self.timestamp = timestamp
        self.active = True

    def as_dict(self):
        return {
            "ip": self.ip,
            "timestamp": self.timestamp,
            "active": self.active
        }


registered_nodes = {}


app = Flask(__name__)


def check_nodes():
    while True:
        for node_ip, node in registered_nodes.items():
            if int(time.time()) - node.timestamp > TIMEOUT:
                registered_nodes[node_ip].active = False
        time.sleep(CHECK_INTERVAL)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api')
def api():
    # copy registered_nodes to nodes_snapshot
    nodes_snapshot = registered_nodes.copy()
    # remove inactive nodes from nodes_snapshot
    nodes = []
    for node_ip, node in nodes_snapshot.items():
        if node.active:
            nodes.append(node.as_dict())
    response = {"nodes": nodes}
    return response


@app.route("/heartbeat")
def heartbeat():
    node_ip = str(request.remote_addr)
    if node_ip not in registered_nodes:
        node = Node(node_ip, int(time.time()))
        registered_nodes[node_ip] = node
    else:
        registered_nodes[node_ip].timestamp = int(time.time())
        registered_nodes[node_ip].active = True
    return "OK"


threading.Thread(target=check_nodes).start()
app.run(host=HOST, port=PORT)
