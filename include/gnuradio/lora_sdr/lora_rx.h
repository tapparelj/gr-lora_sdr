#ifndef LORA_RX_HPP
#define LORA_RX_HPP

#include <gnuradio/lora_sdr/api.h>
#include <gnuradio/top_block.h>
#include <gnuradio/lora_sdr/crc_verif.h>
#include <gnuradio/lora_sdr/deinterleaver.h>
#include <gnuradio/lora_sdr/dewhitening.h>
#include <gnuradio/lora_sdr/fft_demod.h>
#include <gnuradio/lora_sdr/frame_sync.h>
#include <gnuradio/lora_sdr/gray_mapping.h>
#include <gnuradio/lora_sdr/hamming_dec.h>
#include <gnuradio/lora_sdr/header_decoder.h>

namespace gr {
  namespace lora_sdr {

    class LORA_SDR_API lora_sdr_rx : public gr::hier_block2 {
    private:
        lora_sdr::header_decoder::sptr lora_sdr_header_decoder_0;
        lora_sdr::hamming_dec::sptr lora_sdr_hamming_dec_0;
        lora_sdr::gray_mapping::sptr lora_sdr_gray_mapping_0;
        lora_sdr::frame_sync::sptr lora_sdr_frame_sync_0;
        lora_sdr::fft_demod::sptr lora_sdr_fft_demod_0;
        lora_sdr::dewhitening::sptr lora_sdr_dewhitening_0;
        lora_sdr::deinterleaver::sptr lora_sdr_deinterleaver_0;
        lora_sdr::crc_verif::sptr lora_sdr_crc_verif_0;
    public:
        lora_sdr_rx(int bw,
                    uint8_t cr,
                    bool has_crc,
                    uint8_t impl_head,
                    uint8_t pay_len,
                    uint32_t samp_rate,
                    uint8_t sf,
                    bool soft_decoding,
                    uint8_t ldro,
                    std::vector<bool> print_rx);
        ~lora_sdr_rx() {};
    };

    //overload the constructor
    lora_sdr_rx::lora_sdr_rx(int bw,
                            uint8_t cr,
                            bool has_crc,
                            uint8_t impl_head,
                            uint8_t pay_len,
                            uint32_t samp_rate,
                            uint8_t sf,
                            bool soft_decoding,
                            uint8_t ldro_mode,
                            std::vector<bool> print_rx) : gr::hier_block2("lora_sdr_rx",
                                                            gr::io_signature::make(1, 1, sizeof(gr_complex)*1),
                                                            gr::io_signature::make(1, 1, sizeof(char)*1)) {

        uint32_t center_freq = 868100000;
        uint16_t preamble_len = 8;
        std::vector<uint16_t> sync_word = {18};
        bool print_header = print_rx[0];
        bool print_payload = print_rx[1];

        this->lora_sdr_header_decoder_0 = lora_sdr::header_decoder::make(impl_head, cr, pay_len, has_crc, ldro_mode, print_header);
        this->lora_sdr_hamming_dec_0 = lora_sdr::hamming_dec::make(soft_decoding);
        this->lora_sdr_gray_mapping_0 = lora_sdr::gray_mapping::make(soft_decoding);
        this->lora_sdr_frame_sync_0 = lora_sdr::frame_sync::make(center_freq, bw, sf, impl_head, sync_word, int(samp_rate/bw), preamble_len);
        this->lora_sdr_fft_demod_0 = lora_sdr::fft_demod::make(soft_decoding, true);
        this->lora_sdr_dewhitening_0 = lora_sdr::dewhitening::make();
        this->lora_sdr_deinterleaver_0 = lora_sdr::deinterleaver::make(soft_decoding);
        this->lora_sdr_crc_verif_0 = lora_sdr::crc_verif::make(print_payload, false);

        hier_block2::connect(self(),0, this->lora_sdr_frame_sync_0, 0);
        hier_block2::connect(this->lora_sdr_frame_sync_0, 0, this->lora_sdr_fft_demod_0, 0);
        hier_block2::connect(this->lora_sdr_fft_demod_0, 0, this->lora_sdr_gray_mapping_0, 0);
        hier_block2::connect(this->lora_sdr_gray_mapping_0, 0, this->lora_sdr_deinterleaver_0, 0);
        hier_block2::connect(this->lora_sdr_deinterleaver_0, 0, this->lora_sdr_hamming_dec_0, 0);
        hier_block2::connect(this->lora_sdr_hamming_dec_0, 0, this->lora_sdr_header_decoder_0, 0);
        hier_block2::connect(this->lora_sdr_header_decoder_0, 0, this->lora_sdr_dewhitening_0, 0);
        hier_block2::connect(this->lora_sdr_dewhitening_0, 0, this->lora_sdr_crc_verif_0, 0);
        hier_block2::connect(this->lora_sdr_crc_verif_0, 0, self(), 0);
    }

    typedef std::shared_ptr<lora_sdr_rx> sptr;
    sptr make_lora_sdr_rx(int bw,
                        uint8_t cr,
                        bool has_crc,
                        uint8_t impl_head,
                        uint8_t pay_len,
                        uint32_t samp_rate,
                        uint8_t sf,
                        bool soft_decoding,
                        uint8_t ldro_mode,
                        std::vector<bool> print_rx) {
                                
        return gnuradio::get_initial_sptr(new lora_sdr_rx(bw,
                                                        cr,
                                                        has_crc,
                                                        impl_head,
                                                        pay_len,
                                                        samp_rate,
                                                        sf,
                                                        soft_decoding,
                                                        ldro_mode,
                                                        print_rx));
    }
  };
}

#endif