# Copyright 2011 Free Software Foundation, Inc.
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
install(FILES
    lora_sdr_add_crc.xml
    lora_sdr_crc_verif.xml
    lora_sdr_dewhitening.xml
    lora_sdr_gray_decode.xml
    lora_sdr_gray_enc.xml
    lora_sdr_hamming_dec.xml
    lora_sdr_hamming_enc.xml
    lora_sdr_header_decoder.xml
    lora_sdr_header.xml
    lora_sdr_interleaver.xml
    lora_sdr_modulate.xml
    lora_sdr_whitening.xml
    lora_sdr_RH_RF95_header.xml
    lora_sdr_fft_demod.xml
    lora_sdr_data_source.xml
    lora_sdr_frame_sync.xml
    lora_sdr_deinterleaver.xml
    lora_sdr_err_measures.xml DESTINATION share/gnuradio/grc/blocks
)
