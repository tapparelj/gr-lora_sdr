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
        this->lora_sdr_whitening_0 = lora_sdr::whitening::make(false,false,',',"packet_len");

        this->lora_sdr_modulate_0 = lora_sdr::modulate::make(sf, samp_rate, bw, std::vector<uint16_t>{0x12}, preamb_len, (int(20 * std::pow(2, sf) * samp_rate / bw)));

        this->lora_sdr_interleaver_0 = lora_sdr::interleaver::make(cr, sf, ldro, 125000);

        this->lora_sdr_header_decoder_0 = lora_sdr::header_decoder::make(impl_head, cr, pay_len, has_crc, ldro, true);

        this->lora_sdr_header_0 = lora_sdr::header::make(impl_head, has_crc, cr);

        this->lora_sdr_hamming_enc_0 = lora_sdr::hamming_enc::make(cr, sf);

        this->lora_sdr_hamming_dec_0 = lora_sdr::hamming_dec::make(soft_decoding);

        this->lora_sdr_gray_mapping_0 = lora_sdr::gray_mapping::make(soft_decoding);

        this->lora_sdr_gray_demap_0 = lora_sdr::gray_demap::make(sf);

        this->lora_sdr_frame_sync_0 = lora_sdr::frame_sync::make(int(center_freq), bw, sf, impl_head, {18}, (int(samp_rate/bw)),preamb_len);

        this->lora_sdr_fft_demod_0 = lora_sdr::fft_demod::make(soft_decoding, false);

        this->lora_sdr_dewhitening_0 = lora_sdr::dewhitening::make();

        this->lora_sdr_deinterleaver_0 = lora_sdr::deinterleaver::make(soft_decoding);

        this->lora_sdr_crc_verif_0 = lora_sdr::crc_verif::make(true, false);

        this->lora_sdr_add_crc_0 = lora_sdr::add_crc::make(has_crc);

        this->blocks_throttle_0 = blocks::throttle::make(sizeof(gr_complex)*1, (samp_rate*10), true);

        this->blocks_file_source_0_0 =blocks::file_source::make(sizeof(char)*1, "/home/yujwu/Documents/gr-lora_sdr/data/GRC_default/example_tx_source.txt", true, 0, 0);


// Connections:
    this->tb->hier_block2::msg_connect(this->lora_sdr_header_decoder_0, "frame_info", this->lora_sdr_frame_sync_0, "frame_info");
    this->tb->hier_block2::connect(this->blocks_file_source_0_0, 0, this->lora_sdr_whitening_0, 0);
    this->tb->hier_block2::connect(this->blocks_throttle_0, 0, this->lora_sdr_frame_sync_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_add_crc_0, 0, this->lora_sdr_hamming_enc_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_deinterleaver_0, 0, this->lora_sdr_hamming_dec_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_dewhitening_0, 0, this->lora_sdr_crc_verif_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_fft_demod_0, 0, this->lora_sdr_gray_mapping_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_frame_sync_0, 0, this->lora_sdr_fft_demod_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_gray_demap_0, 0, this->lora_sdr_modulate_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_gray_mapping_0, 0, this->lora_sdr_deinterleaver_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_hamming_dec_0, 0, this->lora_sdr_header_decoder_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_hamming_enc_0, 0, this->lora_sdr_interleaver_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_header_0, 0, this->lora_sdr_add_crc_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_header_decoder_0, 0, this->lora_sdr_dewhitening_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_interleaver_0, 0, this->lora_sdr_gray_demap_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_modulate_0, 0, this->blocks_throttle_0, 0);
    this->tb->hier_block2::connect(this->lora_sdr_whitening_0, 0, this->lora_sdr_header_0, 0);
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
    this->lora_sdr_gray_demap_0->set_sf(this->sf);
    this->lora_sdr_hamming_enc_0->set_sf(this->sf);
    this->lora_sdr_interleaver_0->set_sf(this->sf);
    this->lora_sdr_modulate_0->set_sf(this->sf);
}

int tx_rx_simulation::get_samp_rate () const {
    return this->samp_rate;
}

void tx_rx_simulation::set_samp_rate (int samp_rate) {
    this->samp_rate = samp_rate;
    this->blocks_throttle_0->set_sample_rate((this->samp_rate*10));
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
    this->lora_sdr_hamming_enc_0->set_cr(this->cr);
    this->lora_sdr_header_0->set_cr(this->cr);
    this->lora_sdr_interleaver_0->set_cr(this->cr);
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
    top_block->tb->wait();

    return 0;
}
