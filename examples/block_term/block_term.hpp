#ifndef BLOCK_TERM_HPP
#define BLOCK_TERM_HPP
/********************
GNU Radio C++ Flow Graph Header File

Title: Block Term
Author: Tapparel Joachim@EPFL,TCL
GNU Radio version: 3.10.3.0
********************/

/********************
** Create includes
********************/
#include <gnuradio/top_block.h>
#include <gnuradio/analog/noise_source.h>
#include "gnuradio/lora_sdr/crc_verif.h"
#include "gnuradio/lora_sdr/deinterleaver.h"
#include "dewhitening.h"
#include "gnuradio/lora_sdr/fft_demod.h"
#include "gnuradio/lora_sdr/frame_sync.h"
#include "gnuradio/lora_sdr/gray_mapping.h"
#include "gnuradio/lora_sdr/hamming_dec.h"
#include "gnuradio/lora_sdr/header_decoder.h"



using namespace gr;



class block_term {

private:


    lora_sdr::header_decoder::sptr lora_sdr_header_decoder_0;
    lora_sdr::hamming_dec::sptr lora_sdr_hamming_dec_0;
    lora_sdr::gray_mapping::sptr lora_sdr_gray_mapping_0;
    lora_sdr::frame_sync::sptr lora_sdr_frame_sync_0;
    lora_sdr::fft_demod::sptr lora_sdr_fft_demod_0;
    lora_sdr::dewhitening::sptr lora_sdr_dewhitening_0;
    lora_sdr::deinterleaver::sptr lora_sdr_deinterleaver_0;
    lora_sdr::crc_verif::sptr lora_sdr_crc_verif_0;
    analog::noise_source_c::sptr analog_noise_source_x_0;


// Variables:
    bool soft_decoding = false;
    int sf = 7;
    int samp_rate = 500000;
    int preamb_len = 8;
    int pay_len = 16;
    bool ldro = false;
    bool impl_head = false;
    bool has_crc = true;
    int cr = 2;
    int clk_offset = 0;
    double center_freq = 868.1e6;
    int bw = 125000;
    int SNRdB = -5;

public:
    top_block_sptr tb;
    block_term();
    ~block_term();

    bool get_soft_decoding () const;
    void set_soft_decoding(bool soft_decoding);
    int get_sf () const;
    void set_sf(int sf);
    int get_samp_rate () const;
    void set_samp_rate(int samp_rate);
    int get_preamb_len () const;
    void set_preamb_len(int preamb_len);
    int get_pay_len () const;
    void set_pay_len(int pay_len);
    bool get_ldro () const;
    void set_ldro(bool ldro);
    bool get_impl_head () const;
    void set_impl_head(bool impl_head);
    bool get_has_crc () const;
    void set_has_crc(bool has_crc);
    int get_cr () const;
    void set_cr(int cr);
    int get_clk_offset () const;
    void set_clk_offset(int clk_offset);
    double get_center_freq () const;
    void set_center_freq(double center_freq);
    int get_bw () const;
    void set_bw(int bw);
    int get_SNRdB () const;
    void set_SNRdB(int SNRdB);

};


#endif

