import json
import time

from netmiko import ConnectHandler
from requests import HTTPError

from gns3fy import Gns3Connector, Link, Node, Project

GNS3_IP = "198.18.1.200"
GNS3_SERVER_URL = f"http://{GNS3_IP}:3080"
PROJECT = "GNS3fy"

with open("routers.json", "r") as filehandle:
    ROUTERS = json.load(filehandle)

# Define the connector object, by default its port is 3080
server = Gns3Connector(url=GNS3_SERVER_URL)

# Verify connectivity by checking the server version
print(server.get_version())

# Now obtain a project from the server
lab = Project(
    name=PROJECT,
    path=f"/opt/gns3/projects/{PROJECT}",
    scene_height=500,
    scene_width=500,
    connector=server,
)

try:
    lab.create()
except HTTPError as e:
    print(e)
    lab.get()
    lab.delete()
    lab = Project(name=PROJECT, path=f"/opt/gns3/projects/{PROJECT}", connector=server)
    lab.create()
except Exception as e:
    print("Unknown error - type :" + e.__class__.__name__)
    print(e)


# Show some of its attributes
print(f"{lab.name}: {lab.project_id} -- Status {lab.status}")
print(f"{lab.path}")

print(lab.nodes_summary())

# add Nodes
# nodes
for router in ROUTERS:
    node = Node(
        project_id=lab.project_id,
        connector=server,
        name=router["name"],
        template=router["template"],
        x=router["x"],
        y=router["y"],
    )
    node.create()

# Now check again the status of the nodes
lab.get_nodes()
print(lab.nodes_summary())

# Define links  Need to mak this part of topology file and not dependent on knowing node numbers
LINKS = [
    [
        dict(node_id=lab.nodes[0].node_id, adapter_number=0, port_number=0),
        dict(node_id=lab.nodes[1].node_id, adapter_number=0, port_number=0),
    ],
    [
        dict(node_id=lab.nodes[0].node_id, adapter_number=1, port_number=0),
        dict(node_id=lab.nodes[2].node_id, adapter_number=1, port_number=0),
    ],
    [
        dict(node_id=lab.nodes[1].node_id, adapter_number=2, port_number=0),
        dict(node_id=lab.nodes[2].node_id, adapter_number=2, port_number=0),
    ],
]
# create links
for nodes in LINKS:
    link = Link(project_id=lab.project_id, connector=server, nodes=nodes)
    link.create()

# start all the nodes
for node in lab.nodes:
    node.start()
    time.sleep(3)

NODE_START_DELAY = 120

print(f"Waiting { NODE_START_DELAY } seconds for nodes to start")
time.sleep(NODE_START_DELAY)
print(f"Finished Waiting")

for node in lab.nodes:
    R = {
        "ip": GNS3_IP,
        "device_type": "cisco_ios_telnet",
        "port": node.console,
        "auto_connect": False,
    }

    ROUTER = next(item for item in ROUTERS if item["name"] == node.name)
    INTERFACES = ROUTER["interfaces"]

    # move building commands to a template
    commands = [f'hostname { ROUTER["name"]}']
    for interface in INTERFACES:
        commands.append(f'{interface["name"]}')
        commands.append(f'ip address {interface["IP"]} {interface["mask"]}')
        commands.append(f'description {interface["desc"]}')
        commands.append("no shutdown")
    commands.append("end")
    commands.append("copy run start")
    try:
        net_connect = ConnectHandler(**R)
        net_connect.establish_connection()
        net_connect.send_config_set(commands)
        output = net_connect.send_command("show ip int brief")
        print(output)
        net_connect.disconnect()
    except Exception as e:
        print("Unknown error - type :" + e.__class__.__name__)
        print(e)

# lab.close()
