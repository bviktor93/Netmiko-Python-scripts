from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException
import argparse


parser = argparse.ArgumentParser(description="Running commands from global config mode")
parser.add_argument("-c", "--cmd", type=str, nargs="+", help="Config commands you would like to add, one or more must be provided")
parser.add_argument("-u", "--user", type=str, help="Your username")
parser.add_argument("-p", "--passwd", type=str, help="Your password")
parser.add_argument("-e", "--enable", type=str, help="The enable password on the routers")
args = parser.parse_args()

user = args.user
passwd = args.passwd
en = args.enable
commands = args.cmd

CSR1 = {
    'device_type': 'cisco_xe',
    'ip': '10.0.0.1',
    'username': user,
    'password': passwd,
    'secret': en
}

CSR2 = {
    'device_type': 'cisco_xe',
    'ip': '10.0.0.2',
    'username': user,
    'password': passwd,
    'secret': en
}

R3 = {
    'device_type': 'cisco_ios',
    'ip': '10.0.0.3',
    'username': user,
    'password': passwd,
    'secret': en
}

routers = [CSR1, CSR2, R3]
timeouterror = []
autherror = []

for device in routers:
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        hostname = net_connect.send_command("show run | sec hostname").split()[1]
        output = net_connect.send_config_set(commands)
        print("\n" + " " * 30 + f"Issuing the following commands on device {hostname}:")
        print("-" * 90)
        print(output)
        net_connect.disconnect()
    except NetmikoTimeoutException:
        print(f"\n*** COULD NOT CONNECT TO DEVICE {device['ip']}, PLEASE VERIFY IP CONNECTIVITY ***")
        timeouterror.append(device['ip'])
        continue
    except NetmikoAuthenticationException:
        print(f"\n*** AUTHENTICATION FAILURE ON DEVICE {device['ip']}, PLEASE CHECK YOUR CREDENTIALS ***")
        autherror.append(device['ip'])
        continue

if len(timeouterror) != 0:
    print("\nCould not connect to the following devices, please check IP connectivity:")
    print(timeouterror)

if len(autherror) != 0:
    print("\nAuthentication failure on the following devices, please check your credentials:")
    print(autherror)
