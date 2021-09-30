#!/bin/bash

PLATFORM=${PLATFORM:-`sonic-cfggen -H -v DEVICE_METADATA.localhost.platform`}
set -x
ln -s /usr/share/sonic/device/$PLATFORM /tmp/sonic_dev
ln -s /usr/local/lib/python3.7/dist-packages/sonic_platform /tmp/py_sonic_platform
