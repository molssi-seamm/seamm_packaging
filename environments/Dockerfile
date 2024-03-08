# syntax=docker/dockerfile:1

FROM       molssi/mamba141
LABEL      org.opencontainers.image.authors="Paul Saxe <psaxe@vt.edu>"
RUN        apt-get install -qy curl && curl -sSL https://get.docker.com/ | sh
COPY       seamm.yml /root/seamm.yml
RUN        mamba env update --name base --file /root/seamm.yml
ENV        SEAMM_ENVIRONMENT=docker
ENV        PATH=.:$PATH
CMD        ["seamm"]
WORKDIR    /home

