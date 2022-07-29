/*
 * Copyright 2020 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include <pybind11/pybind11.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

namespace py = pybind11;

// Headers for binding functions
/**************************************/
// The following comment block is used for
// gr_modtool to insert function prototypes
// Please do not delete
/**************************************/
// BINDING_FUNCTION_PROTOTYPES(
void bind_add_crc(py::module& m);
void bind_crc_verif(py::module& m);
void bind_data_source(py::module& m);
void bind_deinterleaver(py::module& m);
void bind_dewhitening(py::module& m);
void bind_fft_demod(py::module& m);
void bind_frame_sync(py::module& m);
void bind_gray_demap(py::module& m);
void bind_gray_mapping(py::module& m);
void bind_hamming_dec(py::module& m);
void bind_hamming_enc(py::module& m);
void bind_header_decoder(py::module& m);
void bind_header(py::module& m);
void bind_interleaver(py::module& m);
void bind_modulate(py::module& m);
void bind_payload_id_inc(py::module& m);
void bind_RH_RF95_header(py::module& m);
void bind_utilities(py::module& m);
void bind_whitening(py::module& m);
// ) END BINDING_FUNCTION_PROTOTYPES


// We need this hack because import_array() returns NULL
// for newer Python versions.
// This function is also necessary because it ensures access to the C API
// and removes a warning.
void* init_numpy()
{
    import_array();
    return NULL;
}

PYBIND11_MODULE(lora_sdr_python, m)
{
    // Initialize the numpy C API
    // (otherwise we will see segmentation faults)
    init_numpy();

    // Allow access to base block methods
    py::module::import("gnuradio.gr");

    /**************************************/
    // The following comment block is used for
    // gr_modtool to insert binding function calls
    // Please do not delete
    /**************************************/
    // BINDING_FUNCTION_CALLS(
    bind_add_crc(m);
    bind_crc_verif(m);
    bind_data_source(m);
    bind_deinterleaver(m);
    bind_dewhitening(m);
    bind_fft_demod(m);
    bind_frame_sync(m);
    bind_gray_demap(m);
    bind_gray_mapping(m);
    bind_hamming_dec(m);
    bind_hamming_enc(m);
    bind_header_decoder(m);
    bind_header(m);
    bind_interleaver(m);
    bind_modulate(m);
    bind_payload_id_inc(m);
    bind_RH_RF95_header(m);
    bind_utilities(m);
    bind_whitening(m);
    // ) END BINDING_FUNCTION_CALLS
}
