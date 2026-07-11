from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException
import getpass
import textfsm

user = input("Enter your username: ")
passwd = getpass.getpass("Enter your password: ")
en = getpass.getpass("Enter your enable password: ")

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
        net_connect.send_command("terminal length 0")
        hostname = net_connect.send_command("show run | sec hostname").split()[1]
        traceroute = net_connect.send_command("trace 99.99.99.99 num")
        print("\n" + " " * 30 + f"Output of the device {hostname}:")
        print("-" * 90)
        print(traceroute)
        with open("traceroute.template") as temp:
            fsm = textfsm.TextFSM(temp)
            result = fsm.ParseText(traceroute)
        print("\nHeaders in the template:")
        print(fsm.header)
        print("\nParsed data:")
        print(result)
        net_connect.disconnect()
    except NetmikoTimeoutException:
        print(f"\n*** COULD NOT CONNECT TO DEVICE {device['ip']}, PLEASE VERIFY IP CONNECTIVITY ***")
        timeouterror.append(device['ip'])
        continue
    except NetmikoAuthenticationException:
        print(f"\n*** AUTHENTICATION FAILURE ON DEVICE {device['ip']}, PLEASE CHECK YOUR CREDENTIALS ***")
        autherror.append(device['ip'])
        continue
    except Exception as ex:
        print(f"\nThe following error occured on {device["ip"]}:")
        print(ex)

if len(timeouterror) != 0:
    print("\nCould not connect to the following devices, please check IP connectivity:")
    print(timeouterror)

if len(autherror) != 0:
    print("\nAuthentication failure on the following devices, please check your credentials:")
    print(autherror)