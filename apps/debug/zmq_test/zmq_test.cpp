/********************
GNU Radio C++ Flow Graph Source File

Title: Not titled yet
GNU Radio version: 3.8.2.0
********************/

#include "zmq_test.hpp"
using namespace gr;


zmq_test::zmq_test () {


    std::vector<uint16_t> test {8,16};
    this->tb = gr::make_top_block("Not titled yet");


// Blocks:
    {
        this->lora_sdr_whitening_0_0 = lora_sdr::whitening::make();
    }
    {
        this->lora_sdr_modulate_0_0 = lora_sdr::modulate::make(sf, samp_rate, bw, test,false);
    }
    {
        this->lora_sdr_interleaver_0_0 = lora_sdr::interleaver::make(cr, sf);
    }
    {
        this->lora_sdr_header_0_0 = lora_sdr::header::make(impl_head, has_crc, cr);
    }
    {
        this->lora_sdr_hamming_enc_0_0 = lora_sdr::hamming_enc::make(cr, sf);
    }
    {
        this->lora_sdr_gray_decode_0_0 = lora_sdr::gray_decode::make(sf);
    }
    {
        this->lora_sdr_data_source_sim_0 = lora_sdr::data_source_sim::make(64, n_frame, "ssKTiomvPXMuARfDvU5zzMIoQfJlOtZ4LxNSJ0dmLOGctMDOuzeTbK8PPH0r0NmA", 200, true);
    }
    {
        this->lora_sdr_add_crc_0_0 = lora_sdr::add_crc::make(has_crc);
    }
    {
        this->blocks_throttle_0_1 = blocks::throttle::make(sizeof(gr_complex)*1, samp_rate*10, true);
    }
    {
        this->blocks_null_sink_0 = blocks::null_sink::make(sizeof(gr_complex)*1);
    }

// Connections:
    this->tb->hier_block2::connect(this->blocks_throttle_0_1, 0, this->blocks_null_sink_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_add_crc_0_0, 0, this->lora_sdr_hamming_enc_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_data_source_sim_0, 0, this->lora_sdr_whitening_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_gray_decode_0_0, 0, this->lora_sdr_modulate_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_hamming_enc_0_0, 0, this->lora_sdr_interleaver_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_header_0_0, 0, this->lora_sdr_add_crc_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_interleaver_0_0, 0, this->lora_sdr_gray_decode_0_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_modulate_0_0, 0, this->blocks_throttle_0_1, 0);
    this->tb->hier_block2::connect(this->lora_sdr_whitening_0_0, 0, this->lora_sdr_header_0_0, 0);
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
    this->blocks_throttle_0_1->set_sample_rate(this->samp_rate*10);
}

int zmq_test::get_pay_len () const {
    return this->pay_len;
}

void zmq_test::set_pay_len (int pay_len) {
    this->pay_len = pay_len;
}

int zmq_test::get_n_frame () const {
    return this->n_frame;
}

void zmq_test::set_n_frame (int n_frame) {
    this->n_frame = n_frame;
}

bool zmq_test::get_multi_control () const {
    return this->multi_control;
}

void zmq_test::set_multi_control (bool multi_control) {
    this->multi_control = multi_control;
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
