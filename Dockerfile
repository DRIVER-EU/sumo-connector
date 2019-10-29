# to build this image run the following command
# $ docker build -t sumo-connector:git - < Dockerfile

FROM dlrts/sumo:latest

RUN apt-get -y install git
RUN mkdir /opt/application; cd /opt/application; git clone https://github.com/DRIVER-EU/avro-schemas; git clone https://github.com/DRIVER-EU/python-test-bed-adapter; git clone https://github.com/DRIVER-EU/sumo-connector
CMD ["python3", "/opt/application/sumo-connector/sumo-connector.py", "--nogui"]
