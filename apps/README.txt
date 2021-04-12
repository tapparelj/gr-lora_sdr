File description:

-single_user folder:
	-tx_rx_simulation: flowgraph connecting a receiver and a transmitter in software only, avoiding radio usage. It can be useful to check the installation of the module gr-lora_sdr. 

	-lora_RX: an example of receiver 

	-lora_TX: an example of transmitter

	-tx_rx: flowgraph containing both tx and rx.

	
	If you get the warning: USRP Source Block caught rx error code: 2 when not sharing the local oscillator, you need to switch the clock source and time source to 'mimo' run one time and switch back to 'internal' and 'none'. 


	
	



