.PHONY: all
settingcsv:=config/setting.py
datadir=data/$(runno)/

mock_sample: runno=$(shell awk -F, 'END {print$$1}'$(setting_csv))
mock_sample: filenum=$(shell awk -F, 'END {print$$2}'$(setting_csv))
mock_sample: config/setting.csv
	echo "RUNO:$(runno); data directory: $(datadir); filenum: $(filenum)"

sample: runno=$(shell awk -F, 'END {print$$1}'$(setting_csv))
sample: filenum=$(shell awk -F, 'END {print$$2}'$(setting_csv))
sample: pcie_control/build/pcie_control config/setting.csv
	mkdir -p $(datadir)
	sudo pcie_control/build/pcie_control $(filenum) $(datadir)
