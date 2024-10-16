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

def register_app_cb():
    logger.info("Something happened")

def register_app_error_cb(error):
    logger.critical("Failed: " + str(error))

def big_error(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()
