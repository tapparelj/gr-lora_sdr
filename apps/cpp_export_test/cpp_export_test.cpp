/********************
GNU Radio C++ Flow Graph Source File

Title: Test
GNU Radio version: 3.8.2.0
********************/

#include "cpp_export_test.hpp"
using namespace gr;


cpp_export_test::cpp_export_test () {



    this->tb = gr::make_top_block("Test");


// Blocks:
    {
        this->lora_sdr_hier_tx_0 = lora_sdr::hier_tx::make(pay_len, n_frame, "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ", cr, sf, impl_head,has_crc, samp_rate, bw, mean, true);
    }
    {
        this->lora_sdr_hier_rx_0 = lora_sdr::hier_rx::make(samp_rate, bw, sf, impl_head, cr, pay_len, has_crc, true);
    }
    {
        this->blocks_throttle_0 = blocks::throttle::make(sizeof(gr_complex)*1, samp_rate, true);
    }

// Connections:
    this->tb->hier_block2::connect(this->blocks_throttle_0, 0, this->lora_sdr_hier_rx_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_hier_tx_0, 0, this->blocks_throttle_0, 0);
}

cpp_export_test::~cpp_export_test () {
}

// Callbacks:
int cpp_export_test::get_sf () const {
    return this->sf;
}

void cpp_export_test::set_sf (int sf) {
    this->sf = sf;
}

int cpp_export_test::get_samp_rate () const {
    return this->samp_rate;
}

void cpp_export_test::set_samp_rate (int samp_rate) {
    this->samp_rate = samp_rate;
    this->blocks_throttle_0->set_sample_rate(this->samp_rate);
}

int cpp_export_test::get_pay_len () const {
    return this->pay_len;
}

void cpp_export_test::set_pay_len (int pay_len) {
    this->pay_len = pay_len;
}

int cpp_export_test::get_n_frame () const {
    return this->n_frame;
}

void cpp_export_test::set_n_frame (int n_frame) {
    this->n_frame = n_frame;
}

bool cpp_export_test::get_multi_control () const {
    return this->multi_control;
}

void cpp_export_test::set_multi_control (bool multi_control) {
    this->multi_control = multi_control;
}

int cpp_export_test::get_mult_const () const {
    return this->mult_const;
}

void cpp_export_test::set_mult_const (int mult_const) {
    this->mult_const = mult_const;
}

int cpp_export_test::get_mean () const {
    return this->mean;
}

void cpp_export_test::set_mean (int mean) {
    this->mean = mean;
}

bool cpp_export_test::get_impl_head () const {
    return this->impl_head;
}

void cpp_export_test::set_impl_head (bool impl_head) {
    this->impl_head = impl_head;
}

bool cpp_export_test::get_has_crc () const {
    return this->has_crc;
}

void cpp_export_test::set_has_crc (bool has_crc) {
    this->has_crc = has_crc;
}

int cpp_export_test::get_frame_period () const {
    return this->frame_period;
}

void cpp_export_test::set_frame_period (int frame_period) {
    this->frame_period = frame_period;
}

int cpp_export_test::get_cr () const {
    return this->cr;
}

void cpp_export_test::set_cr (int cr) {
    this->cr = cr;
}

int cpp_export_test::get_bw () const {
    return this->bw;
}

void cpp_export_test::set_bw (int bw) {
    this->bw = bw;
}


int main (int argc, char **argv) {

    cpp_export_test* top_block = new cpp_export_test();
    top_block->tb->start();
    top_block->tb->wait();

    return 0;
}
