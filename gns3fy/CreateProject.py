import json
import time
import sys

from netmiko import ConnectHandler, NetmikoAuthenticationException
from requests import HTTPError, ConnectionError

from gns3fy import Gns3Connector, Link, Node, Project

GNS3_IP = "198.18.1.200"
GNS3_SERVER_URL = f"http://{GNS3_IP}:3080"
PROJECT = "GNS3fy"
NODE_START_DELAY = 120
TOPOLOGY_FILE = "devices.json"


def run():
    with open(TOPOLOGY_FILE, "r") as filehandle:
        devices = json.load(filehandle)

    # Define the connector object, by default its port is 3080
    gns3_server = Gns3Connector(url=GNS3_SERVER_URL)

    # Verify connectivity by checking the server version
    try:
        print(gns3_server.get_version())
    except ConnectionError as e:
        print(f"Connection to {gns3_server} failed:" + e.__class__.__name__)
        sys.exit(1)

    # Now obtain a project from the server
    project = Project(
        name=PROJECT,
        path=f"/opt/gns3/projects/{PROJECT}",
        scene_height=500,
        scene_width=500,
        connector=gns3_server,
    )

    try:
        project.create()
    except HTTPError as e:
        print(e)
        project.get()
        project.delete()
        project = Project(
            name=PROJECT, path=f"/opt/gns3/projects/{PROJECT}", connector=gns3_server
        )
        project.create()

    # Show some of its attributes
    print(f"{project.name}: {project.project_id} -- Status {project.status}")
    print(f"{project.path}")
    print(project.nodes_summary())

    # add Nodes
    for device in devices:
        node = Node(
            project_id=project.project_id,
            connector=gns3_server,
            name=device["name"],
            template=device["template"],
            x=device["x"],
            y=device["y"],
        )
        node.create()

    # Now check again the status of the nodes
    project.get_nodes()
    print(project.nodes_summary())

    # Define links  Need to mak this part of topology file and not dependent on knowing node numbers
    links = [
        [
            dict(node_id=project.nodes[0].node_id, adapter_number=0, port_number=0),
            dict(node_id=project.nodes[1].node_id, adapter_number=0, port_number=0),
        ],
        [
            dict(node_id=project.nodes[0].node_id, adapter_number=1, port_number=0),
            dict(node_id=project.nodes[2].node_id, adapter_number=1, port_number=0),
        ],
        [
            dict(node_id=project.nodes[1].node_id, adapter_number=2, port_number=0),
            dict(node_id=project.nodes[2].node_id, adapter_number=2, port_number=0),
        ],
    ]
    # create links
    for nodes in links:
        link = Link(project_id=project.project_id, connector=gns3_server, nodes=nodes)
        link.create()

    # start all the nodes
    for node in project.nodes:
        node.start()
        time.sleep(3)

    print(f"Waiting { NODE_START_DELAY } seconds for nodes to start")
    time.sleep(NODE_START_DELAY)
    print(f"Finished Waiting")

    for node in project.nodes:
        R = {
            "ip": GNS3_IP,
            "device_type": "cisco_ios_telnet",
            "port": node.console,
        }

        device = next(item for item in devices if item["name"] == node.name)
        interfaces = device["interfaces"]

        # move building commands to a template
        commands = [f'hostname {device["name"]}']
        for interface in interfaces:
            commands.append(f'{interface["name"]}')
            commands.append(f'ip address {interface["IP"]} {interface["mask"]}')
            commands.append(f'description {interface["desc"]}')
            commands.append("no shutdown")
        commands.append("end")
        commands.append("copy run start")
        try:
            net_connect = ConnectHandler(**R)
            net_connect.send_config_set(commands)
            output = net_connect.send_command("show ip int brief")
            print(output)
        except (ConnectionRefusedError, NetmikoAuthenticationException) as e:
            print(
                f'Connection to {device["name"]} failed: Error from Module:{e.__module__},type:{e.__class__.__name__}'
            )
            print(e)


# project.close()


if __name__ == "__main__":
    run()
