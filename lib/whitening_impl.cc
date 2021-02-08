

#include "whitening_impl.h"
#include "debug_tools.h"
#include "tables.h"
#include <gnuradio/io_signature.h>
// Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;
namespace gr {
namespace lora_sdr {

whitening::sptr whitening::make() {
  return gnuradio::get_initial_sptr(new whitening_impl());
}

/**
 * @brief Construct a new whitening impl object
 *
 */
whitening_impl::whitening_impl()
    : gr::sync_block("whitening", gr::io_signature::make(0, 1, sizeof(uint8_t)),
                     gr::io_signature::make(0, 1, sizeof(uint8_t))) {
  new_message = false;

  message_port_register_in(pmt::mp("msg"));
  set_msg_handler(pmt::mp("msg"), // This is the port identifier
                  boost::bind(&whitening_impl::msg_handler, this, _1));
  set_tag_propagation_policy(TPP_ALL_TO_ALL);
}

/**
 * @brief Destroy the whitening impl object
 *
 */
whitening_impl::~whitening_impl() {}

/**
 * @brief Function that waits for the input message, if received copy its to
 * m_payload to be used in work function
 *
 * @param message : string input data
 */
void whitening_impl::msg_handler(pmt::pmt_t message) {
  // get pmt message and parse to string
  std::string str = pmt::symbol_to_string(message);
  if (str == "done") {
    m_work_done = true;
  }
  // copy string into variable m_payload
  std::copy(str.begin(), str.end(), std::back_inserter(m_payload));
  new_message = true;
}

/**
 * @brief General work function, the actual interleaving happens here
 *
 * @param noutput_items : number of output items (2 * m_payload.size())
 * @param input_items : standard input item
 * @param output_items : output data
 * @return int
 */
int whitening_impl::work(int noutput_items,
                         gr_vector_const_void_star &input_items,
                         gr_vector_void_star &output_items) {
  std::vector<tag_t> return_tag;
  // std::cout << nitems_read(0) << std::endl;
  get_tags_in_range(return_tag, 0, 0, nitems_read(0) + 10);
  if (return_tag.size() > 0) {
    add_item_tag(0, nitems_written(0), pmt::intern("status"),
                 pmt::intern("done"));
    noutput_items = 1;
    // return noutput_items;
  } else {
    if (new_message) {
      uint8_t *out = (uint8_t *)output_items[0];
      // do the actual whitening of the payload data
      for (uint i = 0; i < m_payload.size(); i++) {
        out[2 * i] = (m_payload[i] ^ whitening_seq[i]) & 0x0F;
        out[2 * i + 1] = (m_payload[i] ^ whitening_seq[i]) >> 4;
      }

      // set number of output items and clear payload message
      noutput_items = 2 * m_payload.size();
      m_payload.clear();
      new_message = false;

    } else {
      noutput_items = 0;
    }
  }

  return noutput_items;
}

} // namespace lora_sdr
} /* namespace gr */
