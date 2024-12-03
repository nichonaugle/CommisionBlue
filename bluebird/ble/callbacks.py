def register_app_cb():
    logger.info("Something happened")

def register_app_error_cb(error):
    logger.critical("Failed: " + str(error))

def big_error(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()
