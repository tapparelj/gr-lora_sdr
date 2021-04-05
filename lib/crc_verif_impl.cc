#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "crc_verif_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

crc_verif::sptr crc_verif::make(bool exit) {
  return gnuradio::get_initial_sptr(new crc_verif_impl(exit));
}

/*
 * The private constructor
 */
crc_verif_impl::crc_verif_impl(bool exit)
    : gr::block("crc_verif", gr::io_signature::make(1, 1, sizeof(uint8_t)),
                gr::io_signature::make(0, 1, sizeof(uint8_t))) {
  message_port_register_out(pmt::mp("msg"));
}

/*
 * Our virtual destructor.
 */
crc_verif_impl::~crc_verif_impl() {}

void crc_verif_impl::forecast(int noutput_items,
                              gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 1; // m_payload_len;
}
unsigned int crc_verif_impl::crc16(uint8_t *data, uint32_t len) {

  uint16_t crc = 0x0000;
  for (uint i = 0; i < len; i++) {
    uint8_t newByte = data[i];

    for (unsigned char i = 0; i < 8; i++) {
      if (((crc & 0x8000) >> 8) ^ (newByte & 0x80)) {
        crc = (crc << 1) ^ 0x1021;
      } else {
        crc = (crc << 1);
      }
      newByte <<= 1;
    }
  }
  return crc;
}

int crc_verif_impl::general_work(int noutput_items, gr_vector_int &ninput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items) {
  uint8_t *in = (uint8_t *)input_items[0];
  uint8_t *out;
  if (output_items.size())
    out = (uint8_t *)output_items[0];
  int nitem_to_process = ninput_items[0];

  std::vector<tag_t> tags;
  get_tags_in_window(tags, 0, 0, ninput_items[0],
                     pmt::string_to_symbol("frame_info"));
  if (tags.size()) {
    if (tags[0].offset != nitems_read(0)) {
      nitem_to_process = tags[0].offset - nitems_read(0);
    } else {
      if (tags.size() >= 2) {
        nitem_to_process = tags[1].offset - tags[0].offset;
      }

      pmt::pmt_t err = pmt::string_to_symbol("error");
      m_crc_presence = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("crc"), err));
      m_payload_len = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("pay_len"), err));
      // std::cout<<m_payload_len<<" "<<nitem_to_process<<std::endl;
      // std::cout<<"\ncrc_crc "<<tags[0].offset<<" - crc:
      // "<<(int)m_crc_presence<<" - pay_len: "<<(int)m_payload_len<<"\n";
    }
  }

  if ((ninput_items[0] >= (int)m_payload_len + 2) &&
      m_crc_presence) { // wait for all the payload to come

    if (m_payload_len < 2) { // undefined CRC
      std::cout << "CRC not supported for payload smaller than 2 bytes"
                << std::endl;
      return 0;
    } else {
      // calculate CRC on the N-2 firsts data bytes
      m_crc = crc16(&in[0], m_payload_len - 2);

      // XOR the obtained CRC with the last 2 data bytes
      m_crc = m_crc ^ in[m_payload_len - 1] ^ (in[m_payload_len - 2] << 8);
#ifdef GRLORA_DEBUG
      for (int i = 0; i < (int)m_payload_len + 2; i++)
        std::cout << std::hex << (int)in[i] << std::dec << std::endl;
      std::cout << "Calculated " << std::hex << m_crc << std::dec << std::endl;
      std::cout << "Got " << std::hex
                << (in[m_payload_len] + (in[m_payload_len + 1] << 8))
                << std::dec << std::endl;
#endif

      // get payload as string
      message_str.clear();
      for (int i = 0; i < (int)m_payload_len; i++) {
        m_char = (char)in[i];
        message_str = message_str + m_char;
        if (output_items.size())
          out[i] = in[i];
      }

      cnt++;
      std::cout << "msg " << cnt << ": " << message_str << std::endl
                << std::endl;
      if (!(in[m_payload_len] + (in[m_payload_len + 1] << 8) - m_crc))
        std::cout << "CRC valid!" << std::endl << std::endl;
      else
        std::cout << RED << "CRC invalid" << RESET << std::endl << std::endl;
      message_port_pub(pmt::intern("msg"), pmt::mp(message_str));
      consume_each(m_payload_len + 2);
      return m_payload_len;
    }
  } else if ((ninput_items[0] >= (int)m_payload_len) && !m_crc_presence) {
    // get payload as string
    message_str.clear();
    for (int i = 0; i < m_payload_len; i++) {
      m_char = (char)in[i];
      message_str = message_str + m_char;
      if (output_items.size())
        out[i] = in[i];
    }
    cnt++;
    std::cout << "msg " << cnt << ": " << message_str << std::endl;
    message_port_pub(pmt::intern("msg"), pmt::mp(message_str));
    consume_each(m_payload_len);
    return m_payload_len;
  } else
    return 0;
}
} // namespace lora_sdr
} /* namespace gr */
