#!/usr/bin/env python
"""
Ansible module to test that Netmiko SSH/Telent connection to remote device is successful

By default, verifies that '#' exists in the remote device prompt.

based on https://github.com/Domoninic/netmiko-ansible/blob/master/library/netmiko_connect

"""

from ansible.module_utils.basic import *
from netmiko import ConnectHandler

try:
    MEETS_REQUIREMENTS = False
    # require netmiko >= 0.2.5
    import netmiko

    version = netmiko.__version__
    #    major_ver, minor_ver, revision = version.split(".")
    #    if major_ver >= 0 and minor_ver >= 2 and revision >= 5:
    MEETS_REQUIREMENTS = True
#    else:
#        MEETS_REQUIREMENTS = False
except ImportError:
    MEETS_REQUIREMENTS = False


def main():
    """
    Ansible module to test that Netmiko connection to remote device is successful

    By default, verifies that '#' exists in the remote device prompt.
    """

    module = AnsibleModule(
        argument_spec=dict(
            device_type=dict(required=False, default="cisco_ios_telnet"),
            host=dict(required=True),
            port=dict(required=False, default=22),
            username=dict(required=False),
            password=dict(required=False),
            secret=dict(required=False, default=""),
            enable_mode=dict(required=False, default=False),
            check_string=dict(required=False, default="#"),
        ),
        supports_check_mode=False,
    )

    module.debug
    if not MEETS_REQUIREMENTS:
        module.fail_json(msg="netmiko >= 0.2.5 is required for this module")

    net_device = {
        "device_type": module.params["device_type"],
        "ip": module.params["host"],
        "port": int(module.params["port"]),
        "username": module.params["username"],
        "password": module.params["password"],
        "secret": module.params["secret"],
        "verbose": False,
    }

    conn = ConnectHandler(**net_device)
    #    conn.send_command("\n")
    output = conn.find_prompt()
    if module.params["check_string"] in output:
        module.exit_json(msg="SSH connection completed successfully")
    else:
        module.fail_json(msg="Failed to detect check_string in output", output=output)


if __name__ == "__main__":
    main()
