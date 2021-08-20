/*
 * Copyright 2021 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

/***********************************************************************************/
/* This file is automatically generated using bindtool and can be manually edited  */
/* The following lines can be configured to regenerate this file during cmake      */
/* If manual edits are made, the following tags should be modified accordingly.    */
/* BINDTOOL_GEN_AUTOMATIC(0)                                                       */
/* BINDTOOL_USE_PYGCCXML(0)                                                        */
/* BINDTOOL_HEADER_FILE(fft_demod.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(3ec15c9040cb3fce1af39d713b978fd5)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <lora_sdr/fft_demod.h>
// pydoc.h is automatically generated in the build directory
#include <fft_demod_pydoc.h>

void bind_fft_demod(py::module& m)
{

    using fft_demod    = gr::lora_sdr::fft_demod;


    py::class_<fft_demod,
        std::shared_ptr<fft_demod>>(m, "fft_demod", D(fft_demod))

        .def(py::init(&fft_demod::make),
           py::arg("samp_rate"),
           py::arg("bandwidth"),
           py::arg("sf"),
           py::arg("impl_head"),
           D(fft_demod,make)
        )
        



        ;




}







