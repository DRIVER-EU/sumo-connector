# to build this image run the following command
# $ docker build -t sumo-connector:git - < Dockerfile

FROM dlrts/sumo:latest

ENV SUMO_HOME=/usr/share/sumo

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git python3-pip python3-matplotlib
RUN mkdir /opt/application; cd /opt/application; git clone https://github.com/DRIVER-EU/avro-schemas; git clone https://github.com/DRIVER-EU/python-test-bed-adapter; git clone https://github.com/DRIVER-EU/sumo-connector
RUN pip3 install -r /opt/application/python-test-bed-adapter/requirements.txt
CMD ["python3", "/opt/application/sumo-connector/sumo-connector.py", "--nogui"]
