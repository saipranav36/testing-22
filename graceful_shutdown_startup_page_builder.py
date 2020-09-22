from page_builders.base_page_builder import *
import json

SHUTDOWN_STARTUP_PLUGIN_PAGE_PATH = '/opt/install/backend/plugins/graceful_shutdown_startup/graceful_shutdown_startup.json'

class GracefulShutdownStartupPageBuilder(BasePageBuilder):
    def __init__(self, logger):
        super(GracefulShutdownStartupPageBuilder, self).__init__(logger)

    def build(self):
        self.log.info("building Graceful Shutdown Startup plugin main page")
        self.dict_from_json = \
            self.cbis_helper.get_dict_from_file(
                SHUTDOWN_STARTUP_PLUGIN_PAGE_PATH)
       
        # to change something in the json it is possible to edit the dict here
        # before returning it as an answer in the API

        self.log.info("finished building graceful shutdown startup  main page")
        return self.dict_from_json

