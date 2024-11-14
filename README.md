# Concentrator test manual

# Setup
| Name | Type | Voltage | ADC channel | HUV channel |
| :--- | :--- | :--- | :--- | :--- |
| Test PMT | NightVision PM2211-1051 | 1636 V |	? | 33 |
| Cal PMT | NightVision PM2208-9140 | 1696 V | ? | 31 |
| LED | xxx nm | xxx | xxx | xxx |

# How to measure data:

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
