#include "crc_verif_impl.h"
#include <gnuradio/io_signature.h>
// Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;
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
                gr::io_signature::make(0, 0, 0)) {
  message_port_register_out(pmt::mp("msg"));

  message_port_register_in(pmt::mp("pay_len"));
  set_msg_handler(
      pmt::mp("pay_len"),
      boost::bind(&crc_verif_impl::header_pay_len_handler, this, _1));
  message_port_register_in(pmt::mp("CRC"));
  set_msg_handler(pmt::mp("CRC"),
                  boost::bind(&crc_verif_impl::header_crc_handler, this, _1));
  m_exit = exit;
}

/*
 * Our virtual destructor.
 */
crc_verif_impl::~crc_verif_impl() {}

/**
 * @brief standard gnuradio function to tell the system when to start work
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of input items required
 */
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

/**
 * @brief Handles the payload length received from the header_decoder block.
 *
 * @param payload_len : payload length
 */
void crc_verif_impl::header_pay_len_handler(pmt::pmt_t payload_len) {
  m_payload_len = pmt::to_long(payload_len);
  in_buff.clear();
};

/**
 * @brief Handles the crc_presence received from the header_decoder block.
 *
 * @param crc_presence : boolean is crc is turned on
 */
void crc_verif_impl::header_crc_handler(pmt::pmt_t crc_presence) {
  m_crc_presence = pmt::to_long(crc_presence);
};

/**
 * @brief Main crc verify function that verifies the Cyclic redundancy check
 * (CRC) from the add_crc stage
 *
 * @param noutput_items : number of output items
 * @param ninput_items  : number of input items
 * @param input_items  : input items (i.e. dewhitening)
 * @param output_items : output data
 * @return int
 */
int crc_verif_impl::general_work(int noutput_items, gr_vector_int &ninput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items) {
  uint8_t *in = (uint8_t *)input_items[0];

  // return tag vector
  std::vector<tag_t> return_tag;
  // get tags from stream
  get_tags_in_range(return_tag, 0, 0, nitems_read(0) + 1);
  // if we found tags
  if (return_tag.size() > 0) {
    GR_LOG_INFO(this->d_logger, "Got a tag 'done', quitting flowgraph..");
    // message ctrl port we are done
    consume_each(ninput_items[0]);
    // exit program
    if(m_exit == true){
    std::exit(EXIT_SUCCESS);
    // set internal state to being done
    return WORK_DONE;
    }
    else{
      return 1;
    }
    // return WORK_DONE;
  }

  for (size_t i = 0; i < ninput_items[0]; i++) {
    in_buff.push_back(in[i]);
  }
  consume_each(ninput_items[0]);

  if (in_buff.size() >= (int)m_payload_len + 2 &&
      m_crc_presence) {    // wait for all the payload to come
    if (m_payload_len < 2) // undefined CRC
      GR_LOG_WARN(this->d_logger,
                  "WARN:Disable CRC for payload smaller than 2 bytes")
    else {
      // calculate CRC on the N-2 firsts data bytes
      m_crc = crc16(&in_buff[0], m_payload_len - 2);

      // XOR the obtained CRC with the last 2 data bytes
      m_crc = m_crc ^ in_buff[m_payload_len - 1] ^
              (in_buff[m_payload_len - 2] << 8);

      // get payload as string
      message_str.clear();
      for (int i = 0; i < in_buff.size() - 2; i++) {
        m_char = (char)in_buff[i];
        message_str = message_str + m_char;
      }
      GR_LOG_INFO(this->d_logger, "Decode msg is:" + message_str);
      if (!(in_buff[m_payload_len] + (in_buff[m_payload_len + 1] << 8) -
            m_crc)) {
#ifdef GRLORA_DEBUG
        GR_LOG_DEBUG(this->d_logger, "CRC is valid!");
#endif
      } else {
        GR_LOG_INFO(this->d_logger, "CRC is invalid");
#ifdef GRLORA_DEBUG
        GR_LOG_DEBUG(this->d_logger, "CRC is invalid");
#endif
      }
      message_port_pub(pmt::intern("msg"), pmt::mp(message_str));
      in_buff.clear();
      return 0;
    }
  }
  if (in_buff.size() >= (int)m_payload_len && !m_crc_presence) {
    // get payload as string
    message_str.clear();
    for (int i = 0; i < in_buff.size(); i++) {
      m_char = (char)in_buff[i];
      message_str = message_str + m_char;
    }
    GR_LOG_INFO(this->d_logger, "Decode msg is:" + message_str);
    message_port_pub(pmt::intern("msg"), pmt::mp(message_str));
    in_buff.clear();
    return 0;
  } else {
    return 0;
  }
}
} // namespace lora_sdr
} /* namespace gr */
