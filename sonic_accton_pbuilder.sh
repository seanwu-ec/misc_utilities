#!/bin/bash
PATH_TO_SONIC_BUILDIMAGE_DIR=/home/ubuntu/src/sonic-buildimage
#SLAVEIMAGE=sonic202012-barefoot-pbuilder:latest
SLAVEIMAGE=sonic-accton-pbuilder:ef67ba5f6
ENV_LINUX_HEADER="KERNEL_SRC=/usr/src/linux-headers-4.19.0-12-2-amd64/"
docker run --rm=true --privileged --init -e "$ENV_LINUX_HEADER" -v "$PATH_TO_SONIC_BUILDIMAGE_DIR:/sonic" -w "/sonic" -it $SLAVEIMAGE /bin/bash

