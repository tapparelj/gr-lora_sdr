## Summary
This is the fully-functional GNU Radio software-defined radio (SDR) implementation of a LoRa transceiver with all the necessary receiver components to operate correctly even at very low SNRs.  This work has been conducted at the Telecommunication Circuits Laboratory, EPFL. 

In the GNU Radio implementation of the LoRa Tx and Rx chains the user can choose all the parameters of the transmission, such as the spreading factor, the coding rate, the bandwidth, the presence of a header and a CRC, the message to be transmitted, etc.

-   In the Tx chain, the implementation contains all the main blocks of the LoRa transceiver: the header- and the CRC-insertion blocks, the whitening block, the Hamming encoder block, the interleaver block, the Gray mapping block, and the modulation block.
-   On the receiver side there is the packet synchronization block, which performs all the necessary tasks needed for the synchronization, such as the necessary STO and CFO estimation and correction. The demodulation block follows, along with the Gray demapping block, the deinterleaving block, the Hamming decoder block and the dewhitening block, as well as a CRC block.
-   The implementation can be used for fully end-to-end experimental performance results of a LoRa SDR receiver at low SNRs.

This work was based on [https://github.com/rpp0/gr-lora](https://github.com/rpp0/gr-lora) by Pieter Robyns, Peter Quax, Wim Lamotte and William Thenaers. Which architecture and functionnalities have been improved to better emulate the physical layer of LoRa. 

## Reference

J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming, and A. Burg, “An Open-Source LoRa Physical Layer Prototype on GNU Radio”

[https://arxiv.org/abs/2002.08208](https://arxiv.org/abs/2002.08208)

If you find this implementation useful for your project, please consider citing the aforementioned paper.

## Installation:
-   Download the zip archive and extract it    
- The installation path can be set in CMakeLists.txt under #set destination.(default: home/lora_sdr)
    
- Similarly to any GNU Radio OOT module, it can be build with: (It might require to use sudo depending of the installation destination)  
	- mkdir build  
    - cd build  
    - cmake ../  (-DCMAKE_INSTALL_PREFIX=/usr for Arch Linux)
    - make  
    - sudo make install  

## Usage:    
- An example of a transmitter and a receiver can be found in gr-lora_sdr/app (both python and grc).  
- An example of an automated testing script and the corresponding grc and python file can also be found.

## Requirements:  
    - Gnuradio 3.8
    - python >= 2.7
    - cmake  
    - swig  
    - libvolk  
    - UHD
    - cppunit (optional for unit testing)
    - qwt (optional for gui)
    - doxygen (optional for documentation)
    - log4cpp (optional for logging/debugging)