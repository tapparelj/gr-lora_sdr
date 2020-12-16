#include "deinterleaver_impl.h"
#include <gnuradio/io_signature.h>
#include <lora_sdr/utilities.h>
//Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;
namespace gr {
namespace lora_sdr {

deinterleaver::sptr deinterleaver::make(uint8_t sf) {
  return gnuradio::get_initial_sptr(new deinterleaver_impl(sf));
}

/**
 * @brief Construct a new deinterleaver impl object
 *
 * @param sf : sampling rate
 */
deinterleaver_impl::deinterleaver_impl(uint8_t sf)
    : gr::block("deinterleaver", gr::io_signature::make(1, 1, sizeof(uint32_t)),
                gr::io_signature::make(1, 1, sizeof(uint8_t))) {
  is_first = true;
  m_sf = sf;
  message_port_register_in(pmt::mp("CR"));
  set_msg_handler(
      pmt::mp("CR"),
      boost::bind(&deinterleaver_impl::header_cr_handler, this, _1));
  message_port_register_in(pmt::mp("new_frame"));
  set_msg_handler(
      pmt::mp("new_frame"),
      boost::bind(&deinterleaver_impl::new_frame_handler, this, _1));
}

/**
 * @brief Destroy the deinterleaver impl object
 *
 */
deinterleaver_impl::~deinterleaver_impl() {}

/**
 * @brief Standard gnuradio function to tell the system with
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of required output items
 */
void deinterleaver_impl::forecast(int noutput_items,
                                  gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 4;
}

/**
 * @brief Reset the block variables when a new lora packet needs to be
 * decoded.
 *
 * @param id
 */
void deinterleaver_impl::new_frame_handler(pmt::pmt_t id) { is_first = true; }

/**
 * @brief Handles the coding rate received from the header_decoder block.
 *
 * @param cr : coding rate
 */
void deinterleaver_impl::header_cr_handler(pmt::pmt_t cr) {
  m_cr = pmt::to_long(cr);
};

/**
 * @brief Main function where the actual computation is done
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input (i.e gray demapping output)
 * @param output_items : output data
 * @return int
 */
int deinterleaver_impl::general_work(int noutput_items,
                                     gr_vector_int &ninput_items,
                                     gr_vector_const_void_star &input_items,
                                     gr_vector_void_star &output_items) {
  const uint32_t *in = (uint32_t *)input_items[0];
  uint8_t *out = (uint8_t *)output_items[0];
  sf_app = is_first ? m_sf - 2 : m_sf; // Use reduced rate for the first block
  cw_len = is_first ? 8 : m_cr + 4;
  if (ninput_items[0] >= cw_len) { // wait for a full block to deinterleave
    // Create the empty matrices
    std::vector<std::vector<bool>> inter_bin(cw_len);
    std::vector<bool> init_bit(cw_len, 0);
    std::vector<std::vector<bool>> deinter_bin(sf_app, init_bit);

    // convert decimal vector to binary vector of vector
    for (int i = 0; i < cw_len; i++) {
      inter_bin[i] = int2bool(in[i], sf_app);
    }
    // #ifdef GRLORA_DEBUG
    // // std::cout<<"interleaved----"  <<std::endl;
    // // for (uint32_t i =0u ; i<cw_len ;i++){
    // //     for(int j=0;j<int(sf_app);j++){
    // //         std::cout<<inter_bin[i][j];
    // //     }
    // //     std::cout<<" "<<(int)in[i]<< std::endl;
    // // }
    // // std::cout<<std::endl;
    // #endif
    // Do the actual deinterleaving
    for (int32_t i = 0; i < cw_len; i++) {
      for (int32_t j = 0; j < int(sf_app); j++) {
        deinter_bin[mod((i - j - 1), sf_app)][i] = inter_bin[i][j];
      }
    }
    // transform codewords from binary vector to dec
    for (uint i = 0; i < sf_app; i++) {
      out[i] = bool2int(deinter_bin[i]);
    }

    // #ifdef GRLORA_DEBUG
    // // std::cout<<"codewords----"  <<std::endl;
    // // for (uint32_t i =0u ; i<sf_app ;i++){
    // //     for(int j=0;j<int(cw_len);j++){
    // //         std::cout<<deinter_bin[i][j];
    // //     }
    // //     std::cout<<" 0x"<<std::hex<<(int)out[i]<<std::dec<< std::endl;
    // // }
    // // std::cout<<std::endl;
    // #endif

    consume_each(is_first ? 8 : m_cr + 4);
    is_first = false;
    return sf_app;
  } else {
    // fix compile return type compile warning
    return 0;
  }
}
} // namespace lora_sdr
} /* namespace gr */
