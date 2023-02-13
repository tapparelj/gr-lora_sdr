[![GitHub last commit](https://img.shields.io/github/last-commit/tapparelj/gr-lora_sdr)](https://img.shields.io/github/last-commit/tapparelj/gr-lora_sdr)
![gnuradio](https://img.shields.io/badge/GNU%20Radio-3.10.3-important)
![version](https://img.shields.io/badge/Version-0.5.4-brightgreen)
[![arXiv](https://img.shields.io/badge/arXiv-2002.08208-<COLOR>.svg)](https://arxiv.org/abs/2002.08208)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Ftapparelj%2Fgr-lora_sdr&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) 

## Summary
This is the fully-functional GNU Radio software-defined radio (SDR) implementation of a LoRa transceiver with all the necessary receiver components to operate correctly even at very low SNRs. The transceiver is available as a module for GNU Radio 3.10. This work has been conducted at the Telecommunication Circuits Laboratory, EPFL. 

In the GNU Radio implementation of the LoRa Tx and Rx chains the user can choose all the parameters of the transmission, such as the spreading factor, the coding rate, the bandwidth, the sync word, the presence of an explicit header and CRC.

- The module contains convenient hierarchical blocks for both Tx and Rx.
<p float="center">
  <img src="https://user-images.githubusercontent.com/66671413/182565519-e1ad1455-ac44-4aca-b339-00c1f3ba54aa.png" height="120" />
  
  <img src="https://user-images.githubusercontent.com/66671413/182562660-ea7c42fc-da74-4ebb-a269-d8ab944468f6.png" height="120" /> 
</p>

-   In the Tx chain, the implementation contains all the main blocks of the LoRa transceiver: the header- and the CRC-insertion blocks, the whitening block, the Hamming encoder block, the interleaver block, the Gray demapping block, and the modulation block.
![tx_flow](https://user-images.githubusercontent.com/66671413/184139150-a14a0417-7098-46ea-b6ad-ca8ba6709904.png)

-   On the receiver side there is the packet synchronization block, which performs all the necessary tasks needed for the synchronization, such as the necessary STO and CFO estimation and correction. The demodulation block follows, along with the Gray mapping block, the deinterleaving block, the Hamming decoder block and the dewhitening block, as well as a CRC verification block.
![rx_flow](https://user-images.githubusercontent.com/66671413/184138776-2e41efc0-78b4-434b-8958-3bed2443cbc4.png)

-   The implementation can be used for fully end-to-end experimental performance results of a LoRa SDR receiver at low SNRs.
-	A simple simulation framework is available in the apps/simulation folder.



## Functionalities

- Sending and receiving LoRa packets between USRP-USRP and USRP-commercial LoRa transceiver (tested for Adafruit Feather 32u4 RFM95 and dragino LoRa/GPS HAT).

- Parameters available:
	- Spreading factors: 5-12
	- Coding rates: 0-4
	- Implicit and explicit header mode
	- Payload length: 1-255 bytes
	- Sync word selection (network ID)
	- Verification of payload CRC
	- Verification of explicit header checksum
	- Low datarate optimisation mode 
	- Utilisation of soft-decision decoding for improved performances

## Reference
J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, and A. Burg, “An Open-Source LoRa Physical Layer Prototype on GNU Radio”

[https://arxiv.org/abs/2002.08208](https://arxiv.org/abs/2002.08208)

If you find this implementation useful for your project, please consider citing the aforementioned paper.

## Prerequisites
- Gnuradio 3.10
- python 3
- cmake
- libvolk
- Boost
- UHD
- gcc > 9.3.0
- gxx
- pybind11

The conda environment used to develop this module is described by the environment.yml file. 
## Installation
- Clone this repository
	```sh
	git clone https://github.com/tapparelj/gr-lora_sdr.git
	```
- Go to the cloned repository
	```sh
	cd gr-lora_sdr/
	```
- A functionning environment with all dependencies can be installed with conda.
	You can follow this [tutorial](https://www.how2shout.com/how-to/install-anaconda-wsl-windows-10-ubuntu-linux-app.html) or simply following:
	- First download the latest release of conda, for example:
		```sh
		wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh
		```
	- Now run the downloaded file which is the Anaconda Installer script
		```sh
	 	bash Miniconda3-py39_4.12.0-Linux-x86_64.sh
		```
	- And reload the Shell
		```sh
		source ~/.bashrc
		```
	- Now copy our environment to install all the dependencies of the module automatically. Note that it will take quite some time (~20 min).
		```sh
		conda env create -f environment.yml 
		```
	- Start the conda environment GNU Radio 3.10 you just created
		```sh
		conda activate gr310
		```
- To build the code, create an appropriate folder and go in it:
	```sh
	mkdir build
	cd build
	```
- Run the main CMakeLists.txt
	```sh
	cmake .. -DCMAKE_INSTALL_PREFIX=<your prefix> # default to usr/local, CONDA_PREFIX or PYBOMB_PREFIX if no install prefix selected here
	```
- Finally compile the custom GNU Radio blocks composing the LoRa transceiver. Replacing \<X> with the number of core you want to use to speed up the compilation.
	```sh
	(sudo) make install -j<X>
	```
- if you installed as sudo run
	```sh
	sudo ldconfig 
	```
- Now you should be able to run some codes. For example, open the GNU Radio Companion user interface and check if the blocks of gr-lora_sdr are available on the blocks list (e.g. under LoRa_TX).
	```sh
	gnuradio-companion &
	```
- A final verification of the transceiver functionning can be made by executing the following script, transmitting a frame every two seconds:
	```sh
	python3 examples/tx_rx_functionnality_check.py 
	```

## Usage
- An example of a LoRa transmitter and receiver can be found in gr-lora_sdr/examples/ (both python and grc).
- The .grc files can be opened with gnuradio-companion to set the different transmission parameters.
- The python file generated by grc can be executed with ``` python3 ./{file_name}.py```

    
## Frequent issues:  
- "ImportError: No module named lora_sdr":
	- This issue comes probably from missing PYTHONPATH and LD_LIBRARY_PATH                             
	- Refer to https://wiki.gnuradio.org/index.php/ModuleNotFoundError to modify those variables. If you set a prefix during the "cmake" call, skip directly to point C.(Verifying that the paths exist in your folders might help.)
- The OOT blocks doesn't appear in gnuradio-companion:	
	- The new blocks can be loaded in gnuradio-companion by adding the following lines in home/{username}/.gnuradio/config.conf (If this file doesn't exist you need to create it):
		```
		[grc]
		local_blocks_path=path_to_the_downloaded_folder/gr-lora_sdr/grc
## Changelog
- added separator option for file input
- added preamble length option
- added parameter for frame zero-padding
- add low datarate optimisation support

- add support of spreading factors smaller than 7

- add sampling frequency offset estimation and compensation
    - Estimation leverages the relation between CFO and SFO, both caused by the same reference clock
    - The compensation method consists in a two step refinement of the estimates in the preamble and a puncturing/insertion of samples during the payload

- Add frame error rate simulation script in apps/simulation

 	<font size="10"> [...](./Changelog.md)</font>

## Credit
This work was inspired from [https://github.com/rpp0/gr-lora](https://github.com/rpp0/gr-lora) by Pieter Robyns, Peter Quax, Wim Lamotte and William Thenaers. Which architecture and functionalities have been improved to better emulate the physical layer of LoRa. 

## Licence
Distributed under the GPL-3.0 License License. See LICENSE for more information.




	














