FROM ubuntu:18.04
RUN apt-get update ; apt-get -y install rig boxes
ADD genid.sh /bin/genid.sh
RUN chmod +x /bin/genid.sh
ENTRYPOINT ["/bin/genid.sh"]
