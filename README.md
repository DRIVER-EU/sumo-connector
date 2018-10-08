# sumo-connector
Connecting the Test-bed to DLR's open-source traffic simulator SUMO.
This is an example to connect the open-source microscopic traffic simulation SUMO with the Apache Kafka test-bed with use of the test-bed's python adapter, so that the test-bed can send messages to SUMO and SUMO can take them into considerations during simulation. SUMO can also send messages back to the test-bed.
# Installation
Before you use this connector on your computer/laptop, you need to
 - Set-up the Kafka test-bed (see the related instruction under https://github.com/DRIVER-EU)
 - Install Python 3+
 - Install matplotlib
 - Install pyproj
 - Get SUMO 1+ under http://sumo.dlr.de/wiki/Downloads
 - Clone sumo-connector
 - Clone python-testbed-adapter
# Scenario
The used scenario is a part of the City Bologna, Italy. All the related data can be found under the directory acosta.
- Description

- Outputs

# Execution
After the installation, you need to execute the sumo_connector.py and test_sumo_connector.py as well as to start the time service at the test-bed, which you set up.
