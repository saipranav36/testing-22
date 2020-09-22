from api.base_page_api import PageBluePrint
from plugins.graceful_shutdown_startup.graceful_shutdown_startup import GracefulShutdownStartup
from plugins.graceful_shutdown_startup.graceful_shutdown_startup_page_builder import GracefulShutdownStartupPageBuilder
from common.constants import DeploymentStates
import os.path
from flask import jsonify

VLAN_VALIDATION_LOG_PATH = '/var/log/cbis/graceful_shutdown_startup.log'
VLAN_VALIDATION_LOG_LEVEL = "DEBUG"


class GracefulShutdownStartupPageBlueprint(PageBluePrint):
    def __init__(self):
        super(GracefulShutdownStartupPageBlueprint, self).__init__(
            page_name="graceful_shutdown_startup",
            flow_class=GracefulShutdownStartup,
            page_builder_class=GracefulShutdownStartupPageBuilder,
            log_path=VLAN_VALIDATION_LOG_PATH,
            log_level=VLAN_VALIDATION_LOG_LEVEL,
           # require_undercloud_installed=True,
           # require_full_cbis_installed=True,
           # require_undercloud_installation_process_inactive=True
        )


    def get_test_status(self):
        plugin_state = DeploymentStates.NEW
        running = self._is_flow_process_running()
        if running:
            plugin_state = DeploymentStates.IN_PROGRESS
        else:
            file_path = os.getcwd() + "/plugins/graceful_shutdown_startup/tmp/status.yaml"
            if os.path.exists(file_path):
                status = self.cbis_helper.get_dict_from_file(file_path)
                plugin_state = status['status']
        return plugin_state

    def get_state(self):
        plugin_state = self.get_test_status()
        return jsonify({"state": plugin_state})

