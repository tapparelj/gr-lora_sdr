#include "modulate_impl.h"
#include "debug_tools.h"
// Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;
namespace gr {
namespace lora_sdr {

modulate::sptr modulate::make(uint8_t sf, uint32_t samp_rate, uint32_t bw,
                              bool create_zeros) {
  return gnuradio::get_initial_sptr(
      new modulate_impl(sf, samp_rate, bw, create_zeros));
}

/**
 * @brief Construct a new modulate impl object
 *
 * @param sf spreading factor
 * @param samp_rate sampling rate
 * @param bw bandwith
 */
modulate_impl::modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw,
                             bool create_zeros)
    : gr::block("modulate", gr::io_signature::make(1, 1, sizeof(uint32_t)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {

  m_sf = sf;
  m_samp_rate = samp_rate;
  m_bw = bw;

  m_number_of_bins = (uint32_t)(1u << m_sf);
  m_symbols_per_second = (double)m_bw / m_number_of_bins;
  m_samples_per_symbol = (uint32_t)(m_samp_rate / m_symbols_per_second);

  m_downchirp.resize(m_samples_per_symbol);
  m_upchirp.resize(m_samples_per_symbol);

  build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

  n_up = 8;
  symb_cnt = 0;
  m_multi_control = create_zeros;
  message_port_register_in(pmt::mp("msg"));
  set_msg_handler(pmt::mp("msg"),
                  boost::bind(&modulate_impl::msg_handler, this, _1));
  message_port_register_in(pmt::mp("ctrl_in"));
  set_tag_propagation_policy(TPP_ALL_TO_ALL);
  m_samples_send = 0;
}

/**
 * @brief Destroy the modulate impl object
 *
 */
modulate_impl::~modulate_impl() {}

/**
 * @brief standard gnuradio forecast function that tells the system that input
 * data is needed before it can continue and compute the actual modulation
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of required input items
 */
void modulate_impl::forecast(int noutput_items,
                             gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 1;
}

/**
 * @brief Gnuradio function that handles the PMT message
 *
 * @param message : PMT message (i.e. input data from datasource)
 */
void modulate_impl::msg_handler(pmt::pmt_t message) { symb_cnt = 0; }

/**
 * @brief Main function where the actual computation is done.
 *
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input data  (i.e. output of gray mapping stage)
 * @param output_items : output data
 * @return int
 */
int modulate_impl::general_work(int noutput_items, gr_vector_int &ninput_items,
                                gr_vector_const_void_star &input_items,
                                gr_vector_void_star &output_items) {
  // cast input and output to the right data type
  const uint32_t *in = (const uint32_t *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];
  if (m_create_zeros == true) {
    for (int i = 0; i < m_samples_per_symbol; i++) {
      out[i] = gr_complex(0,0);
    }
    // std::cout << "Adding zeros" << std::endl;
    // memcpy(&out[0], 0, m_samples_per_symbol * sizeof(gr_complex));
    // unsigned char val = 0;
    // int *zero = (int *)val;
    // memset(&out[0], *zero, m_samples_per_symbol * sizeof(gr_complex));
    noutput_items = m_samples_per_symbol;
    consume_each(ninput_items[0]);
  }
  // std::cout << "Running modulate" << std::endl;
  std::vector<tag_t> return_tag;
  // std::cout << nitems_read(0) << std::endl;
  get_tags_in_range(return_tag, 0, 0, nitems_read(0) + 100);
  if (return_tag.size() > 0) {
    consume_each(ninput_items[0]);
    if(m_multi_control == true){
    add_item_tag(0, nitems_written(0), pmt::intern("status"),
                 pmt::intern("done"));
    }
    else{
      m_create_zeros = true;
    }

    
    // upsampling factor
    int usFactor = 4;
    return usFactor * (m_samples_per_symbol + 2);
  } else {
    noutput_items = m_samples_per_symbol;
    uint i = 0;
    // send preamble
    if (symb_cnt < n_up + 4.25) {
      if (symb_cnt == 0) { // offset
        uint off = 0;
        // copy to the output
        memcpy(&out[0], &m_upchirp[0],
               m_samples_per_symbol * sizeof(gr_complex));
        noutput_items = m_samples_per_symbol + off;
      } else if (symb_cnt < n_up) { // upchirps
        memcpy(&out[0], &m_upchirp[0],
               m_samples_per_symbol * sizeof(gr_complex));
      } else if (symb_cnt == n_up) { // network identifier 1
        build_upchirp(&out[0], 8, m_sf);
      } else if (symb_cnt == n_up + 1) { // network identifier 2
        build_upchirp(&out[0], 16, m_sf);
      } else if (symb_cnt < n_up + 4) { // downchirps
        memcpy(&out[0], &m_downchirp[0],
               m_samples_per_symbol * sizeof(gr_complex));
      } else { // quarter of downchirp
        memcpy(&out[0], &m_downchirp[0],
               m_samples_per_symbol / 4 * sizeof(gr_complex));
        noutput_items = m_samples_per_symbol / 4;
      }
    }
    // payload
    else {
      // Returns an modulated upchirp using s_f=bw
      build_upchirp(&out[0], in[0], m_sf);
      consume_each(1);
    }
    symb_cnt++;
  }

  // #ifdef GRLORA_DEBUG
  //   // get vector length
  //   double N = 1 << m_sf;
  //   // output the modulated signal to the debugger
  //   GR_LOG_DEBUG(this->d_logger,
  //                "Output Tx:" + complex_vector_2_string(&out[0], N));
  // #endif

    m_samples_send = m_samples_send + noutput_items;
  std::cout << "Samples send:" << std::endl;
  std::cout << m_samples_send << std::endl;

  return (noutput_items);
}

} // namespace lora_sdr
} /* namespace gr */
