# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT lora_sdr_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT lora_sdr_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND lora_sdr_python_files
    python_bindings.cc
    add_crc_python.cc
    err_measures_python.cc
    fft_demod_python.cc
    frame_detector_sequence_python.cc
    frame_detector_threshold_python.cc
    frame_detector_timeout_python.cc
    frame_src_python.cc
    frame_sync_python.cc
    gray_decode_python.cc
    gray_enc_python.cc
    hamming_dec_python.cc
    hamming_enc_python.cc
    header_decoder_python.cc
    header_python.cc
    header_utils.py
    hier_rx_python.cc
    hier_tx_python.cc
    interleaver_python.cc
    modulate_python.cc
    mu_detection_python.cc
    mu_synchro_python.cc
    noise_est_python.cc
    partial_ml_python.cc
    python_bindings.cc
    README.md
    RH_RF95_header_python.cc
    signal_detector_python.cc
    whitening_python.cc
    crc_verif_python.cc
    data_source_python.cc
    data_source_sim_python.cc
    deinterleaver_python.cc
    dewhitening_python.cc
)

GR_PYBIND_MAKE_OOT(lora_sdr 
   ../..
   gr::lora_sdr
   "${lora_sdr_python_files}")

install(TARGETS lora_sdr_python DESTINATION ${GR_PYTHON_DIR}/lora_sdr COMPONENT pythonapi)
