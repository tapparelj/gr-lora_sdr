File description:
lora_RX: an example of receiver 

lora_TX: an example of transmitter

tx_rx: flowgraph containing both tx and rx. In this example we use a mimo cable to link the two USRP. 

measurements_example: example of modification of tx_rx.py that sweep the Tx power. If you want to save the frame errors as well as the received power and the synchronization informations, you have to define "GRLORA_MEASUREMENTS" in err_measures_impl.h, fft_demod_impl.h and frame_sync_impl.h.

If you get the warning: USRP Source Block caught rx error code: 2 when not sharing the local oscillator, just switch the clock source and time source to 'mimo' run one time and switch back to 'internal' and 'none'. 

setpaths.sh: script that add the library and python paths for the current shell process. It might have to be changed accordingly to your installation locations.

