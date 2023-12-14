[![GitHub last commit](https://img.shields.io/github/last-commit/tapparelj/gr-lora_sdr)](https://img.shields.io/github/last-commit/tapparelj/gr-lora_sdr)
![gnuradio](https://img.shields.io/badge/GNU%20Radio-3.10.6-important)
![version](https://img.shields.io/badge/Version-0.5.7-brightgreen)
[![arXiv](https://img.shields.io/badge/arXiv-2002.08208-<COLOR>.svg)](https://arxiv.org/abs/2002.08208)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Ftapparelj%2Fgr-lora_sdr&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
[![Build conda package](https://github.com/tapparelj/gr-lora_sdr/actions/workflows/conda-build.yml/badge.svg)](https://github.com/tapparelj/gr-lora_sdr/actions/workflows/conda-build.yml)
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

- Sending and receiving LoRa packets between USRP-USRP and USRP-commercial LoRa transceiver (tested with RFM95, SX1276, SX1262).

- Parameters available:
	- Spreading factors: 5-12*
	- Coding rates: 0-4
	- Implicit and explicit header mode
	- Payload length: 1-255 bytes
	- Sync word selection (network ID)
	- Verification of payload CRC
	- Verification of explicit header checksum
	- Low datarate optimisation mode 
	- Utilisation of soft-decision decoding for improved performances

\* Spreading factors 5 and 6 are not compatible with SX126x.
## Reference
J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming and A. Burg, "An Open-Source LoRa Physical Layer Prototype on GNU Radio," 2020 IEEE 21st International Workshop on Signal Processing Advances in Wireless Communications (SPAWC), Atlanta, GA, USA, 2020, pp. 1-5.

[IEEE Xplore link](https://ieeexplore.ieee.org/document/9154273), [arXiv link](https://arxiv.org/abs/2002.08208)

If you find this implementation useful for your project, please consider citing the aforementioned paper.

## Prerequisites
- Gnuradio 3.10
- python 3
- cmake
- libvolk
- boost
- UHD
- gcc > 9.3.0
- gxx
- pybind11

The conda environment used to develop this module is described by the environment.yml file. 
## Installation
The out of tree module gr-lora_sdr can be installed from source or directly as a conda package.
### From source
- Clone this repository
	```sh
	git clone https://github.com/tapparelj/gr-lora_sdr.git
	```
- Go to the cloned repository
	```sh
	cd gr-lora_sdr/
	```
- A functioning environment with all dependencies can be installed with conda or you can install them individually and skip to the next step.
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
- You can test that the installation is successful by running
  ```sh
  make test
  ```
- Now you should be able to run some codes. For example, open the GNU Radio Companion user interface and check if the blocks of gr-lora_sdr are available on the blocks list (e.g. under LoRa_TX).
	```sh
	gnuradio-companion &
	```
- A final verification of the transceiver functioning can be made by executing the following script, transmitting a frame every two seconds:
	```sh
	python3 examples/tx_rx_functionality_check.py 
	```

#### Usage
- An example of a LoRa transmitter and receiver can be found in gr-lora_sdr/examples/ (both python and grc).
- The .grc files can be opened with gnuradio-companion to set the different transmission parameters.
- The python file generated by grc can be executed with ``` python3 ./{file_name}.py```

### From conda
Thanks to Ryan Volz this OOT module can also directly be installed as a Conda package. Note that gnuradio will also be installed in the conda environment.

- Create or activate the conda environment you want to install this module in. Refer to the conda [getting start guide](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) if you are not familiar with it already.
- Install the module from the anaconda channel [tapparelj](https://anaconda.org/tapparelj/gnuradio-lora_sdr) with:
	```sh
	conda install -c tapparelj -c conda-forge gnuradio-lora_sdr
	```
- Depending on your needs you might want to install complementary packages for gnuradio with:
	```sh
	conda install -c conda-forge gnuradio
	```
- The gnuradio metapackage installs all of the following subpackages: 
	- `gnuradio-grc`
	- `gnuradio-iio`
	- `gnuradio-qtgui`
	- `gnuradio-soapy`
	- `gnuradio-uhd`
	- `gnuradio-video-sdl`
	- `gnuradio-zeromq`
- If you don't want all of those and their dependencies, you can install the ones you'd like individually with: 
	```sh
	conda install -c conda-forge gnuradio-uhd
	```
#### Usage
- Example gnuradio-companinon flowgraphs are installed with the package and can be found in:
	- (Linux/macOS) `$CONDA_PREFIX/share/gr-lora_sdr/examples`
	- (Windows) `%CONDA_PREFIX%\Library\share\gr-lora_sdr\examples`

   
## Frequent issues:  
- Fail to `make` after pulling a new version from git
	- If the parameters of a block have changed in the new version, you need to first clean the old installation before building the module again.
	- from within the build folder, run 
		```
		(sudo) make uninstall
		make clean
		make -j4
		(sudo) make install
		```
- "ImportError: No module named lora_sdr":
	- This issue comes probably from missing PYTHONPATH and LD_LIBRARY_PATH                             
	- Refer to https://wiki.gnuradio.org/index.php/ModuleNotFoundError to modify those variables. If you set a prefix during the "cmake" call, skip directly to point C.(Verifying that the paths exist in your folders might help.)
- The OOT blocks doesn't appear in gnuradio-companion:	
	- The new blocks can be loaded in gnuradio-companion by adding the following lines in home/{username}/.gnuradio/config.conf (If this file doesn't exist you need to create it):
		```
		[grc]
		local_blocks_path=path_to_the_downloaded_folder/gr-lora_sdr/grc
## Changelog
- Add optional print of received payload as hex values
- Added tagged stream input support (for frame definition of frame length)
- Fixed LLR stream format between _fft\_demod_ and _deinterleaver_ 
- added tags to crc verification output stream indication frame start, length and CRC result.
- added separator option for file input
- added preamble length option
- added parameter for frame zero-padding
- add low datarate optimisation support
- add support of spreading factors smaller than 7

 	<font size="10"> [...](./Changelog.md)</font>

## Credit
This work was inspired from [https://github.com/rpp0/gr-lora](https://github.com/rpp0/gr-lora) by Pieter Robyns, Peter Quax, Wim Lamotte and William Thenaers. Which architecture and functionalities have been improved to better emulate the physical layer of LoRa. 

## Licence
Distributed under the GPL-3.0 License License. See LICENSE for more information.
