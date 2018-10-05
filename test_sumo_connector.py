#!/usr/bin/env python3
import unittest
import sys
import json
import os
import queue
import threading
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

    def main(self):
        options = {
            "auto_register_schemas": True,
            "schema_folder": 'data/schemas',
            # "kafka_host": 'driver-testbed.eu:3501',
            # "schema_registry": 'http://driver-testbed.eu:3502',
            "kafka_host": '127.0.0.1:3501',
            "schema_registry": 'http://localhost:3502',
            "reset_offset_on_start": True,
            "client_id": 'Test SUMO Connector',
            "consume": ["simulation_entity_item"],
            "produce": ["sumo_SumoConfiguration", "sumo_AffectedArea"]}

        test_bed_options = TestBedOptions(options)
        test_bed_adapter = TestBedAdapter(test_bed_options)

        # This funcion will act as a handler. It only prints the message once it has been sent
        message_sent_handler = lambda message : logging.info("\n\n------\nmessage sent:\n------\n\n" + str(message))
        test_bed_adapter.on_message += self.addToQueue
        test_bed_adapter.on_sent += message_sent_handler

        test_bed_adapter.initialize()

        # The current configuration expects the Time Service to start on 2018-09-26 09:00:00
        # The simulation starts at 2018-09-26 09:01:00 and ends at 2018-09-26 09:02:00
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acosta", "Configuration.json")
        message = {"messages":json.load(open(message_path))}
        test_bed_adapter.producer_managers["sumo_SumoConfiguration"].send_messages(message)

        # The affected area is valid from 2018-09-26 09:01:10 until 2018-09-26 09:01:50
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acosta", "AffectedArea.json")
        message = {"messages":json.load(open(message_path))}
        test_bed_adapter.producer_managers["sumo_AffectedArea"].send_messages(message)

        threads = []
        for topic in options["consume"]:
            threads.append(threading.Thread(target=test_bed_adapter.consumer_managers[topic].listen_messages))
            threads[-1].start()
        while True:
            message = self._queue.get()
            logging.info("\n\n-----\nReceived message\n-----\n\n" + str(message))

if __name__ == '__main__':
    ProducerExample().main()
