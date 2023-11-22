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
#include <gnuradio/blocks/vector_sink.h>
#include "gnuradio/lora_sdr/whitening.h"



using namespace gr;



class tx_rx_simulation {

private:


    lora_sdr::whitening::sptr lora_sdr_whitening_0;
    blocks::vector_sink_b::sptr blocks_vector_sink_x_0;
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

