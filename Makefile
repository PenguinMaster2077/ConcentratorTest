.PHONY: all
setting_csv:=config/setting.csv
runno=$(shell awk -F, 'END {print$$1}' $(setting_csv))
filenum=$(shell awk -F, 'END {print$$2}' $(setting_csv))
filenum_list=$(shell seq 0 $$(($(filenum)-1)))
N_wave:=1000
N_ch:=2

datadir=data/$(runno)

mock_sample: config/setting.csv
	echo "RUNO:$(runno); data directory: $(datadir); filenum: $(filenum)"

sample: pcie_control/build/pcie_control config/setting.csv
	mkdir -p $(datadir)
	sudo pcie_control/build/pcie_control $(filenum) $(datadir)

preview: $(datadir)/preview.pdf $(filenum_list:%=$(datadir)/%.pdf)
$(datadir)/preview.pdf: $(filenum_list:%=$(datadir)/%.h5)
	python3 converter/preview.py -i $^ -o $@
$(datadir)/%.h5: $(datadir)/%.bin
	python3 converter/converter.py -i $^ -o $@ -N_ch $(N_ch) -N $(N_wave)
$(datadir)/%.pdf: $(datadir)/%.h5
	python3 converter/preview.py -i $^ -o $@ -N 100 --onlywave

