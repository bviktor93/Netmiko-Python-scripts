from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException
import yaml
from jinja2 import Environment, FileSystemLoader

timeouterror = []
autherror = []

#yaml.safe_load() converts the YAML file into a Python dictionary
with open("routers_ikev2.yaml", "r") as file:
    #Now devices is a dictonary
    devices = yaml.safe_load(file)
#print(devices["routers_list"])

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('ipsec_ikev2.j2')

for i in devices["routers_list"]:
    ipsec_config = template.render(
        ike_peer_name=i["ike_peer_name"],
        ike_peer_address = i["ike_peer_address"],
        tunnel_src = i["tunnel_src"],
        tunnel_dst = i["tunnel_dst"],
        tunnel_ip = i["tunnel_ip"])
    #print(ipsec_config)
    with open(i["hostname"], "w") as f:
        f.write(ipsec_config)
    try:
        net_connect = ConnectHandler(ip=i["ip"], username=i["username"], password=i["password"], secret=i["secret"], device_type=i["device_type"])
        net_connect.enable()
        hostname = net_connect.send_command("show run | sec hostname").split()[1]
        output = net_connect.send_config_from_file(i["hostname"])
        print("\n" + " " * 30 + f"Sending the following commands to {hostname}:")
        print("-" * 90)
        print(output)
        net_connect.disconnect()
    except NetmikoTimeoutException:
        print(f"\n*** COULD NOT CONNECT TO DEVICE {i['ip']}, PLEASE VERIFY IP CONNECTIVITY ***")
        timeouterror.append(i['ip'])
        continue
    except NetmikoAuthenticationException:
        print(f"\n*** AUTHENTICATION FAILURE ON DEVICE {i['ip']}, PLEASE CHECK YOUR CREDENTIALS ***")
        autherror.append(i['ip'])
        continue

if len(timeouterror) != 0:
    print("\nCould not connect to the following devices, please check IP connectivity:")
    print(timeouterror)

if len(autherror) != 0:
    print("\nAuthentication failure on the following devices, please check your credentials:")
    print(autherror)
