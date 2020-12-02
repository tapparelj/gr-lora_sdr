#include "err_measures_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

err_measures::sptr err_measures::make() {
  return gnuradio::get_initial_sptr(new err_measures_impl());
}

/**
 * @brief Construct a new err measures impl object
 *
 */
err_measures_impl::err_measures_impl()
    : gr::sync_block("err_measures", gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(0, 0, 0)) {
  drop = 0;
  message_port_register_in(pmt::mp("msg"));
  set_msg_handler(pmt::mp("msg"),
                  boost::bind(&err_measures_impl::msg_handler, this, _1));
  message_port_register_in(pmt::mp("ref"));
  set_msg_handler(pmt::mp("ref"),
                  boost::bind(&err_measures_impl::ref_handler, this, _1));
  message_port_register_out(pmt::mp("err"));
  // #ifdef GRLORA_MEASUREMENTS
  // int num = 0;//check next file name to use
  // while(1){
  //     std::ifstream
  //     infile("../matlab/measurements/err"+std::to_string(num)+".txt");
  //      if(!infile.good())
  //         break;
  //     num++;
  // }
  // err_outfile.open("../matlab/measurements/err"+std::to_string(num)+".txt",
  // std::ios::out | std::ios::trunc ); #endif
}

/**
 * @brief Destroy the err measures impl object
 *
 */
err_measures_impl::~err_measures_impl() {}

/**
 * @brief Bit counter
 * 
 * @param n : number of bits
 * @return int 
 */
int countSetBits(int n) {
  // base case
  if (n == 0)
    return 0;
  else
    return 1 + countSetBits(n & (n - 1));
}

/**
 * @brief Msg handler, will handle the incoming decoded message
 *
 * @param msg : decoded payload message
 */
void err_measures_impl::msg_handler(pmt::pmt_t msg) {
  std::string payload = pmt::symbol_to_string(msg);
  m_payload.resize(payload.length() + 1);
  strcpy(&m_payload[0], pmt::symbol_to_string(msg).c_str());
  BE = 0;

  for (size_t i = 0; (i < payload.length()) && (i < m_corr_payload.size());
       i++) {
    BE += countSetBits((m_corr_payload[i] ^ m_payload[i]));
  }
  //   #ifdef GRLORA_MEASUREMENTS
  //   err_outfile<<BE<<",";
  //   #endif
  GR_LOG_INFO(this->d_logger,
              "INFO: Bit Error Count (BER): " + std::to_string(BE));
  if (BE > 0)
    message_port_pub(pmt::intern("err"), pmt::mp(BE));
  drop = 0;
};

/**
 * @brief Reference handler, input of the reference payload
 *
 * @param ref : reference payload to compare against
 */
void err_measures_impl::ref_handler(pmt::pmt_t ref) {
  //   #ifdef GRLORA_MEASUREMENTS
  //   if(drop){
  //           err_outfile<<"-1,";
  //   }
  //   #endif
  drop = 1;
  m_corr_payload.resize(pmt::symbol_to_string(ref).length() + 1);
  strcpy(&m_corr_payload[0], pmt::symbol_to_string(ref).c_str());
}

/**
 * @brief Main function of error measurement
 *
 * @param noutput_items : number of output items
 * @param input_items  : input items (i.e data from dewhitening)
 * @param output_items : output data (i.e. decode payload)
 * @return int
 */
int err_measures_impl::work(int noutput_items,
                            gr_vector_const_void_star &input_items,
                            gr_vector_void_star &output_items) {
  return 0;
}

} /* namespace lora_sdr */
} /* namespace gr */
