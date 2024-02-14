FROM    molssi/mamba141
RUN     apt-get install -qy curl && curl -sSL https://get.docker.com/ | sh
COPY    seamm.yml /root/seamm.yml
RUN     mamba env update --name base --file /root/seamm.yml
WORKDIR /home
ENV     SEAMM_ENVIRONMENT=docker

