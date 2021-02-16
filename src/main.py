#!/usr/bin/env python3

import logging
import signal
import time

from communication_module import CommunicationModule
from iombian_system_info_displayer import IoMBianSystemInfoDisplayer
from st7735_display.st7735_controller import ST7735Controller
from sub_client import SubClient

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-20s  - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

YAML_HOST = "127.0.0.1"
YAML_PORT = 5555
SYSTEM_INFO_HOST = "127.0.0.1"
SYSTEM_INFO_PORT = 5557


def signal_handler(sig, frame):
    logger.debug("Stoping IoMBian Display Handler Service")
    display.shutdown(["IoMBian Off", "{}".format(time.strftime('%H:%M'))])
    yaml_module.stop()
    if system_info_displayer:
        system_info_displayer.stop()


if __name__ == "__main__":
    logger.info("Starting IoMBian Display Handler Service")
    display = ST7735Controller()
    display.initialize()

    yaml_module = CommunicationModule(host=YAML_HOST, port=YAML_PORT)
    yaml_module.start()

    system_info_displayer = None

    if yaml_module.execute_command("is_configured"):
        logger.info("Device correctly configured")
        system_info_client = SubClient(host=SYSTEM_INFO_HOST, port=SYSTEM_INFO_PORT)
        system_info_displayer = IoMBianSystemInfoDisplayer(info_receiver=system_info_client, display_driver=display)
        system_info_displayer.start()
    else:
        logger.info("Device not configured")
        device_name = yaml_module.execute_command("get_device_id")
        link = "https://iombian-configurator.web.app"
        display.render_config(device_name, link)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()