FROM ankane/pgvector:latest

USER root
RUN apt-get update && \
    apt-get install -y vim curl wget git sudo locales locales-all && \
    localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8
ENV LANG ja_JP.UTF-8

RUN useradd -m ubuntu -s /bin/bash && \
    echo "ubuntu:ubuntu" | chpasswd && \
    gpasswd -a ubuntu sudo && \
    sed -i 's/^#alias/alias/' /home/ubuntu/.bashrc

RUN update-locale LANG=ja_JP.UTF-8

WORKDIR /home/ubuntu/pgvectordb
ENTRYPOINT []

CMD ["docker-entrypoint.sh", "postgres"]
