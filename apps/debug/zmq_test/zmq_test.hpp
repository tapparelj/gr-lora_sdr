#ifndef ZMQ_TEST_HPP
#define ZMQ_TEST_HPP
/********************
GNU Radio C++ Flow Graph Header File

Title: Not titled yet
GNU Radio version: 3.8.2.0
********************/

/********************
** Create includes
********************/
#include <gnuradio/top_block.h>
#include <gnuradio/blocks/null_sink.h>
#include <gnuradio/blocks/tag_debug.h>
#include <gnuradio/blocks/throttle.h>
#include <lora_sdr/add_crc.h>
#include <lora_sdr/data_source_sim.h>
#include <lora_sdr/gray_decode.h>
#include <lora_sdr/hamming_enc.h>
#include <lora_sdr/header.h>
#include <lora_sdr/interleaver.h>
#include <lora_sdr/modulate.h>
#include <lora_sdr/whitening.h>



using namespace gr;



class zmq_test {

private:


    lora_sdr::whitening::sptr lora_sdr_whitening_0_0;
    lora_sdr::modulate::sptr lora_sdr_modulate_0_0;
    lora_sdr::interleaver::sptr lora_sdr_interleaver_0_0;
    lora_sdr::header::sptr lora_sdr_header_0_0;
    lora_sdr::hamming_enc::sptr lora_sdr_hamming_enc_0_0;
    lora_sdr::gray_decode::sptr lora_sdr_gray_decode_0_0;
    lora_sdr::data_source_sim::sptr lora_sdr_data_source_sim_0;
    lora_sdr::add_crc::sptr lora_sdr_add_crc_0_0;
    blocks::throttle::sptr blocks_throttle_0_1;
    blocks::tag_debug::sptr blocks_tag_debug_1_0_0_0_0;
    blocks::null_sink::sptr blocks_null_sink_0;


// Variables:
    int sf = 9;
    int samp_rate = 250000;
    int pay_len = 64;
    int n_frame = 3;
    bool multi_control = true;
    int mean = 200;
    bool impl_head = true;
    bool has_crc = false;
    int frame_period = 200;
    int cr = 4;
    int bw = 250000;

public:
    top_block_sptr tb;
    zmq_test();
    ~zmq_test();

    int get_sf () const;
    void set_sf(int sf);
    int get_samp_rate () const;
    void set_samp_rate(int samp_rate);
    int get_pay_len () const;
    void set_pay_len(int pay_len);
    int get_n_frame () const;
    void set_n_frame(int n_frame);
    bool get_multi_control () const;
    void set_multi_control(bool multi_control);
    int get_mean () const;
    void set_mean(int mean);
    bool get_impl_head () const;
    void set_impl_head(bool impl_head);
    bool get_has_crc () const;
    void set_has_crc(bool has_crc);
    int get_frame_period () const;
    void set_frame_period(int frame_period);
    int get_cr () const;
    void set_cr(int cr);
    int get_bw () const;
    void set_bw(int bw);

};


#endif

