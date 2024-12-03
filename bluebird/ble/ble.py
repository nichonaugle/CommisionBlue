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
from .base import BaseService, BaseCharacteristic, BaseAdvertisement, BaseApplication
from .util import find_adapter

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
        self.add_characteristic(PayloadCharacteristic(bus, 1, self))

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
        #self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

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
            self, bus, index, CHARACTERISTIC_UUID_PAYLOAD, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = []
        #self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        logger.info("auto off write: " + repr(value))
        cmd = bytes(value)

        # write it to machine
        logger.info(f"writing {cmd} to machine")
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
    # PASSES
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._mainloop = GLib.MainLoop()
        self._running_mainloop = None #MainLoop()
        self._bus = dbus.SystemBus()
        self._adapter = find_adapter(self._bus)
        self._adapter_obj = self._bus.get_object(BLUEZ_SERVICE_NAME, self._adapter)
        self._adapter_props = dbus.Interface(self._adapter_obj, "org.freedesktop.DBus.Properties")
        self._service_manager = dbus.Interface(self._adapter_obj, GATT_MANAGER_IFACE)
        self._advertising_manger = dbus.Interface(self._adapter_obj, LE_ADVERTISING_MANAGER_IFACE)
        self._bluez_obj = self._bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")
        # self._agent = Agent(self._bus, AGENT_PATH)
        self.app = None
    
    def start(self):
        if not self._adapter:
            print("GattManager1 interface not found") #logger.critical("GattManager1 interface not found")
            sys.exit(1)
        
        self._adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1)) # powered property on the controller to on
        advertisement = CommissioningAdvertisement(self._bus, 0)
        self.app = BaseApplication(self._bus)
        self.app.add_service(CommissioningService(self._bus, 2))
        self._advertising_manger.RegisterAdvertisement(
            advertisement.get_path(),
            {},
            reply_handler=self.register_ad_cb,
            error_handler=self.register_ad_error_cb,
        )
        #logger.info("Registering GATT application...")
        self._service_manager.RegisterApplication(
            self.app.get_path(),
            {},
            reply_handler=self.register_app_cb,
            error_handler=self.register_app_error_cb,
        )
        # agent_manager = dbus.Interface(_bluez_obj, "org.bluez.AgentManager1")
        # agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
        # agent_manager.RequestDefaultAgent(AGENT_PATH)
        self._mainloop.run()
    
    def register_ad_cb(self):
        print("Advertisement registered")

    def register_app_cb(self):
        print("Application registered")

    def register_ad_error_cb(self, error):
        print("Failed to register advertisement: " + str(error))
        self._mainloop.quit()
    
    def register_app_error_cb(self, error):
        print("Failed to register application: " + str(error))
        self._mainloop.quit()