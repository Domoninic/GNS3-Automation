import json

from gns3_parameters import *
from netmiko import ConnectHandler, NetmikoAuthenticationException, ReadTimeout
from projects.gns3_project import *


def main():
    with open(f"{PROJECTS_PATH}{DEVICE_FILE}", "r") as filehandle:
        devices = json.load(filehandle)

    for device in devices:
        if device.get("device_type") == "cisco_ios_telnet":
            R = {
                "ip": GNS3_IP,
                "device_type": "cisco_ios_telnet",
                "port": device.get("console"),
                "session_log": f'{device["name"]}.log',
            }

            net_connect = ConnectHandler(**R)
            net_connect.disconnect


if __name__ == "__main__":
    main()
