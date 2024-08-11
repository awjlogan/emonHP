# emonHP - Heat Pump Monitoring

## Introduction

_emonHP_ is a system for monitoring heat pump operation. It is designed to work with [OpenEnergyMonitor](https://openenergymonitor.org), but can be used as a standalone system.

## Getting started

- Purchase a heat pump monitoring system from the [OpenEnergyMonitor Shop](https://shop.openenergymonitor.com/)
- Build your own board!
  - With [KiCad](https://www.kicad.org/) installed, run `./generate.py` in the `pcb` directory (Linux and macOS only) to generate manufacturing files (KiCad PCB, Gerbers, BoM).

## Hardware Overview

The system provides the following interfaces:

- MBUS interface
- RS485 interface
- AC-coupled current transformer (CT) input
- 2x configurable analog, OneWire, or pulse input
