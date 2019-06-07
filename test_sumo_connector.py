#!/usr/bin/env python3
import unittest
import sys
import json
import os
import queue
import threading
import time
from argparse import ArgumentParser
sys.path += [os.path.join(os.path.dirname(__file__), "..", "python-test-bed-adapter")]
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter
import sumo_connector

import logging
logging.basicConfig(level=logging.INFO)


class ProducerExample:
    def __init__(self):
        self._queue = queue.Queue()
        self._test_bed_adapter = None
        self._connector = None

    def addToQueue(self, message):
        self._queue.put(message['decoded_value'][0])

    def sendTime(self):
        t = 0
        while self._connector is not None:
            message = [{"state": "Started", "trialTime": t}]
            self._connector.addToQueue({"decoded_value": message})
            time.sleep(1)
            t += 1000

    def sendMessage(self, manager, msgFile):
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), msgFile)
        message = [json.load(open(message_path))]
        if self._test_bed_adapter is not None:
            self._test_bed_adapter.producer_managers[manager].send_messages(message)
        else:
            self._connector.addToQueue({"decoded_value": message})

    def main(self, host, port, scenario, log, ownerFilter):
        options = {
            "auto_register_schemas": True,
            "schema_folder": 'data/schemas',
            "kafka_host": "%s:%s" % (host, port),
            "schema_registry": 'http://%s:%s' % (host, port+1),
            "reset_offset_on_start": True,
            "offset_type": "LATEST",
            "client_id": 'Test SUMO Connector',
            "consume": ["simulation_entity_item"],
            "produce": ["sumo_SumoConfiguration", "sumo_AffectedArea", "simulation_request_unittransport"]}

        if host != "none":
            self._test_bed_adapter = TestBedAdapter(TestBedOptions(options))
            self._test_bed_adapter.on_message += self.addToQueue
            # This function will act as a handler. It only prints the message once it has been sent
            self._test_bed_adapter.on_sent += lambda message : logging.info("\n\n------\nmessage sent:\n------\n\n" + str(message))
            self._test_bed_adapter.initialize()
            time.sleep(5)
        else:
            self._connector = sumo_connector.SumoConnector(msgReceiver=self)

        # Start simulation
        self.sendMessage("sumo_SumoConfiguration", os.path.join(scenario, "Configuration.json"))

        # Send affected area
#        time.sleep(5)
# TODO check why SUMO collapses if I activate this one
        self.sendMessage("sumo_AffectedArea", os.path.join(scenario, "AffectedArea.json"))

        # Send routing request
        time.sleep(5)
        self.sendMessage("simulation_request_unittransport", os.path.join(scenario, "simulation_request_unittransport.json"))

        # Try to send the same message again (still failing)
        #time.sleep(5)
        #self.sendMessage("simulation_request_unittransport", os.path.join(scenario, "simulation_request_unittransport.json"))

        if host != "none":
            threads = []
            for topic in options["consume"]:
                threads.append(threading.Thread(target=self._test_bed_adapter.consumer_managers[topic].listen_messages))
                threads[-1].start()
        else:
            threading.Thread(target=self._connector.run).start()
            threading.Thread(target=self.sendTime).start()
        logFile = open(log, "w") if log else None
        while True:
            message = self._queue.get()
            if "owner" not in message or message["owner"] != ownerFilter:
                logging.info("\n\n-----\nReceived message\n-----\n\n" + str(message))
                if log and "updatedAt" not in message:
                    print(message, file=logFile)
                    logFile.flush()


if __name__ == '__main__':
    argParser = ArgumentParser()
    argParser.add_argument("scenario", help="the (directory) name of the scenario to run")
    argParser.add_argument("--log", help="the file name of log output", metavar="FILE")
    argParser.add_argument("-s", "--server", default="localhost",
                           help="define the server; other possible values: 'tb6.driver-testbed.eu:3561', 'driver-testbed.eu', '129.247.218.121'")
    argParser.add_argument("-v", "--verbose", action="store_true", default=False,
                           help="tell me what you are doing")
    argParser.add_argument("-f", "--filter", default="Thales.SE-Star", help="filter incoming messages for the given owner")
    options = argParser.parse_args()

    if options.log is None:
        options.log = options.scenario + ".log"

    if ":" not in options.server:
        host = options.server
        port = 3501
    else:
        host, port = options.server.split(":")
    ProducerExample().main(host, int(port), options.scenario, options.log, options.filter)
