import dbus
import sys
import dbus.service
import dbus.exceptions
from gi.repository import GLib
import dbus.mainloop.glib
import struct
import requests
import array
import logging
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
CHARACTERISTIC_UUID_AVALIABLE_SSIDS = "51FF12BB-3ED8-46E5-AD5B-D64E2F21B21B"
CHARACTERISTIC_UUID_PUBLIC_KEY = "bfc0c92f-317d-4ba9-976b-cc11ce77b21B"

AGENT_PATH = "/commission/agent"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

class CommissioningService(BaseService):
    def __init__(self, bus, index):
        BaseService.__init__(self, bus, index, SERVICE_UUID, True)
        self.ssid_characteristic = SsidCharacteristic(bus, 0, self)
        self.payload_characteristic = PayloadCharacteristic(bus, 1, self)
        self.available_ssids_characteristic = AvaliableSsidsCharacteristic(bus, 2, self)
        self.public_key_characteristic = PublicKeyCharacteristic(bus, 3, self)

        self.add_characteristic(self.ssid_characteristic)
        self.add_characteristic(self.payload_characteristic)
        self.add_characteristic(self.available_ssids_characteristic)
        self.add_characteristic(self.public_key_characteristic)

class SsidCharacteristic(BaseCharacteristic):
    description = b"Plaintext SSID"

    def __init__(self, bus, index, service):
        BaseCharacteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID_SSID, ["encrypt-read", "encrypt-write"], service,
        )
        self.value = [0x0000]

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        logger.info("auto off write: " + repr(value))
        cmd = bytes(value)

        # write it to machine
        logger.info(f"writing {cmd} to machine")
        self.value = value

class PayloadCharacteristic(BaseCharacteristic):
    description = b"Encrypted Password (With AES and ECC)"

    def __init__(self, bus, index, service):
        BaseCharacteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID_PAYLOAD, ["encrypt-read", "encrypt-write"], service,
        )
        self.value = [0x0000]

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        logger.info("auto off write: " + repr(value))
        cmd = bytes(value)

        # write it to machine
        logger.info(f"writing {cmd} to machine")
        self.value = value

class AvaliableSsidsCharacteristic(BaseCharacteristic):
    description = b"Avaliable SSIDs"

    def __init__(self, bus, index, service):
        BaseCharacteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID_AVALIABLE_SSIDS, ["secure-read"], service,
        )

        self.value = [0xFF]
        #self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self)) Make a rescan characteristic?

    def ReadValue(self, options):
        return self.value

class PublicKeyCharacteristic(BaseCharacteristic):
    description = b"Public Key"

    def __init__(self, bus, index, service):
        BaseCharacteristic.__init__(
            self, bus, index, CHARACTERISTIC_UUID_PUBLIC_KEY, ["secure-read"], service,
        )

        self.value = [0x69]
        #self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self)) Make a regen characteristic?
    def ReadValue(self, options):
        return self.value

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
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._mainloop = GLib.MainLoop()
        self._bus = dbus.SystemBus()
        self._adapter = find_adapter(self._bus)
        self._adapter_obj = self._bus.get_object(BLUEZ_SERVICE_NAME, self._adapter)
        self._adapter_props = dbus.Interface(self._adapter_obj, "org.freedesktop.DBus.Properties")
        self._service_manager = dbus.Interface(self._adapter_obj, GATT_MANAGER_IFACE)
        self._advertising_manger = dbus.Interface(self._adapter_obj, LE_ADVERTISING_MANAGER_IFACE)
        self._bluez_obj = self._bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")
        self._commissioning_service = CommissioningService(self._bus, 2)
        self.app = None
        self.params = {
            "avaliable_ssids": self._commissioning_service.payload_characteristic.ReadValue(None),
            "ssid": self._commissioning_service.ssid_characteristic.ReadValue(None),
            "payload": self._commissioning_service.payload_characteristic.ReadValue(None),
            "public-key": self._commissioning_service.public_key_characteristic.ReadValue(None)
        }
    
    def start(self):
        if not self._adapter:
            logger.critical("GattManager1 interface not found")
            sys.exit(1)
        
        self._adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))
        advertisement = CommissioningAdvertisement(self._bus, 0)
        self.app = BaseApplication(self._bus)
        self.app.add_service(self._commissioning_service)
        self._advertising_manger.RegisterAdvertisement(
            advertisement.get_path(),
            {},
            reply_handler=self.register_ad_cb,
            error_handler=self.register_ad_error_cb,
        )
        self._service_manager.RegisterApplication(
            self.app.get_path(),
            {},
            reply_handler=self.register_app_cb,
            error_handler=self.register_app_error_cb,
        )
        agent_manager = dbus.Interface(self._bluez_obj, "org.bluez.AgentManager1")
        agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
        agent_manager.RequestDefaultAgent(AGENT_PATH)
        self._mainloop.run()
    
    def close(self):
        logger.info("Shutting off commissioner") 
        self._mainloop.quit()

    def register_ad_cb(self):
        logger.info("Advertisement registered")

    def register_app_cb(self):
        logger.info("Application registered")

    def register_ad_error_cb(self, error):
        logger.critical("Failed to register advertisement: " + str(error))
        self._mainloop.quit()
    
    def register_app_error_cb(self, error):
        logger.critical("Failed to register application: " + str(error))
        self._mainloop.quit()