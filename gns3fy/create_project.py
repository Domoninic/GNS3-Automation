import json
import sys
import time
from pprint import pprint

from netmiko import ConnectHandler, NetmikoAuthenticationException, ReadTimeout
from requests import ConnectionError, HTTPError

from gns3fy import Gns3Connector, Node, Project

from gns3fy.gns3_parameters import *


def main():
    PROJECT = "GNS3fy"
    # PATH = None
    PROJECTS_PATH = f"{GNS3_PROJECTS_PATH}{PROJECT}"
    NODE_START_DELAY = 120
    TEMPLATES_PATH = "./templates/"
    GNS3_TEMPLATE_FILE = "GNS3_templates.json"
    DEVICE_FILE = "devices.json"
    LINKS_FILE = "links.json"

    # Define the connector object, by default its port is 3080
    gns3_server = Gns3Connector(url=GNS3_SERVER_URL)

    # Verify connectivity by checking the server version
    try:
        print(gns3_server.get_version())
    except ConnectionError as e:
        print(f"Connection to {gns3_server} failed:" + e.__class__.__name__)
        sys.exit(1)

    # create cloud template if it does not exist
    with open(f"{TEMPLATES_PATH}{GNS3_TEMPLATE_FILE}", "r") as filehandle:
        templates = json.load(filehandle)
    for template in templates:
        try:
            gns3_server.create_template(**template)
        except ValueError as e:
            print(f"{e}")

    # Now obtain a project from the server
    project = Project(
        name=PROJECT,
        path=PROJECTS_PATH,
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
            name=PROJECT,
            path=PROJECTS_PATH,
            scene_height=500,
            scene_width=500,
            connector=gns3_server,
        )
        project.create()

    # Show some of its attributes
    print(f"{project.name}: {project.project_id} -- Status {project.status}")
    print(f"{project.path}")
    print(project.nodes_summary())

    # add Nodes
    with open(f"{TEMPLATES_PATH}{DEVICE_FILE}", "r") as filehandle:
        devices = json.load(filehandle)

    for device in devices:
        node = Node(
            project_id=project.project_id,
            connector=gns3_server,
            name=device["name"],
            template=device["template"],
            x=device["x"],
            y=device["y"],
        )
        try:
            node.create()
        except HTTPError as e:
            print(e)

    # Now check again the status of the nodes
    project.get_nodes()
    print(project.nodes_summary())

    with open(f"{TEMPLATES_PATH}{LINKS_FILE}", "r") as file:
        links_data = file.read()

    links = json.loads(links_data)

    for link in links:
        project.create_link(*link)

    # start all the nodes
    for node in project.nodes:
        if node.node_type == "cloud":
            pass
        else:
            print(f"Starting Node {node.name}")
            node.start()
            time.sleep(3)

    print(f"Waiting { NODE_START_DELAY } seconds for nodes to start")
    time.sleep(NODE_START_DELAY)
    print(f"Finished Waiting")

    for node in project.nodes:
        if node.node_type == "cloud":
            pass
        else:
            R = {
                "ip": GNS3_IP,
                "device_type": "cisco_ios_telnet",
                "port": node.console,
                # "session_log": f"{node.name}.log",
            }

            device = next(item for item in devices if item["name"] == node.name)
            interfaces = device["interfaces"]

            commands = [f'hostname {device["name"]}']
            for interface in interfaces:
                commands.append(f'interface {interface["name"]}')
                commands.append(f'ip address {interface["IP"]} {interface["mask"]}')
                commands.append(f'description {interface["desc"]}')
                commands.append("no shutdown")
            commands.append("exit")
            commands.append("do copy run start")
            try:
                with ConnectHandler(**R) as net_connect:
                    net_connect = ConnectHandler(**R)
                    net_connect.send_config_set(commands)
                    print("Finding prompt")
                    prompt = net_connect.find_prompt()
                    print(f"Prompt: {prompt}")

                    # net_connect.save_config()
                    output = net_connect.send_command(
                        "show ip int brief", expect_string=prompt
                    )
                    print(output)
                    net_connect.disconnect()
            except (
                ConnectionRefusedError,
                NetmikoAuthenticationException,
                ReadTimeout,
            ) as e:
                print(
                    f'Connection to {device["name"]} failed: Error from Module:{e.__module__},type:{e.__class__.__name__}'
                )
                print(e)


# project.close()


if __name__ == "__main__":
    main()
