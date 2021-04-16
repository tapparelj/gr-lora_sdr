/********************
GNU Radio C++ Flow Graph Source File

Title: Not titled yet
GNU Radio version: 3.8.2.0
********************/

#include "zmq_test.hpp"
using namespace gr;


zmq_test::zmq_test () {



    this->tb = gr::make_top_block("Not titled yet");


// Blocks:
    {
        std::vector<uint16_t> sync_words = {8, 16};
        this->lora_sdr_hier_tx_1 = lora_sdr::hier_tx::make(pay_len, n_frame, "TrccpfQHyKfvXswsA4ySxtTiIvi10nSJCUJPYonkWqDHH005UmNfGuocPw3FHKc9",
                            cr, sf, impl_head,has_crc,
                            samp_rate, bw, mean,sync_words,true);
    }
    {
        std::vector<uint16_t> sync_words = {8, 16};
        this->lora_sdr_hier_rx_1 = lora_sdr::hier_rx::make(samp_rate, bw, sf, impl_head, cr, pay_len, has_crc, sync_words ,true);
    }
    {
        this->lora_sdr_frame_detector_2 = lora_sdr::frame_detector::make(samp_rate,bw,sf,200);
    }
    {
        std::vector<gr_complex> taps = {-0.128616616593872,	-0.212206590789194,	-0.180063263231421,	3.89817183251938e-17	,0.300105438719035	,0.636619772367581	,0.900316316157106,	1	,0.900316316157106,	0.636619772367581,	0.300105438719035,	3.89817183251938e-17,	-0.180063263231421,	-0.212206590789194,	-0.128616616593872};
        this->interp_fir_filter_xxx_0_1_0_0 = filter::interp_fir_filter_ccc::make(4, taps);
    }
    {
        this->blocks_throttle_0_1_0 = blocks::throttle::make(sizeof(gr_complex)*1, samp_rate*10, true);
    }
    {
        this->blocks_add_xx_0 = blocks::add_cc::make(1);
    }
    {
        this->noise_source_x_0 = analog::noise_source_c::make(analog::GR_UNIFORM, noise, 0);
    }

// Connections:
    this->tb->hier_block2::connect(this->analog_noise_source_x_0, 0, this->blocks_add_xx_0, 1);
    this->tb->hier_block2::connect(this->blocks_add_xx_0, 0, this->blocks_throttle_0_1_0, 0);
    this->tb->hier_block2::connect(this->blocks_throttle_0_1_0, 0, this->lora_sdr_frame_detector_2, 0);
    this->tb->hier_block2::connect(this->interp_fir_filter_xxx_0_1_0_0, 0, this->lora_sdr_hier_rx_1, 0);
    this->tb->hier_block2::connect(this->lora_sdr_frame_detector_2, 0, this->interp_fir_filter_xxx_0_1_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_hier_tx_1, 0, this->blocks_add_xx_0, 0);
}

zmq_test::~zmq_test () {
}

// Callbacks:
int zmq_test::get_sf () const {
    return this->sf;
}

void zmq_test::set_sf (int sf) {
    this->sf = sf;
}

int zmq_test::get_samp_rate () const {
    return this->samp_rate;
}

void zmq_test::set_samp_rate (int samp_rate) {
    this->samp_rate = samp_rate;
    this->blocks_throttle_0_1_0->set_sample_rate(this->samp_rate*10);
}

int zmq_test::get_pay_len () const {
    return this->pay_len;
}

void zmq_test::set_pay_len (int pay_len) {
    this->pay_len = pay_len;
}

int zmq_test::get_noise () const {
    return this->noise;
}

void zmq_test::set_noise (int noise) {
    this->noise = noise;
    this->analog_noise_source_x_0->set_amplitude(this->noise);
}

int zmq_test::get_n_frame () const {
    return this->n_frame;
}

void zmq_test::set_n_frame (int n_frame) {
    this->n_frame = n_frame;
}

int zmq_test::get_mean () const {
    return this->mean;
}

void zmq_test::set_mean (int mean) {
    this->mean = mean;
}

bool zmq_test::get_impl_head () const {
    return this->impl_head;
}

void zmq_test::set_impl_head (bool impl_head) {
    this->impl_head = impl_head;
}

bool zmq_test::get_has_crc () const {
    return this->has_crc;
}

void zmq_test::set_has_crc (bool has_crc) {
    this->has_crc = has_crc;
}

int zmq_test::get_frame_period () const {
    return this->frame_period;
}

void zmq_test::set_frame_period (int frame_period) {
    this->frame_period = frame_period;
}

int zmq_test::get_cr () const {
    return this->cr;
}

void zmq_test::set_cr (int cr) {
    this->cr = cr;
}

int zmq_test::get_bw () const {
    return this->bw;
}

void zmq_test::set_bw (int bw) {
    this->bw = bw;
}


int main (int argc, char **argv) {

    zmq_test* top_block = new zmq_test();
    top_block->tb->start();
    top_block->tb->wait();

    return 0;
}
