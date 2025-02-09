# MineSweeper

## Overview
Welcome to our Capstone Team 5 Repository for our MineSweeper Project. We plan to add more so please be patient.

### WiFi Hotspot for File Transfer
- SSID: rpi-team5
- PWD: minesweeper

#### Command to resume hotspot
sudo nmcli device up wlan0

#### Command to enable hotspot (initialization)
sudo nmcli device wifi hotspot ssid [network-name] password [custom-password]

#### Command to disable hotspot
sudo nmcli device disconnect wlan0