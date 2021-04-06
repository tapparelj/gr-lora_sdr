#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "dewhitening_impl.h"
#include "tables.h"
#include <gnuradio/io_signature.h>
#include <lora_sdr/utilities.h>

namespace gr {
namespace lora_sdr {

dewhitening::sptr dewhitening::make() {
  return gnuradio::get_initial_sptr(new dewhitening_impl());
}

/**
 * @brief Construct a new dewhitening impl object
 *
 */
dewhitening_impl::dewhitening_impl()
    : gr::block("dewhitening", gr::io_signature::make(1, 1, sizeof(uint8_t)),
                gr::io_signature::make(1, 1, sizeof(uint8_t))) {
  set_tag_propagation_policy(TPP_DONT);
}

/**
 * @brief Destroy the dewhitening impl object
 *
 */
dewhitening_impl::~dewhitening_impl() {}

/**
 * @brief standard gnuradio function to tell the system when to start work
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of input items required
 */
void dewhitening_impl::forecast(int noutput_items,
                                gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 2;
}

/**
 * @brief Handles the payload length received from the header_decoder block.
 *
 * @param payload_len : payload length
 */
void dewhitening_impl::header_pay_len_handler(pmt::pmt_t payload_len) {
  m_payload_len = pmt::to_long(payload_len);
};

/**
 * @brief Reset the block variables for a new frame.
 *
 * @param id
 */
void dewhitening_impl::new_frame_handler(pmt::pmt_t id) { offset = 0; }

/**
 * @brief Receive indication on the CRC presence
 *
 * @param crc_presence : control message if add_crc is active
 */
void dewhitening_impl::header_crc_handler(pmt::pmt_t crc_presence) {
  m_crc_presence = pmt::to_long(crc_presence);
};

/**
 * @brief Main dewhitining function
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input data (i.e. header_decoder stage)
 * @param output_items : output data
 * @return int
 */
int dewhitening_impl::general_work(int noutput_items,
                                   gr_vector_int &ninput_items,
                                   gr_vector_const_void_star &input_items,
                                   gr_vector_void_star &output_items) {
  const uint8_t *in = (const uint8_t *)input_items[0];
  uint8_t *out = (uint8_t *)output_items[0];
  int nitem_to_process = ninput_items[0];
        //search for work_done tags and if found add them to the stream
        std::vector<tag_t> work_done_tags;
        get_tags_in_window(work_done_tags, 0, 0, ninput_items[0],
                           pmt::string_to_symbol("work_done"));
        if (work_done_tags.size()) {
            add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
                         pmt::intern("done"), pmt::intern("dewhitening"));
            return 1;
        }
  uint8_t low_nib, high_nib;

  std::vector<tag_t> tags;
  get_tags_in_window(tags, 0, 0, ninput_items[0],
                     pmt::string_to_symbol("frame_info"));
  if (tags.size()) {
    if (tags[0].offset != nitems_read(0))
      nitem_to_process = tags[0].offset - nitems_read(0);

    else {
      if (tags.size() >= 2)
        nitem_to_process = tags[1].offset - tags[0].offset;

      pmt::pmt_t err = pmt::string_to_symbol("error");
      m_crc_presence = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("crc"), err));
      m_payload_len = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("pay_len"), err));
      offset = 0;
      tags[0].offset = nitems_written(0);
      add_item_tag(0, tags[0]);
      // std::cout<<"\ndewi_crc "<<tags[0].offset<<" - crc:
      // "<<(int)m_crc_presence<<" - pay_len: "<<(int)m_payload_len<<"\n";
    }
  }

  for (int i = 0; i < nitem_to_process / 2; i++) {

    if (offset < m_payload_len) {
      low_nib = in[2 * i] ^ (whitening_seq[offset] & 0x0F);
      high_nib = in[2 * i + 1] ^ (whitening_seq[offset] & 0xF0) >> 4;
      dewhitened.push_back(high_nib << 4 | low_nib);
    } else if ((offset < m_payload_len + 2) &&
               m_crc_presence) { // do not dewhiten the CRC
      low_nib = in[2 * i];
      high_nib = in[2 * i + 1];
      dewhitened.push_back(high_nib << 4 | low_nib);
    } else { // full packet received
      break;
    }
    offset++;
  }
#ifdef GRLORA_DEBUGV
  for (uint i = 0; i < dewhitened.size(); i++) {
    std::cout << (char)(int)dewhitened[i] << "    0x" << std::hex
              << (int)dewhitened[i] << std::dec << std::endl;
  }
#endif
  consume_each(dewhitened.size() * 2); // ninput_items[0]/2*2);
  noutput_items = dewhitened.size();
  memcpy(out, &dewhitened[0], noutput_items * sizeof(uint8_t));

  dewhitened.clear();
  return noutput_items;
}
} // namespace lora_sdr
} /* namespace gr */
