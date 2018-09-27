#!/usr/bin/env python3
import unittest
import sys
import json
import os
sys.path += [".."]
from test_bed_adapter.options.test_bed_options import TestBedOptions
from test_bed_adapter import TestBedAdapter

import logging
logging.basicConfig(level=logging.INFO)

class ProducerExample:

    def main(self):
        options = {
            "auto_register_schemas": True,
            "schema_folder": 'data/schemas',
            # "kafka_host": 'driver-testbed.eu:3501',
            # "schema_registry": 'http://driver-testbed.eu:3502',
            "kafka_host": '127.0.0.1:3501',
            "schema_registry": 'http://localhost:3502',
            "fetch_all_versions": False,
            "from_off_set": True,
            "client_id": 'PYTHON TEST BED ADAPTER',
            "produce": ["sumo_SumoConfiguration", "sumo_AffectedArea"]}

        test_bed_options = TestBedOptions(options)
        test_bed_adapter = TestBedAdapter(test_bed_options)

        # This funcion will act as a handler. It only prints the message once it has been sent
        message_sent_handler = lambda message : logging.info("\n\n------\nmessage sent:\n------\n\n" + str(message))
        test_bed_adapter.on_sent += message_sent_handler

        test_bed_adapter.initialize()

        #We load a test message from file
        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acosta", "Configuration.json")
        message = {"messages":json.load(open(message_path))}
        test_bed_adapter.producer_managers["sumo_SumoConfiguration"].send_messages(message)

        message_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acosta", "AffectedArea.json")
        message = {"messages":json.load(open(message_path))}
        test_bed_adapter.producer_managers["sumo_AffectedArea"].send_messages(message)

if __name__ == '__main__':
    ProducerExample().main()
