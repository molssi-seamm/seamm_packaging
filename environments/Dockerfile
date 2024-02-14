FROM    molssi/mamba141
COPY    seamm.yml /root/seamm.yml
RUN     mamba env update --name base --file /root/seamm.yml
WORKDIR /home
ENV     SEAMM_ENVIRONMENT = docker

