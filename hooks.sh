#!/bin/sh
apt-get -q update > /dev/null
apt-get -q -y install git > /dev/null
python -m pip -q install ruuvitag-sensor
mamba install -q -y pylint black boto3 pytz
