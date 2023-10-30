#ifndef TX_RX_SIMULATION_HPP
#define TX_RX_SIMULATION_HPP
/********************
GNU Radio C++ Flow Graph Header File

Title: Tx Rx Simulation
Author: Tapparel Joachim@EPFL,TCL
GNU Radio version: 3.10.3.0
********************/

/********************
** Create includes
********************/
#include <gnuradio/top_block.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/blocks/throttle.h>
#include "gnuradio/lora_sdr/add_crc.h"
#include "gnuradio/lora_sdr/crc_verif.h"
#include "gnuradio/lora_sdr/deinterleaver.h"
#include "dewhitening.h"
#include "gnuradio/lora_sdr/fft_demod.h"
#include "gnuradio/lora_sdr/frame_sync.h"
#include "gnuradio/lora_sdr/gray_demap.h"
#include "gnuradio/lora_sdr/gray_mapping.h"
#include "gnuradio/lora_sdr/hamming_dec.h"
#include "gnuradio/lora_sdr/hamming_enc.h"
#include "gnuradio/lora_sdr/header.h"
#include "gnuradio/lora_sdr/header_decoder.h"
#include "gnuradio/lora_sdr/interleaver.h"
#include "gnuradio/lora_sdr/modulate.h"
#include "gnuradio/lora_sdr/whitening.h"



using namespace gr;



class tx_rx_simulation {

private:


    lora_sdr::whitening::sptr lora_sdr_whitening_0;
    lora_sdr::modulate::sptr lora_sdr_modulate_0;
    lora_sdr::interleaver::sptr lora_sdr_interleaver_0;
    lora_sdr::header_decoder::sptr lora_sdr_header_decoder_0;
    lora_sdr::header::sptr lora_sdr_header_0;
    lora_sdr::hamming_enc::sptr lora_sdr_hamming_enc_0;
    lora_sdr::hamming_dec::sptr lora_sdr_hamming_dec_0;
    lora_sdr::gray_mapping::sptr lora_sdr_gray_mapping_0;
    lora_sdr::gray_demap::sptr lora_sdr_gray_demap_0;
    lora_sdr::frame_sync::sptr lora_sdr_frame_sync_0;
    lora_sdr::fft_demod::sptr lora_sdr_fft_demod_0;
    lora_sdr::dewhitening::sptr lora_sdr_dewhitening_0;
    lora_sdr::deinterleaver::sptr lora_sdr_deinterleaver_0;
    lora_sdr::crc_verif::sptr lora_sdr_crc_verif_0;
    lora_sdr::add_crc::sptr lora_sdr_add_crc_0;
    blocks::throttle::sptr blocks_throttle_0;
    blocks::file_source::sptr blocks_file_source_0_0;


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
    tx_rx_simulation();
    ~tx_rx_simulation();

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

