import datetime
import random
import time
from math import sin
from threading import Thread

from opcua import ua, uamethod, Server

URL = "opc.tcp://127.0.0.1:4840/mp_opua_test/"
SERVER_NAME = "OPC UA Test Server"
NAMESPACE_NAME = "OPC UA Test Server"
start_timestamp = time.time()


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    """

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)

    def event_notification(self, event):
        print("New event", event)


# method to be exposed through server
def func(parent, variant):
    ret = False
    if variant.Value % 2 == 0:
        ret = True
    return [ua.Variant(ret, ua.VariantType.Boolean)]


# method to be exposed through server
# uses a decorator to automatically convert to and from variants
@uamethod
def multiply(parent, x, y):
    print("multiply method call with parameters: ", x, y)
    return x * y


class VarUpdater(Thread):
    def __init__(self, var):
        Thread.__init__(self)
        self._stopev = False
        self.var = var

    def stop(self):
        self._stopev = True

    def run(self):
        while not self._stopev:
            # v = sin(time.time() / 10)
            temperature = 20 + random.randint(0, 10)
            self.var.set_value(temperature)
            time.sleep(1)


def start():
    mServer = Server()
    mServer.set_endpoint(URL)
    mServer.set_security_policy([
        ua.SecurityPolicyType.NoSecurity,
        ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
        ua.SecurityPolicyType.Basic256Sha256_Sign])

    address_space = mServer.register_namespace(NAMESPACE_NAME)
    root_node = mServer.get_objects_node()
    params = root_node.add_object(address_space, "Parameters")
    start_time = params.add_variable(address_space, "start_time", start_timestamp)

    data = root_node.add_object(address_space, "data")

    pump = data.add_object(address_space, "Pump")
    temperature = 20 + random.randint(0, 10)
    pump_temp_var = pump.add_variable(address_space, "temperature", temperature)
    pump_temp_vup = VarUpdater(pump_temp_var)  # just  a dummy class update a variable

    pump_temp_unit = pump.add_variable(address_space, "unit", "°C")
    pump_status = pump.add_variable(address_space, "status", False)
    pump_status.set_writable()
    level = 12
    pump_level = pump.add_variable(address_space, "level", level)
    pump_level.set_writable()

    sleep_period = 0.5
    # Start the server
    mServer.start()
    print("Server started at {}".format(URL))

    # enable following if you want to subscribe to nodes on server side
    handler = SubHandler()
    sub = mServer.create_subscription(500, handler)
    handle = sub.subscribe_data_change(pump_level)

    # IMPORTANT: This should be started after the mServer.start()
    pump_temp_vup.start()
    try:
        while True:
            time.sleep(sleep_period)
    finally:
        # close connection, remove subscriptions, etc
        pump_temp_vup.stop()    # should be stopped
        mServer.stop()


if __name__ == '__main__':
    start()

