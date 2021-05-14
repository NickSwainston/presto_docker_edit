ARG VER=v4.0.1
FROM nickswainston/presto:${VER}

# Add bc for some command line math
RUN apt-get update -qq && \
    apt-get -y --no-install-recommends install \
    bc \
    xauth && \
    apt-get clean all && \
    rm -r /var/lib/apt/lists/*

# Install tempo2
WORKDIR /home/soft/tempo2
ENV TEMPO2 /home/soft/tempo2
RUN wget https://sourceforge.net/projects/tempo2/files/latest/download && \
    tar -xzvf download && \
    rm download && \
    cp -r tempo2*/T2runtime/ $TEMPO2

ADD ACCEL_sift.py /usr/bin/
