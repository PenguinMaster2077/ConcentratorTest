.PHONY: all
setting_csv:=config/setting.csv
runno=$(shell awk -F, 'END {print$$1}' $(setting_csv))
filenum=$(shell awk -F, 'END {print$$2}' $(setting_csv))

datadir=data/$(runno)/

mock_sample: config/setting.csv
	echo "RUNO:$(runno); data directory: $(datadir); filenum: $(filenum)"

sample: pcie_control/build/pcie_control config/setting.csv
	mkdir -p $(datadir)
	sudo pcie_control/build/pcie_control $(filenum) $(datadir)
