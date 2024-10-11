# ruuvitag
A ruuvitag is a weatherproof, battery powered sensor which reports temperature, humidity, pressure and motion via Bluetooth Low Energy (BLE) beacons. This repo shows how to define Ruuvitags to listen and write their values to AWS Timestream. The system is scalable by utilizing Balena fleet. Setting up the AWS side is left for the reader.

<img src="./architecture.png" alt="architecture diagram" width="80%" class="center"/>

## Sensor application
Since the recommended way of reading Ruuvi measuments is registering a handler, the application is split into two processes: one filling the queue and one emptying it. Python's `multiprocessing` library is used for this purpose.

## Deploy
[![](https://balena.io/deploy.svg)](https://dashboard.balena-cloud.com/deploy?repoUrl=https://github.com/ahtonen/ruuvitag)

Just click the button, create or sign-in to your balenaCloud account, add and configure your device and start sending Ruuvitag data.

## Balena fleet and device configuration
Easiest way to prepare for scaling is to setup environment variables that are shared between devices as fleet variables:
```
AWS_ACCESS_KEY_ID
AWS_REGION
AWS_SECRET_ACCESS_KEY
AWS_WRITE_INTERVAL
MAX_EMPTY_QUEUE_COUNT
DATABASE
TABLE
```
From variables that are not self-evident `AWS_WRITE_INTERVAL` is seconds between writes to AWS Timestream, `60` by default. As the process writing to AWS Timestream is emptying the queue on given intervals, it sometimes happens that Linux BT stack gets an issue and no measurements are received by Ruuvi's library. To fix this *feature* in Linux's BT stack, it was decided to try to ask Balena OS supervisor to restart the `sensor` container, if the queue has been empty `MAX_EMPTY_QUEUE_COUNT` times. So with 60s interval and max count of 10, it would mean a forced restart, if no measurements has been received during last 10 minutes.

In addition you need to define following environment variables for each device:
```
COUNTRY
CITY
PLACE
RUUVITAG_MAC_ALIASES
```
First three are defined as *attributes* in AWS Timestream. Last variable binds finally Ruuvitag MAC to location like this:
```
RUUVITAG_MAC_ALIASES={'ED:BD:47:DA:64:D4': 'sauna', 'C9:50:B1:7D:A8:8F': 'balcony'}
```
Location is the last of total 4 unique attributes for each AWS record.

## Hardware required
* Raspberry Pi or balenaFin (see [supported devices](#supported-devices) )
* [Ruuvitag](https://shop.ruuvi.com/product/ruuvitag-1-pack/)(s)

## Software required
* A free [balenaCloud account](https://dashboard.balena-cloud.com/signup) (first ten devices are free and fully-featured, no credit card needed to start)
* A tool to flash OS images to SD cards, like [balenaEtcher](https://www.balena.io/etcher/)

## Supported devices
This project *has been tested to work* on the following devices:

| Device Type  | Status |
| ------------- | ------------- |
| Raspberry Pi 3b+ (64-bit OS) | ✔ |
