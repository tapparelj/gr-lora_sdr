

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include "whitening_impl.h"
#include "tables.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

whitening::sptr whitening::make() {
  return gnuradio::get_initial_sptr(new whitening_impl());
}

/**
 * @brief Construct a new whitening impl::whitening impl object
 *
 */
whitening_impl::whitening_impl()
    : gr::sync_block("whitening", gr::io_signature::make(0, 1, sizeof(uint8_t)),
                     gr::io_signature::make(0, 1, sizeof(uint8_t))) {
  new_message = false;
  set_tag_propagation_policy(TPP_ONE_TO_ONE);
  message_port_register_in(pmt::mp("msg"));
  set_msg_handler(pmt::mp("msg"),
                  [this](pmt::pmt_t msg) { this->msg_handler(msg); });
}

/**
 * @brief Destroy the whitening impl::whitening impl object
 *
 */
whitening_impl::~whitening_impl() {}

/**
 * @brief
 *
 * @param message
 */
void whitening_impl::msg_handler(pmt::pmt_t message) {

  //  payload_str.push_back(random_string(rand()%253+2));
  // payload_str.push_back(rand()%2?"12345":"abcdefghijklmnop");
  payload_str.push_back(pmt::symbol_to_string(message));
  // std::copy(payload_str.begin(), payload_str.end(),
  // std::back_inserter(m_payload));
  new_message = true;
}

/**
 * @brief
 *
 * @param noutput_items
 * @param input_items
 * @param output_items
 * @return int
 */
int whitening_impl::work(int noutput_items,
                         gr_vector_const_void_star &input_items,
                         gr_vector_void_star &output_items) {
  //search for work_done tags and if found add them to the stream
  std::vector<tag_t> work_done_tags;
  get_tags_in_window(work_done_tags, 0, 0, nitems_read(0) + 10,
                      pmt::string_to_symbol("work_done"));
  if (work_done_tags.size()) {
      add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
                    pmt::intern("done"),pmt::intern("whitening"));
      noutput_items = 1;
  }else {
      if (payload_str.size() >= 100 && !(payload_str.size() % 100))
          std::cout << RED << payload_str.size()
                    << " frames in waiting list. Transmitter has issue to keep up at "
                       "that transmission frequency."
                    << RESET << std::endl;
      if (payload_str.size() && noutput_items >= 2 * payload_str.front().length()) {
          pmt::pmt_t frame_len = pmt::from_long(2 * payload_str.front().length());
          add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_len"),
                       frame_len);

          add_item_tag(0, nitems_written(0), pmt::string_to_symbol("payload_str"),
                       pmt::string_to_symbol(payload_str.front()));

          uint8_t *out = (uint8_t *) output_items[0];

          std::copy(payload_str.front().begin(), payload_str.front().end(),
                    std::back_inserter(m_payload));

          for (uint i = 0; i < m_payload.size(); i++) {
              out[2 * i] = (m_payload[i] ^ whitening_seq[i]) & 0x0F;
              out[2 * i + 1] = (m_payload[i] ^ whitening_seq[i]) >> 4;
          }

          noutput_items = 2 * m_payload.size();
          m_payload.clear();
          payload_str.erase(payload_str.begin());
          new_message = false;
      } else {
          noutput_items = 0;
      }
  }
  return noutput_items;
}

} // namespace lora_sdr
} /* namespace gr */
