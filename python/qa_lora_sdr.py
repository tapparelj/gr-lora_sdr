#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 "Martyn van Dijke".
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import pmt
import lora_sdr_swig as lora_sdr
from gnuradio import filter


class qa_lora_sdr(gr_unittest.TestCase):
    """Main class of unit test cases for the entire lora sdr

    Args:
        gr_unittest ([type]): [description]
    """

    def setUp(self):
        """Setup for testing
        """


if __name__ == '__main__':
    gr_unittest.run(qa_lora_sdr)
