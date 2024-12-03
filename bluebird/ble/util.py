import dbus

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"

def find_adapter(bus):
    """
    Returns the first object that the bluez service has that has a GattManager1 interface
    """
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
    
    objects = remote_om.GetManagedObjects()
    print(objects)
    for o, props in objects.items():
        if GATT_MANAGER_IFACE in props.keys():
            return o

    return None