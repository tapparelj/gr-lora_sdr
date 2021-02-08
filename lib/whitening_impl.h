

#ifndef INCLUDED_LORA_WHITENING_IMPL_H
#define INCLUDED_LORA_WHITENING_IMPL_H

#include <lora_sdr/whitening.h>

namespace gr {
namespace lora_sdr {

class whitening_impl : public whitening {
private:
  /**
   * @brief PMT message to indicate that a new message (input data) has to be whitened
   * 
   */
  bool new_message; 

  /**
   * @brief Variables that stores the payload bytes
   * 
   */
  std::vector<uint8_t> m_payload;  

  /**
   * @brief Function that waits for the input message, if received copy its to m_payload to be used in work function
   * 
   * @param message : string input data
   */
  void msg_handler(pmt::pmt_t message);

  bool m_work_done;

public:
  /**
   * @brief Construct a new whitening impl object
   * 
   */
  whitening_impl();
  /**
   * @brief Destroy the whitening impl object
   * 
   */
  ~whitening_impl();

  /**
   * @brief General work function, the actual interleaving happens here
   * 
   * @param noutput_items : number of output items (2 * m_payload.size())
   * @param input_items : standard input item
   * @param output_items : output data
   * @return int 
   */
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
};
} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_WHITENING_IMPL_H */
