# emonHP - Heat Pump Monitoring

## Introduction

_emonHP_ is a system for monitoring heat pump operation. It is designed to work with [OpenEnergyMonitor](https://openenergymonitor.org), but can be used as a standalone system.

The system provides the following interfaces:

- MBUS
- RS485
- AC sense
- OneWire
- USB-C
- 40-pin Raspberry Pi header

## Getting started

### Getting a board

- Purchase a heat pump monitoring system from the [OpenEnergyMonitor Shop](https://shop.openenergymonitor.com/)
- Build your own!
  - With [KiCad](https://www.kicad.org/) installed, run `./generate.py` in the `pcb` directory (tested on Linux and macOS only) to generate manufacturing files (KiCad PCB, Gerbers, BoM).

### emonHP

> [!NOTE]
Setting up as an integrated emonHP system requires a Raspberry Pi 4. This exposes extra UART ports on the 40-pin header which are not available on older versions.

Connect the Raspberry Pi to the 40 pin header.

> [!WARNING]
Power must only be applied to one of the emonHP's USB-C port *or* the Raspberry Pi's power port, never both.

### Standalone

Connect to a host computer through the USB-C port. The emonHP will enumerate as 3 serial ports.

