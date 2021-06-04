# GNU Radio C++ Flow Graph CMakeLists.txt
#
# Title: cpp_debug
# GNU Radio version: 3.8.2.0


cmake_minimum_required(VERSION 3.8)


include_directories(
    ${GNURADIO_ALL_INCLUDE_DIRS}
    ${Boost_INCLUDE_DIRS}
    $ENV{HOME}/.grc_gnuradio
)




set(GR_LIBRARIES
    boost_system
    gnuradio-blocks
    gnuradio-runtime
    gnuradio-pmt
    log4cpp
    gnuradio-lora_sdr
    gnuradio-filter
)

add_executable(zmq_test zmq_test.cpp)
target_link_libraries(zmq_test ${GR_LIBRARIES})
