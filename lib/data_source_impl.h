#ifndef INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H
#define INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H

#include <lora_sdr/data_source.h>
#include <lora_sdr/utilities.h>

namespace gr {
namespace lora_sdr {

class data_source_impl : public data_source {
private:
  /**
   * @brief : Count the number of frame sent
   *
   */
  int frame_cnt;
  /**
   * @brief : The maximal number of frame to send
   *
   */
  int m_n_frames;
  /**
   * @brief : The payload length
   *
   */
  int m_pay_len;

  /**
   * @brief : Input data source, if empty random generated data source is used.
   *
   */
  std::string m_string_input;

  /**
   * @brief returns a random string containing [a-z A-Z 0-9] for testing the
   * payload data
   *
   * @param nbytes : the number of char in the string
   * @return std::string : the random generated string
   */
  std::string random_string(int nbytes);

  /**
   * @brief Main function that handles the trigger and dispatches the message
   * making
   *
   * @param msg : PMT input msg (i.e. trigger from strobe)
   */
  void trigg_handler(pmt::pmt_t msg);

public:
  /**
   * @brief Construct a new data source impl object
   *
   * @param pay_len : payload length
   * @param n_frames : number of frames to generate data for
   * @param string_input
   */
  data_source_impl(int pay_len, int n_frames, std::string string_input);
  
  /**
   * @brief Destroy the data source impl object
   * 
   */
  ~data_source_impl();
  
  /**
   * @brief Place holder function of data_source that generated random ([a-z A-Z
   * 0-9]) data source to be sent over the network
   *
   * @param noutput_items
   * @param input_items
   * @param output_items
   * @return int
   */
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
};
} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H */
