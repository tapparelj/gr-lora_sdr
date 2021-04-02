#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "deinterleaver_impl.h"
#include <gnuradio/io_signature.h>
#include <lora_sdr/utilities.h>

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
  // is_first = true;
  m_sf = sf;
  set_tag_propagation_policy(TPP_DONT);
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

  std::vector<tag_t> tags;
  get_tags_in_window(tags, 0, 0, 1, pmt::string_to_symbol("frame_info"));
  if (tags.size()) {
    pmt::pmt_t err = pmt::string_to_symbol("error");
    m_is_header = pmt::to_bool(
        pmt::dict_ref(tags[0].value, pmt::string_to_symbol("is_header"), err));
    if (m_is_header) {
      //   std::cout<<"deinterleaver_header "<<tags[0].offset<<std::endl;
      // is_first = true;
    } else {
      // is_first=false;
      m_cr = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cr"), err));

      // std::cout<<"\ndeinter_cr "<<tags[0].offset<<" - cr: "<<(int)m_cr<<"\n";
    }
    tags[0].offset = nitems_written(0);
    add_item_tag(0, tags[0]);
  }

  sf_app = m_is_header ? m_sf - 2 : m_sf; // Use reduced rate for the first
                                          // block
  cw_len = m_is_header ? 8 : m_cr + 4;
  if (ninput_items[0] >= cw_len) { // wait for a full block to deinterleave
    // Create the empty matrices
    std::vector<std::vector<bool>> inter_bin(cw_len);
    std::vector<bool> init_bit(cw_len, 0);
    std::vector<std::vector<bool>> deinter_bin(sf_app, init_bit);

    // convert decimal vector to binary vector of vector
    for (int i = 0; i < cw_len; i++) {
      inter_bin[i] = int2bool(in[i], sf_app);
    }
#ifdef GRLORA_DEBUG
    std::cout << "interleaved----" << std::endl;
    for (uint32_t i = 0u; i < cw_len; i++) {
      for (int j = 0; j < int(sf_app); j++) {
        std::cout << inter_bin[i][j];
      }
      std::cout << " " << (int)in[i] << std::endl;
    }
    std::cout << std::endl;
#endif
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

#ifdef GRLORA_DEBUG
    std::cout << "codewords----" << std::endl;
    for (uint32_t i = 0u; i < sf_app; i++) {
      for (int j = 0; j < int(cw_len); j++) {
        std::cout << deinter_bin[i][j];
      }
      std::cout << " 0x" << std::hex << (int)out[i] << std::dec << std::endl;
    }
    std::cout << std::endl;
#endif
    // if(is_first)
    //     add_item_tag(0, nitems_written(0),
    //     pmt::string_to_symbol("header_len"), pmt::mp((long)sf_app));//sf_app
    //     is the header part size
    consume_each(cw_len);

    if (noutput_items < sf_app)
      std::cout << RED << "wow1! " << noutput_items << "/" << sf_app
                << std::endl;
    return sf_app;
  }
  return 0;
}
} // namespace lora_sdr
} /* namespace gr */
