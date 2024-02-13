FROM    molssi/mamba141
RUN     sudo apt-get install gcc python3-dev
COPY    seamm.yml /root/seamm.yml
RUN     mamba env update -f /root/seamm.yml
WORKDIR /home

