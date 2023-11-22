# GNU Radio C++ Flow Graph CMakeLists.txt
#
# Title: Tx Rx Simulation
# Author: Tapparel Joachim@EPFL,TCL
# GNU Radio version: 3.10.3.0


cmake_minimum_required(VERSION 3.8)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")

project(tx_rx_simulation)

find_package(Gnuradio "3.10" COMPONENTS
    blocks
    fec
    fft
    filter
    analog
    digital
    dtv
    audio
    channels
    pdu
    iio
    qtgui
    trellis
    uhd
    uhd UHD 4.0 RFNoC
    video-sdl
    vocoder
    wavelet
    zeromq
    network
    soapy
)


include_directories(/home/yujwu/conda/envs/gr310/include/gnuradio/lora_sdr)

add_executable(tx_rx_simulation tx_rx_simulation.cpp)
target_link_libraries(tx_rx_simulation
    gnuradio::gnuradio-blocks
    /home/yujwu/Documents/gr-lora_sdr/build/lib/libgnuradio-lora_sdr.so

)

