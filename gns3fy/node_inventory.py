import sys

from gns3_parameters import *

from requests import ConnectionError, HTTPError

from gns3fy import Gns3Connector, Project


def main():
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
        name="GNS3fy_Ansible",
        connector=gns3_server,
    )
    project.get()
    try:
        nodes_inventory = project.nodes_inventory()
    except HTTPError as e:
        print(e)

    print(nodes_inventory)


if __name__ == "__main__":
    main()
