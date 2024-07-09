/*
 * Copyright 2024 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

/***********************************************************************************/
/* This file is automatically generated using bindtool and can be manually
 * edited  */
/* The following lines can be configured to regenerate this file during cmake */
/* If manual edits are made, the following tags should be modified accordingly.
 */
/* BINDTOOL_GEN_AUTOMATIC(0) */
/* BINDTOOL_USE_PYGCCXML(0) */
/* BINDTOOL_HEADER_FILE(modulate.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(2f4e1101c5eabd18418839d5e0ac6b19) */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/lora_sdr/modulate.h>
// pydoc.h is automatically generated in the build directory
#include <modulate_pydoc.h>

void bind_modulate(py::module &m) {

  using modulate = ::gr::lora_sdr::modulate;

  py::class_<modulate, gr::block, gr::basic_block, std::shared_ptr<modulate>>(
      m, "modulate", D(modulate))

      .def(py::init(&modulate::make), py::arg("sf"), py::arg("samp_rate"),
           py::arg("bw"), py::arg("sync_words"), py::arg("inter_frame_padd"),
           py::arg("preamble_len"), D(modulate, make))

      ;
}
