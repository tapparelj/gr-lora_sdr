File description:

setpaths.sh: script that add the library and python paths for the current shell process. It might have to be adapted accordingly to your installation locations.

-two_users folder:
	-Flowgraphs:
		- mu_tx_rx_simulation: flowgraph containing two transmitters and a receiver connected in software only. It can be useful to check the installation of the module gr-lora_sdr.
	
		- mu_tx_rx: flowgraph containing two transmitters and a receiver. It requires 3 USRPS, with the two transmitter linked with a MIMO cable for clock synchronization.
	
	- Usage:
		- In gnuradio-companion(GRC) adapt the measurement_folder variable to set location where the results will be saved
		- Set the parameters you are interested in such as STO, CFO, Power (note that only power[1]>power[0] is supported by the current user detection)
		- Generate the python script in GRC and run it in a terminal using ./mu_tx_rx(_simulation)
		- An example of a matlab script retriving symbol errors is available in gr-lora_sdr/matlab
	- Tips:
		- A description of each block can be found in gnuradio-companion under the documentation tab.
		- If underflow appears when using radios, you need to adapt the spreading factor, the oversampling factor or the interframe delay to match the performances of your system.
		

-single_user folder:
	-tx_rx_simulation: flowgraph connecting a receiver and a transmitter in software only, avoiding radio usage. It can be useful to check the installation of the module gr-lora_sdr. 

	-lora_RX: an example of receiver 

	-lora_TX: an example of transmitter

	-tx_rx: flowgraph containing both tx and rx. In this example we use a mimo cable to link the two USRP. 

	-measurements_example: example of modification of tx_rx.py that sweep the Tx power. If you want to save the frame errors as well as the received power and the synchronization informations, you have to define "GRLORA_MEASUREMENTS" in err_measures_impl.h, fft_demod_impl.h and frame_sync_impl.h.

	If you get the warning: USRP Source Block caught rx error code: 2 when not sharing the local oscillator, you need to switch the clock source and time source to 'mimo' run one time and switch back to 'internal' and 'none'. 


	
	



