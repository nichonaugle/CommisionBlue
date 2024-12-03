from bluebird.ble import BluebirdCommissioner

commissioner = BluebirdCommissioner()
try:
    commissioner.start()
except KeyboardInterrupt:
    commissioner.close()