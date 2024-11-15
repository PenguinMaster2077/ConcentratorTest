# Concentrator test manual

# Setup
| Name | Type | Voltage | ADC channel | HUV channel |
| :--- | :--- | :--- | :--- | :--- |
| Test PMT | NightVision PM2211-1051 | 1636 V |	? | 33 |
| Cal PMT | NightVision PM2208-9140 | 1696 V | ? | 31 |
| LED | xxx nm | xxx | xxx | xxx |

# How to measure data:

## Steps for measuring light concentrator
1. Open the Dark Box lid, and move light source to specific angle and distance
2. Close the Dark Box lid, and put shade on it
3. Turn on the test PMT and cali PMT and wait for the voltage to set level
4. Change info in `/home/tao/Concentrator/data/config/setting.csv`
5. Waiting for xxx minutes to allow the dark noise to settle to a constant level
6. Execute the `make sample` command to start data acquisition
7. Move data files to Backup disk
8. Start next measurement according step 1-7

## Facility setting
+ A csv records the setting.
  + runno
  + filenum: estimate sample time duration
  + angle
  + distance

## Readout
+ The code is under `pcie_control/tools`, compile and generate the executable `build/pcie_control`
```shell
# Compile using CMake
mkdir -p build && cd build
cmake ..
make
```
+ General configuration: `Makefile`
  + data output path: `datadir` the data is stored in the path.
+ Sample as the administrator:
```shell
# check the sample setting
make mock_sample
# sample
make sample
```

## Analysis
