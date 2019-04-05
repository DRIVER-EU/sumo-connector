#!/usr/bin/env python3
import unittest
import sys
import json
import os
import queue
import threading
import time
sys.path += [os.path.join(os.path.dirname(__file__), "..", "python-test-bed-adapter")]
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter

import logging
logging.basicConfig(level=logging.INFO)

class ProducerExample:
    def __init__(self):
        self._queue = queue.Queue()

    def addToQueue(self, message):
        self._queue.put(message['decoded_value'][0])

    def main(self, host, port, scenario, log=None):
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

        test_bed_options = TestBedOptions(options)
        test_bed_adapter = TestBedAdapter(test_bed_options)

        # This function will act as a handler. It only prints the message once it has been sent
        message_sent_handler = lambda message : logging.info("\n\n------\nmessage sent:\n------\n\n" + str(message))
        test_bed_adapter.on_message += self.addToQueue
        test_bed_adapter.on_sent += message_sent_handler

        test_bed_adapter.initialize()

        # The current configuration expects the Time Service to start on 2018-09-26 09:00:00
        # The simulation starts at 2018-09-26 09:01:00 and ends at 2018-09-26 09:02:00
        time.sleep(5)
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), scenario, "Configuration.json")
        test_bed_adapter.producer_managers["sumo_SumoConfiguration"].send_messages([json.load(open(message_path))])

        # The affected area is valid from 2018-09-26 09:01:10 until 2018-09-26 09:01:50
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), scenario, "AffectedArea.json")
#        test_bed_adapter.producer_managers["sumo_AffectedArea"].send_messages([json.load(open(message_path))])

        time.sleep(5)
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), scenario, "simulation_request_unittransport.json")
        test_bed_adapter.producer_managers["simulation_request_unittransport"].send_messages([json.load(open(message_path))])

        threads = []
        for topic in options["consume"]:
            threads.append(threading.Thread(target=test_bed_adapter.consumer_managers[topic].listen_messages))
            threads[-1].start()
        logFile = open(log, "w") if log else None
        while True:
            message = self._queue.get()
            logging.info("\n\n-----\nReceived message\n-----\n\n" + str(message))
            if log and "updatedAt" not in message:
                print(message, file=logFile)
                logFile.flush()


if __name__ == '__main__':
    host = "localhost" # other possible values: 'tb6.driver-testbed.eu:3561', 'driver-testbed.eu', '129.247.218.121'
    scenario = "acosta" # the name of the scenario directory; the other existing example scenario: 'WorldForumTheHague' or the self-defined scenario
    if len(sys.argv) > 1:
        if ":" not in sys.argv[1]:
            host = sys.argv[1]
            port = 3501
        else:
            host, port = sys.argv[1].split(":")
    if len(sys.argv) > 2:
        scenario = sys.argv[2]
    log = scenario + ".log"
    if len(sys.argv) > 3:
        log = sys.argv[3]
    ProducerExample().main(host, int(port), scenario, log)
