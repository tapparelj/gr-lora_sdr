
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "data_source_impl.h"
#include <gnuradio/block.h>
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

data_source::sptr data_source::make(int pay_len, int n_frames,
                                    std::string string_input) {
  return gnuradio::get_initial_sptr(
      new data_source_impl(pay_len, n_frames, string_input));
}

/**
 * @brief Construct a new data source impl object
 *
 * @param pay_len : payload length
 * @param n_frames : number of frames to generate data for
 * @param string_input : input string from gnuradio-companian
 */
data_source_impl::data_source_impl(int pay_len, int n_frames,
                                   std::string string_input)
    : gr::sync_block("data_source", gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(0, 0, 0)) {
  m_n_frames = n_frames;
  m_pay_len = pay_len;
  frame_cnt = -5; // let some time to the Rx to start listening
  m_string_input = string_input;
  message_port_register_in(pmt::mp("trigg"));
  set_msg_handler(pmt::mp("trigg"),
                  [this](pmt::pmt_t msg) { this->trigg_handler(msg); });
  message_port_register_out(pmt::mp("msg"));
}

/**
 * @brief Destroy the data source impl object
 *
 */
data_source_impl::~data_source_impl() {}

/**
 * @brief Random string generator as input data for the flowgraph
 *
 * @param Nbytes : number of bytes
 * @return std::string : the random generated data string
 */
std::string data_source_impl::random_string(int Nbytes) {
  const char *charmap =
      "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const size_t charmapLength = strlen(charmap);
  auto generator = [&]() { return charmap[rand() % charmapLength]; };
  std::string result;
  result.reserve(Nbytes);
  std::generate_n(std::back_inserter(result), Nbytes, generator);
  return result;
}

/**
 * @brief Main function that handles the trigger and dispatches the message
 * making
 *
 * @param msg : PMT input msg (i.e. trigger from strobe)
 */
void data_source_impl::trigg_handler(pmt::pmt_t msg) {
  // send a new payload
  if (frame_cnt < m_n_frames && frame_cnt >= 0) {
    std::string str;
    // if no string is set generate random string otherwise use set string.
    if (m_string_input.empty()) {
      // generate random string
      str = random_string(m_pay_len);
    } else {
      str = random_string(m_pay_len);
    }
    message_port_pub(pmt::intern("msg"), pmt::mp(str));
#ifdef GRLORA_DEBUG
    GR_LOG_DEBUG(this->d_logger, "DEBUG:Input string:" + str);
#endif
    if (!mod(frame_cnt, 50))
      GR_LOG_INFO(this->d_logger,
                  "INFO:Processing frame :" + std::to_string(frame_cnt) + "/" +
                      std::to_string(m_n_frames));
    frame_cnt++;
  } else if (frame_cnt < m_n_frames) // wait some time for Rx to start listening
    frame_cnt++;
  else if (frame_cnt == m_n_frames) {
    GR_LOG_INFO(this->d_logger, "INFO:Done !, generated : " +
                                    std::to_string(m_n_frames) + " frames");
    frame_cnt++;
  }
}

int data_source_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items) {
  return 0;
}

} /* namespace lora_sdr */
} /* namespace gr */
