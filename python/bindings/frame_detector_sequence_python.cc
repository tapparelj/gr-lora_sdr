/*
 * Copyright 2022 Free Software Foundation, Inc.
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
/* BINDTOOL_HEADER_FILE(frame_detector_sequence.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(48c911e35cb412c7dd650dae78940dc0)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <lora_sdr/frame_detector_sequence.h>
// pydoc.h is automatically generated in the build directory
#include <frame_detector_sequence_pydoc.h>

void bind_frame_detector_sequence(py::module& m)
{

    using frame_detector_sequence    = ::gr::lora_sdr::frame_detector_sequence;


    py::class_<frame_detector_sequence, gr::block, gr::basic_block,
        std::shared_ptr<frame_detector_sequence>>(m, "frame_detector_sequence", D(frame_detector_sequence))

        .def(py::init(&frame_detector_sequence::make),
           py::arg("sf"),
           py::arg("samp_rate"),
           py::arg("bw"),
           py::arg("n_seq"),
           D(frame_detector_sequence,make)
        )
        



        ;




}








