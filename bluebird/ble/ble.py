import dbus
import sys
import dbus.service
import dbus.exceptions
from gi.repository import GLib
import dbus.mainloop.glib
import struct
import requests
import array
from enum import Enum

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE = "org.bluez.GattDescriptor1"

LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"

AGENT_INTERFACE = "org.bluez.Agent1"

SERVICE_UUID = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
CHARACTERISTIC_UUID_SSID = "51FF12BB-3ED8-46E5-AD5B-D64E2FEC021B"
CHARACTERISTIC_UUID_PAYLOAD = "bfc0c92f-317d-4ba9-976b-cc11ce77b4ca"

AGENT_PATH = "/com/punchthrough/agent"

VivaldiBaseUrl = "XXXXXXXXXXXX"

mainloop = None

"""
def main():
    logging.basicConfig(level=logging.INFO)
    # Set up the D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Register GATT service
    bus = dbus.SystemBus()
    # get the ble controller
    adapter = find_adapter(bus)
    print(adapter)
    if not adapter:
        logger.critical("GattManager1 interface not found")
        return

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)
    print("adpater_obj: " + str(adapter_obj) + "\n")
    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    print("service_manger: " + str(service_manager) + "\n")
    
    # Initialize GATT service and characteristics
    wifi_service = BLEService(bus, 0, uuid=SERVICE_UUID, primary=True)

    # Characteristics for Wi-Fi credentials and payload
    ssid_char = BLECharacteristic(bus, 0, CHARACTERISTIC_UUID_SSID, ["read", "write"], wifi_service)
    payload_char = BLECharacteristic(bus, 1, CHARACTERISTIC_UUID_PASS, ["read", "write"], wifi_service)

    # Add characteristics to the service
    wifi_service.add_characteristic(ssid_char)
    wifi_service.add_characteristic(payload_char)
    print(wifi_service)
    # Start the GLib main loop to process D-Bus events
    mainloop = GLib.MainLoop()

    try:
        service_manager.RegisterApplication(wifi_service.get_path(), {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
        logging.info("GATT service registered successfully")
    except dbus.exceptions.DBusException as e:
        logging.error(f"Failed to register GATT service: {str(e)}")

    adapter = find_adapter(bus)
    print(adapter)
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logging.info("GATT service interrupted, exiting...")
        mainloop.quit()
"""

class CommissioningService(BaseService):
    """
    Dummy test service that provides characteristics and descriptors that
    exercise various API functionality.

    """

    def __init__(self, bus, index):
        BaseService.__init__(self, bus, index, SERVICE_UUID, True)
        self.add_characteristic(SsidCharacteristic(bus, 0, self))
        self.add_characteristic(PasswordCharacteristic(bus, 1, self))
        self.add_characteristic(AesCharacteristic(bus, 2, self))
        self.add_characteristic(EccCharacteristic(bus, 3, self))

class SsidCharacteristic(BaseCharacteristic):
    description = b"Plaintext SSID"

    class State(Enum):
        on = "ON"
        off = "OFF"
        unknown = "UNKNOWN"

        @classmethod
        def has_value(cls, value):
            return value in cls._value2member_map_

    power_options = {"ON", "OFF", "UNKNOWN"}

    def __init__(self, bus, index, service):
        BaseCharacteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID_SSID, ["secure-read", "secure-write"], service,
        )

        self.value = [0xFF]
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        logger.info("auto off write: " + repr(value))
        cmd = bytes(value)

        # write it to machine
        logger.info("writing {cmd} to machine")
        data = {"cmd": "autoOffMinutes", "time": struct.unpack("i", cmd)[0]}
        self.value = value

class PayloadCharacteristic(BaseCharacteristic):
    description = b"Encrypted Password (With AES and ECC)"

    def __init__(self, bus, index, service):
        BaseCharacteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID_PASS, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = []
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        logger.info("auto off write: " + repr(value))
        cmd = bytes(value)

        # write it to machine
        logger.info(f"writing {cmd} to machine")
        self.value = value

class CharacteristicUserDescriptionDescriptor(BaseDescriptor):
    """
    Writable CUD descriptor.
    """

    CUD_UUID = "2901"

    def __init__(
        self, bus, index, characteristic,
    ):

        self.value = array.array("B", characteristic.description)
        self.value = self.value.tolist()
        BaseDescriptor.__init__(self, bus, index, self.CUD_UUID, ["read"], characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value

class CommissioningAdvertisement(BaseAdvertisement):
    def __init__(self, bus, index):
        BaseAdvertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x70, 0x74],
        )
        self.add_service_uuid(SERVICE_UUID)

        self.add_local_name("Comissioning Service")
        self.include_tx_power = True

class BluebirdCommissioner():

    def __init__():
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        _mainloop = GLib.MainLoop
        _bus = dbus.SystemBus()
        _adapter = find_adapter(self._bus)
        _adapter_obj = lambda: (None if not self._adapter else self._bus.get_object(BLUEZ_SERVICE_NAME, self._adapter))
        _adapter_props = lambda: (None if not self._adapter else dbus.Interface(self._adapter_obj, "org.freedesktop.DBus.Properties"))

        # Lambda function handles finding the adapter and initializing related properties
        self._adapter, self._adapter_obj, self._adapter_props = (lambda: (
            adapter := find_adapter(self._bus),
            None if not adapter else self._bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            None if not adapter else dbus.Interface(
                self._bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                "org.freedesktop.DBus.Properties"
            )
        ) if (adapter := find_adapter(self._bus)) else (None, None, None))()
    
    def start():
        if not _adapter:
            print("GattManager1 interface not found") #logger.critical("GattManager1 interface not found")
            sys.exit(1)
        
        self._adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1)) # powered property on the controller to on

def main():
    # Get manager objs
    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advertisement = CommissioningAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = BaseApplication(bus)
    app.add_service(CommissioningService(bus, 2))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    logger.info("Registering GATT application...")

    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=[big_error],
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)

    mainloop.run()
    # ad_manager.UnregisterAdvertisement(advertisement)
    # dbus.service.Object.remove_from_connection(advertisement)

if __name__ == "__main__":
    main()