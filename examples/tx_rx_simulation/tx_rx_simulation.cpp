/********************
GNU Radio C++ Flow Graph Source File

Title: Tx Rx Simulation
Author: Tapparel Joachim@EPFL,TCL
GNU Radio version: 3.10.3.0
********************/

#include "tx_rx_simulation.hpp"

using namespace gr;


tx_rx_simulation::tx_rx_simulation ()  {


    this->tb = gr::make_top_block("Tx Rx Simulation");

// Blocks:
        this->lora_sdr_header_0 = lora_sdr::header::make(impl_head, has_crc, cr);

        this->blocks_vector_source_x_0 = blocks::vector_source_b::make((0, 0, 0), true, 1, []);

        this->blocks_vector_sink_x_2 = blocks::vector_sink_b::make(1, 1024);


// Connections:
    this->tb->hier_block2::connect(this->blocks_vector_source_x_0, 0, this->lora_sdr_header_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_header_0, 0, this->blocks_vector_sink_x_2, 0);
}

tx_rx_simulation::~tx_rx_simulation () {
}

// Callbacks:
bool tx_rx_simulation::get_soft_decoding () const {
    return this->soft_decoding;
}

void tx_rx_simulation::set_soft_decoding (bool soft_decoding) {
    this->soft_decoding = soft_decoding;
}

int tx_rx_simulation::get_sf () const {
    return this->sf;
}

void tx_rx_simulation::set_sf (int sf) {
    this->sf = sf;
}

int tx_rx_simulation::get_samp_rate () const {
    return this->samp_rate;
}

void tx_rx_simulation::set_samp_rate (int samp_rate) {
    this->samp_rate = samp_rate;
}

int tx_rx_simulation::get_preamb_len () const {
    return this->preamb_len;
}

void tx_rx_simulation::set_preamb_len (int preamb_len) {
    this->preamb_len = preamb_len;
}

int tx_rx_simulation::get_pay_len () const {
    return this->pay_len;
}

void tx_rx_simulation::set_pay_len (int pay_len) {
    this->pay_len = pay_len;
}

bool tx_rx_simulation::get_ldro () const {
    return this->ldro;
}

void tx_rx_simulation::set_ldro (bool ldro) {
    this->ldro = ldro;
}

bool tx_rx_simulation::get_impl_head () const {
    return this->impl_head;
}

void tx_rx_simulation::set_impl_head (bool impl_head) {
    this->impl_head = impl_head;
}

bool tx_rx_simulation::get_has_crc () const {
    return this->has_crc;
}

void tx_rx_simulation::set_has_crc (bool has_crc) {
    this->has_crc = has_crc;
}

int tx_rx_simulation::get_cr () const {
    return this->cr;
}

void tx_rx_simulation::set_cr (int cr) {
    this->cr = cr;
    this->lora_sdr_header_0->set_cr(this->cr);
}

int tx_rx_simulation::get_clk_offset () const {
    return this->clk_offset;
}

void tx_rx_simulation::set_clk_offset (int clk_offset) {
    this->clk_offset = clk_offset;
}

double tx_rx_simulation::get_center_freq () const {
    return this->center_freq;
}

void tx_rx_simulation::set_center_freq (double center_freq) {
    this->center_freq = center_freq;
}

int tx_rx_simulation::get_bw () const {
    return this->bw;
}

void tx_rx_simulation::set_bw (int bw) {
    this->bw = bw;
}

int tx_rx_simulation::get_SNRdB () const {
    return this->SNRdB;
}

void tx_rx_simulation::set_SNRdB (int SNRdB) {
    this->SNRdB = SNRdB;
}


int main (int argc, char **argv) {

    tx_rx_simulation* top_block = new tx_rx_simulation();
    top_block->tb->start();
    std::cout << "Press Enter to quit: ";
    std::cin.ignore();
    top_block->tb->stop();
    top_block->tb->wait();

    return 0;
}
