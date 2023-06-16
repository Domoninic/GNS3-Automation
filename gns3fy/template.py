from jinja2 import Environment, FileSystemLoader
import json


TEMPLATE_FILE = "interface.j2"
TOPOLOGY_FILE = "devices.json"

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template(TEMPLATE_FILE)


with open(TOPOLOGY_FILE, "r") as filehandle:
    devices = json.load(filehandle)

conf = ""

for device in devices:
    for interface in device.get("interfaces") or []:
        conf += template.render(interface)
print(conf)
