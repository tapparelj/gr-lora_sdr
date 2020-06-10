# Copyright 2011,2012,2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})
list(APPEND lora_sdr_sources
    add_crc_impl.cc
    crc_verif_impl.cc
    dewhitening_impl.cc
    gray_decode_impl.cc
    gray_enc_impl.cc
    hamming_dec_impl.cc
    hamming_enc_impl.cc
    header_decoder_impl.cc
    header_impl.cc
    interleaver_impl.cc
    modulate_impl.cc
    whitening_impl.cc
    kiss_fft.c
    RH_RF95_header_impl.cc
    fft_demod_impl.cc
    data_source_impl.cc
    frame_sync_impl.cc
    deinterleaver_impl.cc
    err_measures_impl.cc )

set(lora_sdr_sources "${lora_sdr_sources}" PARENT_SCOPE)
if(NOT lora_sdr_sources)
	MESSAGE(STATUS "No C++ sources... skipping lib/")
	return()
endif(NOT lora_sdr_sources)

add_library(gnuradio-lora_sdr SHARED ${lora_sdr_sources})
target_link_libraries(gnuradio-lora_sdr ${Boost_LIBRARIES} ${GNURADIO_ALL_LIBRARIES})
set_target_properties(gnuradio-lora_sdr PROPERTIES DEFINE_SYMBOL "gnuradio_lora_sdr_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-lora_sdr PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
include(GrMiscUtils)
GR_LIBRARY_FOO(gnuradio-lora_sdr RUNTIME_COMPONENT "lora_sdr_runtime" DEVEL_COMPONENT "lora_sdr_devel")

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_lora_sdr_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_lora_sdr.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_lora_sdr.cc
)

add_executable(test-lora_sdr ${test_lora_sdr_sources})

target_link_libraries(
  test-lora_sdr
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-lora_sdr
)

GR_ADD_TEST(test_lora_sdr test-lora_sdr)

########################################################################
# Print summary
########################################################################
message(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Building for version: ${VERSION} / ${LIBVER}")

