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
/* BINDTOOL_HEADER_FILE(hier_tx.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(45b8c081126999cf30dbc6c2d82d61e5)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <lora_sdr/hier_tx.h>
// pydoc.h is automatically generated in the build directory
#include <hier_tx_pydoc.h>

void bind_hier_tx(py::module& m)
{

    using hier_tx    = gr::lora_sdr::hier_tx;


    py::class_<hier_tx,gr::hier_block2,
        std::shared_ptr<hier_tx>>(m, "hier_tx", D(hier_tx))

        .def(py::init(&hier_tx::make),
           py::arg("pay_len"),
           py::arg("n_frames"),
           py::arg("src_data"),
           py::arg("cr"),
           py::arg("sf"),
           py::arg("impl_head"),
           py::arg("has_crc"),
           py::arg("samp_rate"),
           py::arg("bw"),
           py::arg("mean"),
           py::arg("sync_words"),
           py::arg("create_zeros"),
           D(hier_tx,make)
        )
        



        ;




}








