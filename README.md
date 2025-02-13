# MineSweeper
**Authors:** Alston, Anthony, Brian, Isaac, Pyo, Thomas

## Overview
Welcome to our Capstone Team 5 Repository for our MineSweeper Project. We will be using a Raspberry Pi with multiple sensors to create a Probability Map of where points of interests can be located in a minefield. 

## Testing Scripts
There will be files for users to execute when testing MineSweeper.
The data from the scripts will be stored in the `data` directory.
- To test all scripts, execute `test.sh` in superuser mode.
- To clear data directory, add `-c` flag in the arguments.
- To see all flag options, add `-h` flag in the arguments.

### WiFi Hotspot for File Transfer
- **SSID:** rpi-team5
- **PWD:** minesweeper

#### Command to resume hotspot
`sudo nmcli device up wlan0`

#### Command to enable hotspot (initialization)
`sudo nmcli device wifi hotspot ssid [network-name] password [custom-password]`

#### Command to disable hotspot
`sudo nmcli device disconnect wlan0`