FROM seleniarm/standalone-chromium
RUN sudo apt update
RUN DEBIAN_FRONTEND="noninteractive" sudo apt -y install tzdata
RUN sudo apt install -y python python3 python3-pip build-essential libssl-dev libffi-dev python-dev && sudo rm -rf /var/lib/apt/lists/*
RUN pip3 install selenium paho-mqtt pickle-secure
RUN sudo mkdir /session
RUN sudo chmod 777 /session
COPY src/* /opt/bin/
RUN sudo chmod +x /opt/bin/start.sh
CMD ["/opt/bin/start.sh"]