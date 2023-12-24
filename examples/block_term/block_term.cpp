/********************
GNU Radio C++ Flow Graph Source File

Title: Block Term
Author: Tapparel Joachim@EPFL,TCL
GNU Radio version: 3.10.3.0
********************/

#include "block_term.hpp"

using namespace gr;


block_term::block_term ()  {


    this->tb = gr::make_top_block("Block Term");

// Blocks:
        this->lora_sdr_header_decoder_0 = lora_sdr::header_decoder::make(impl_head, cr, pay_len, has_crc, ldro, true);

        this->lora_sdr_hamming_dec_0 = lora_sdr::hamming_dec::make(soft_decoding);

        this->lora_sdr_gray_mapping_0 = lora_sdr::gray_mapping::make(soft_decoding);

        this->lora_sdr_frame_sync_0 = lora_sdr::frame_sync::make(int(center_freq), bw, sf, impl_head, {18}, (int(samp_rate/bw)),preamb_len);

        this->lora_sdr_fft_demod_0 = lora_sdr::fft_demod::make(soft_decoding, false);

        this->lora_sdr_dewhitening_0 = lora_sdr::dewhitening::make();

        this->lora_sdr_deinterleaver_0 = lora_sdr::deinterleaver::make(soft_decoding);

        this->lora_sdr_crc_verif_0 = lora_sdr::crc_verif::make(true, false);

        this->analog_noise_source_x_0 = analog::noise_source_c::make(analog::GR_GAUSSIAN, 1, 0);


// Connections:
    this->tb->hier_block2::msg_connect(this->lora_sdr_header_decoder_0, "frame_info", this->lora_sdr_frame_sync_0, "frame_info");
    this->tb->hier_block2::connect(this->analog_noise_source_x_0, 0, this->lora_sdr_frame_sync_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_deinterleaver_0, 0, this->lora_sdr_hamming_dec_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_dewhitening_0, 0, this->lora_sdr_crc_verif_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_fft_demod_0, 0, this->lora_sdr_gray_mapping_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_frame_sync_0, 0, this->lora_sdr_fft_demod_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_gray_mapping_0, 0, this->lora_sdr_deinterleaver_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_hamming_dec_0, 0, this->lora_sdr_header_decoder_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_header_decoder_0, 0, this->lora_sdr_dewhitening_0, 0);
}

block_term::~block_term () {
}

// Callbacks:
bool block_term::get_soft_decoding () const {
    return this->soft_decoding;
}

void block_term::set_soft_decoding (bool soft_decoding) {
    this->soft_decoding = soft_decoding;
}

int block_term::get_sf () const {
    return this->sf;
}

void block_term::set_sf (int sf) {
    this->sf = sf;
}

int block_term::get_samp_rate () const {
    return this->samp_rate;
}

void block_term::set_samp_rate (int samp_rate) {
    this->samp_rate = samp_rate;
}

int block_term::get_preamb_len () const {
    return this->preamb_len;
}

void block_term::set_preamb_len (int preamb_len) {
    this->preamb_len = preamb_len;
}

int block_term::get_pay_len () const {
    return this->pay_len;
}

void block_term::set_pay_len (int pay_len) {
    this->pay_len = pay_len;
}

bool block_term::get_ldro () const {
    return this->ldro;
}

void block_term::set_ldro (bool ldro) {
    this->ldro = ldro;
}

bool block_term::get_impl_head () const {
    return this->impl_head;
}

void block_term::set_impl_head (bool impl_head) {
    this->impl_head = impl_head;
}

bool block_term::get_has_crc () const {
    return this->has_crc;
}

void block_term::set_has_crc (bool has_crc) {
    this->has_crc = has_crc;
}

int block_term::get_cr () const {
    return this->cr;
}

void block_term::set_cr (int cr) {
    this->cr = cr;
}

int block_term::get_clk_offset () const {
    return this->clk_offset;
}

void block_term::set_clk_offset (int clk_offset) {
    this->clk_offset = clk_offset;
}

double block_term::get_center_freq () const {
    return this->center_freq;
}

void block_term::set_center_freq (double center_freq) {
    this->center_freq = center_freq;
}

int block_term::get_bw () const {
    return this->bw;
}

void block_term::set_bw (int bw) {
    this->bw = bw;
}

int block_term::get_SNRdB () const {
    return this->SNRdB;
}

void block_term::set_SNRdB (int SNRdB) {
    this->SNRdB = SNRdB;
}


int main (int argc, char **argv) {

    block_term* top_block = new block_term();
    top_block->tb->start();
    top_block->tb->wait();

    return 0;
}
