#bin/bash
echo 'Patching FIR filter to also output cpp'
sudo cp filter_interp_fir_filter_xxx.block.yml /usr/share/gnuradio/grc/blocks/filter_interp_fir_filter_xxx.block.yml
echo "Please reload blocks in gnuradio companion"