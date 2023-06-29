import json
import sys
from pprint import pprint

from gns3fy import Gns3Connector, Project, Node, Link

GNS3_IP = "198.18.1.200"
GNS3_SERVER_URL = f"http://{GNS3_IP}:3080"
PROJECT = "GNS3fy"
# PROJECT = "Cloud Link"


def main():
    # Define the connector object, by default its port is 3080
    gns3_server = Gns3Connector(url=GNS3_SERVER_URL)

    # Verify connectivity by checking the server version
    try:
        print(gns3_server.get_version())
    except ConnectionError as e:
        print(f"Connection to {gns3_server} failed:" + e.__class__.__name__)
        sys.exit(1)

    lab = Project(name=PROJECT, connector=gns3_server)
    lab.get()

    # GNSMgmt = lab.get_node(name="GNSMgmt")
    # pprint(GNSMgmt)

    # pprint(lab.links_summary())
    lab.links_summary()

    # for link in lab.links:
    #    print(link)

    # for node in lab.nodes:
    #    print(node)


if __name__ == "__main__":
    main()
