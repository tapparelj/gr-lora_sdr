#!/bin/bash
# Script to redo all python bindings in case there is a version mismatch

gr_modtool bind add_crc
gr_modtool bind crc_verif
gr_modtool bind data_source
gr_modtool bind deinterleaver
gr_modtool bind dewhitening
gr_modtool bind fft_demod
gr_modtool bind frame_sync
gr_modtool bind gray_demap
gr_modtool bind gray_mapping
gr_modtool bind hamming_dec
gr_modtool bind hamming_enc
gr_modtool bind header_decoder
gr_modtool bind header
gr_modtool bind interleaver
gr_modtool bind modulate
gr_modtool bind payload_id_inc
gr_modtool bind RH_RF95_header
gr_modtool bind utilities
gr_modtool bind whitening

