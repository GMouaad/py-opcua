import argparse

from opcua import Client

parser = argparse.ArgumentParser(description="Minimalistic OPC UA Client")
parser.add_argument("-a",
                    "--address",
                    help="URL of OPC UA server (for example: example.org:4840)",
                    default='localhost:4840')
args = vars(parser.parse_args())


def start():
    address = args['address']
    server_url = "opc.tcp://{}/mp_opua_test/".format(address)
    client = Client(server_url)
    try:
        # Start the client
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

    finally:
        client.disconnect()


if __name__ == '__main__':
    start()
