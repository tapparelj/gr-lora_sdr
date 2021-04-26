#ifndef ZMQ_TEST_HPP
#define ZMQ_TEST_HPP
/********************
GNU Radio C++ Flow Graph Header File

Title: cpp_debug
GNU Radio version: 3.8.2.0
********************/

/********************
** Create includes
********************/
#include <gnuradio/top_block.h>
#include <gnuradio/blocks/throttle.h>
#include <gnuradio/filter/interp_fir_filter.h>
#include <lora_sdr/frame_detector.h>
#include <lora_sdr/hier_rx.h>
#include <lora_sdr/hier_tx.h>



using namespace gr;



class zmq_test {

private:


    lora_sdr::hier_tx::sptr lora_sdr_hier_tx_1;
    lora_sdr::hier_rx::sptr lora_sdr_hier_rx_1;
    lora_sdr::frame_detector::sptr lora_sdr_frame_detector_1;
    filter::interp_fir_filter_ccf::sptr interp_fir_filter_xxx_0_1_0;
    blocks::throttle::sptr blocks_throttle_0_1_0;


// Variables:
    int time_wait = 200;
    int threshold = 100;
    int sf = 10;
    int samp_rate = 250000;
    int pay_len = 64;
    int noise = 5;
    int n_frame = 1;
    bool multi_control = true;
    int mult_const = 1;
    bool impl_head = false;
    bool has_crc = false;
    int frame_period = 200;
    int cr = 4;
    int bw = 250000;

public:
    top_block_sptr tb;
    zmq_test();
    ~zmq_test();

    int get_time_wait () const;
    void set_time_wait(int time_wait);
    int get_threshold () const;
    void set_threshold(int threshold);
    int get_sf () const;
    void set_sf(int sf);
    int get_samp_rate () const;
    void set_samp_rate(int samp_rate);
    int get_pay_len () const;
    void set_pay_len(int pay_len);
    int get_noise () const;
    void set_noise(int noise);
    int get_n_frame () const;
    void set_n_frame(int n_frame);
    bool get_multi_control () const;
    void set_multi_control(bool multi_control);
    int get_mult_const () const;
    void set_mult_const(int mult_const);
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

