#!/usr/bin/env python3

import logging

logger = logging.getLogger(__name__)


class IoMBianSystemInfoDisplayer(object):

    def __init__(self, info_receiver, display_driver):
        self.info_receiver = info_receiver
        self.display_driver = display_driver

    def start(self):
        logger.debug("Starting IoMBian System Info Displayer")
        self.info_receiver.set_message_callback(self.__on_message_callback)
        self.info_receiver.start()

    def stop(self):
        logger.debug("Stoping IoMBian System Info Displayer")
        self.info_receiver.stop()

    def __on_message_callback(self, info):
        logger.debug(f"New info to be displayed: {info}")
        lines = self.__info_to_lines(info)
        logger.debug("Number of lines to be displayed: {}".format(len(lines)))
        self.display_driver.render_lines(lines)

    def __info_to_lines(self, info):
        lines = []
        if "hostname" in info:
            lines.append("Host: {}".format(info.get("hostname")))
        if "system_time" in info and "uptime" in info:
            lines.append("Time: {} (Uptime: {})".format(info.get("system_time"), info.get("uptime")))
        if "used_disk" in info and "total_disk" in info and "percent_disk" in info:
            lines.append("Storage: {}/{}GB ({}%)".format(info.get("used_disk"), info.get("total_disk"), info.get("percent_disk")))
        if "local_network" in info:
            lines.append("Network: {}".format("Connected" if info.get("local_network", {}).get("status", False) else "Not connected"))
            for key, value in info.get("local_network", {}).get("interfaces", {}).items():
                lines.append("    {}: {}".format(key, value))
        if "internet_status" in info:
            lines.append("Internet: {}".format("Connected" if info.get("internet_status", False) else "Not connected"))
        return lines