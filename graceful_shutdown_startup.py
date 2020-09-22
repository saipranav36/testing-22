from common.constants import UNDERCLOUD
from flows.base_flow import BaseFlow
from common.commons import CbisException
from common.constants import DeploymentStates
import os

SHUTDOWN_STARTUP_ANSIBLE_FODLER = '/opt/install/backend/plugins/graceful_shutdown_startup/shutdown_startup_scripts/'
PREREQUISITE_ANSIBLE_SCRIPT = 'prerequisite.yaml'
SHUTDOWN_ANSIBLE_SCRIPT = 'shutdown.yaml'
STARTUP_ANSIBLE_SCRIPT = 'startup.yaml'


class GracefulShutdownStartup(BaseFlow):
    check_prerequisite = True
    check_shutdown = False
    check_startup = False
    error = False

    def __init__(self, logger):
        super(GracefulShutdownStartup, self).__init__(logger)

    def set_request(self, request, page_json):
        self.log.info("Set Request ")
        super(GracefulShutdownStartup, self).set_request(request, page_json)
        request = self.request
        try:
            self.check_prerequisite = request['graceful_shutdown_startup'] \
                ['subsection_1']['prerequisite']
        except:
            self.check_prerequisite = False
        self.check_shutdown = request['graceful_shutdown_startup'] \
            ['subsection_1']['shutdown']
        self.check_startup = request['graceful_shutdown_startup'] \
            ['subsection_1']['startup']

        self.log.info("**Done setting request**")

    def deploy(self):
        self.log.info("staring graceful shutdown startup flow")
        if not self.check_shutdown and self.check_prerequisite and self.check_startup:
            self.check_prerequisite = False

        if self.check_prerequisite:
            self.prerequisite_start()

        if self.check_shutdown:
            if not self.check_prerequisite:
                self.prerequisite_start()
            self.shutdown_start()

        if self.check_startup:
            self.startup_start()

        self.define_status()

    def prerequisite_start(self):
        self.log.info ("Prerequisite Check Procedure Started")

        self.scp_cmd(os.path.join(SHUTDOWN_STARTUP_ANSIBLE_FODLER,
                                  PREREQUISITE_ANSIBLE_SCRIPT),
                     'stack@{}:/tmp'.format(UNDERCLOUD))
        try:
            self.cbis_helper.ssh_cmds(UNDERCLOUD, [
                'ansible-playbook {}'.format(
                    os.path.join('/tmp/', PREREQUISITE_ANSIBLE_SCRIPT))])
            self.log.info ("Prerequisite Check Done Successfully")
        except:
            self.log.info ("Prerequisite Check Failed")
            self.error = True

    def shutdown_start(self):
        self.log.info ("Shutdown Procedure Started It will 5 - 10 min to showing the logs")

        self.scp_cmd(os.path.join(SHUTDOWN_STARTUP_ANSIBLE_FODLER,
                                  SHUTDOWN_ANSIBLE_SCRIPT),
                     'stack@{}:/tmp'.format(UNDERCLOUD))
        try:
            self.cbis_helper.ssh_cmds(UNDERCLOUD, [
                'ansible-playbook {}'.format(
                    os.path.join('/tmp/', SHUTDOWN_ANSIBLE_SCRIPT))])
            self.log.info ("Shutdown Done Successfully")
        except:
            self.log.info ("Shutdown Failed")

            self.error = True

    def startup_start(self):
        self.log.info ("Startup Procedure Started It will 10 - 30 min to showing the logs")
        self.scp_cmd(os.path.join(SHUTDOWN_STARTUP_ANSIBLE_FODLER,
                                  STARTUP_ANSIBLE_SCRIPT),
                     'stack@{}:/tmp'.format(UNDERCLOUD))
        try:
            self.cbis_helper.ssh_cmds(UNDERCLOUD, [
                'ansible-playbook {}'.format(
                    os.path.join('/tmp/', STARTUP_ANSIBLE_SCRIPT))])
            self.log.info ("Startup Done Successfully")

        except:
            self.log.info ("Shutdown Failed")

            self.error = True

    def define_status(self):
        if self.error:
            self.update_plugin_status(DeploymentStates.FAIL)
        else:
            self.update_plugin_status(DeploymentStates.SUCCESS)

    def scp_cmd(self, src, dst):
        self.cbis_helper.cmds_run_sync(
            [
                'scp -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '
                + src + ' ' + dst])

    ''' This function to update statues plugin'''

    def update_plugin_status(self, status):
        file_path = os.getcwd() + "/plugins/graceful_shutdown_startup/tmp/status.yaml"
        f = open(file_path, "w+")
        f.write("")
        f.close()
        _status = {"status": status}
        self.cbis_helper.write_dict_to_file(file_path, _status)



