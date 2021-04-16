title: The LORA_SDR OOT Module
brief: Open source low level reverse engineering of LoRa
tags: # Tags are arbitrary, but look at CGRAN what other authors are using
  - sdr
  - LoRa
  - c-ran
author:
  - Martyn van Dijke <martijnvdijke600@gmail.com>
copyright_owner:
  - Copyright Owner 1
stable_release: master
license: GPL
dependencies:
  - gnuradio (>= 3.8.0)
  - python (>= 3.8)
  - cmake (>= 3.8)
  - swig (>= 4.0)
  - libvolk
  - uhd
  - doxygen
  - log4cpp
gr_supported_version: 3.8.0,3.8.1,3.8.2
repo: https://github.com/martynvdijke/gr-lora_sdr
website: https://martynvdijke.github.io/gr-lora_sdr/html/index.html
icon: https://github.com/martynvdijke/gr-lora_sdr/settings) 
---
This is the fully-functional GNU Radio software-defined radio (SDR) implementation of a LoRa transceiver with all the necessary receiver components to operate correctly even at very low SNRs. This work has been originally conducted at the Telecommunication Circuits Laboratory, EPFL and later the code has been extended at the Technical University of Eindhoven.
The extension of this project is to implement a simulated multi-stream gateway, this is currently implemented in an experimental version.
More information on this extended work is available in this repo.


In the GNU Radio implementation of the LoRa Tx and Rx chains the user can choose all the parameters of the transmission, such as the spreading factor, the coding rate, the bandwidth, the presence of a header and a CRC, the message to be transmitted, etc.

- In the Tx chain, the implementation contains all the main blocks of the LoRa transceiver: the header- and the CRC-insertion blocks, the whitening block, the Hamming encoder block, the interleaver block, the Gray mapping block, and the modulation block.
- On the receiver side there is the packet synchronization block, which performs all the necessary tasks needed for the synchronization, such as the necessary STO and CFO estimation and correction. The demodulation block follows, along with the Gray demapping block, the deinterleaving block, the Hamming decoder block and the dewhitening block, as well as a CRC block.
- The implementation can be used for fully end-to-end experimental performance results of a LoRa SDR receiver at low SNRs.