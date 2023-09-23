# ruuvitag
A ruuvitag is a weatherproof, battery powered sensor which reports temperature, humidity, pressure and motion via Bluetooth Low Energy (BLE) beacons. This repo shows how to define Ruuvitags to listen and write their values to AWS Timestream.

## Deploy
[![](https://balena.io/deploy.svg)](https://dashboard.balena-cloud.com/deploy?repoUrl=https://github.com/ahtonen/ruuvitag)

Just click the button, create or sign-in to your balenaCloud account, add your device and start sending Ruuvitag data!

## Balena device configuration

Each device must have these environment variables set. First defines RuuviTag MACs to listen and second their aliases.
```
RUUVITAG_MACS_TO_LISTEN=['ED:BD:47:DA:64:D4', 'C9:50:B1:7D:A8:8F']
RUUVITAG_MAC_ALIASES={'ED:BD:47:DA:64:D4': 'sauna', 'C9:50:B1:7D:A8:8F': 'outside'}
```
Setting first variable to `[]` means listening all MACs.

## Hardware required
* Raspberry Pi or balenaFin (see [supported devices](#supported-devices) )
* A [ruuvitag](https://shop.ruuvi.com/product/ruuvitag-1-pack/)

## Software required
* A free [balenaCloud account](https://dashboard.balena-cloud.com/signup) (first ten devices are free and fully-featured, no credit card needed to start)
* A tool to flash OS images to SD cards, like [balenaEtcher](https://www.balena.io/etcher/)

## Supported devices
This project has been tested to work on the following devices:

| Device Type  | Status |
| ------------- | ------------- |
| Raspberry Pi 3b+ (64-bit OS) | ✔ |
