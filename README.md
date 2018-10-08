# sumo-connector
Connecting the Test-bed to DLR's open-source traffic simulator SUMO.
This is an example to connect the open-source microscopic traffic simulation SUMO with the Apache Kafka test-bed with use of the test-bed's python adapter, so that the test-bed can send messages to SUMO and SUMO can take them into considerations during simulation. SUMO can also send messages back to the test-bed.
# Installation
Before you use this connector on your computer/laptop, you need to
 - Set-up the Kafka test-bed (see the related instruction under https://github.com/DRIVER-EU)
 - Install Python 3+
 - Install matplotlib
   - pip install matplotlib
 - Download/install pyproj
   - download website: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj
   - use pip to install pyproj
 - Clone/install the python-testbed-adapter (see the instruction under https://github.com/DRIVER-EU/python-test-bed-adapter)
 - Clone the sumo-connector
 - Get SUMO 1+ under http://sumo.dlr.de/wiki/Downloads
# Scenario
Adter cloning the sumo-connector you will find a directory called acosta, which is the example scenario. This scenario is a part of the City Bologna in Italy. All the related simulation data can be found under the directory acosta.
- Description
  A intersection is closed in this scenario. A The test-bed will inform

- Output
   The data (vehicle type, slope, speed, position and angle) for each single vehicle will be sent to the test-bed at each sample interval, defined in the Configuration.json under the directory acosta.
# Execution
After the installation, you need to execute the sumo_connector.py and test_sumo_connector.py as well as to start the time service at the test-bed, which you set up.
