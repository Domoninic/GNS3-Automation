import sys

from gns3fy.gns3parameters import *
from requests import ConnectionError, HTTPError

from gns3fy import Gns3Connector, Link, Node, Project


def main():
    PROJECT = "GNS3fy"

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
        connector=gns3_server,
    )

    try:
        project.get()
        project.delete()
    except HTTPError as e:
        print(e)


if __name__ == "__main__":
    main()
