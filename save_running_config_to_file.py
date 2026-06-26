from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException
import getpass

user = input("Enter your username: ")
passwd = getpass.getpass("Enter your password: ")
en = getpass.getpass("Enter your enable password: ")
#command = input("What is the show command you would like to run? ")

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
        output = net_connect.send_command("show run")
        print("\n" + " " * 30 + f"Saving the running config of {hostname}:")
        print("-" * 90)
        with open("config_"+str(hostname)+".cfg", "w") as file:
            file.write(output)
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
