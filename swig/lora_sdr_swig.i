/* -*- c++ -*- */

#define LORA_SDR_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "lora_sdr_swig_doc.i"

%{
#include "lora_sdr/add_crc.h"
#include "lora_sdr/crc_verif.h"
#include "lora_sdr/dewhitening.h"
#include "lora_sdr/gray_decode.h"
#include "lora_sdr/gray_enc.h"
#include "lora_sdr/hamming_dec.h"
#include "lora_sdr/hamming_enc.h"
#include "lora_sdr/header_decoder.h"
#include "lora_sdr/header.h"
#include "lora_sdr/interleaver.h"
#include "lora_sdr/modulate.h"
#include "lora_sdr/whitening.h"
#include "lora_sdr/RH_RF95_header.h"
#include "lora_sdr/fft_demod.h"
#include "lora_sdr/data_source.h"
#include "lora_sdr/frame_sync.h"
#include "lora_sdr/deinterleaver.h"
#include "lora_sdr/err_measures.h"
%}


%include "lora_sdr/add_crc.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, add_crc);
%include "lora_sdr/crc_verif.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, crc_verif);

%include "lora_sdr/dewhitening.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, dewhitening);

%include "lora_sdr/gray_decode.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, gray_decode);
%include "lora_sdr/gray_enc.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, gray_enc);
%include "lora_sdr/hamming_dec.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, hamming_dec);
%include "lora_sdr/hamming_enc.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, hamming_enc);
%include "lora_sdr/header_decoder.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, header_decoder);
%include "lora_sdr/header.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, header);
%include "lora_sdr/interleaver.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, interleaver);
%include "lora_sdr/modulate.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, modulate);

%include "lora_sdr/whitening.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, whitening);
%include "lora_sdr/RH_RF95_header.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, RH_RF95_header);


%include "lora_sdr/fft_demod.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, fft_demod);
%include "lora_sdr/data_source.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, data_source);
%include "lora_sdr/frame_sync.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, frame_sync);

%include "lora_sdr/deinterleaver.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, deinterleaver);
%include "lora_sdr/err_measures.h"
GR_SWIG_BLOCK_MAGIC2(lora_sdr, err_measures);
