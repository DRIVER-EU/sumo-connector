# to build this image run the following command
# $ docker build -t sumo-connector:git - < Dockerfile

FROM dlrts/sumo:latest
ENV SUMO_HOME=/usr/share/sumo
RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git python3-pip python3-matplotlib
RUN mkdir -p /opt/application;
WORKDIR /opt/application
RUN git clone https://github.com/DRIVER-EU/avro-schemas; git clone https://github.com/DRIVER-EU/python-test-bed-adapter;
WORKDIR /opt/application/python-test-bed-adapter
RUN pip3 install -r ./requirements.txt
RUN mkdir -p /opt/application/sumo-connector
WORKDIR /opt/application/sumo-connector
COPY . .
CMD ["python3", "./sumo_connector.py", "--nogui"]
