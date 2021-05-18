/**
 * @file data_source_sim_impl.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2021-01-05
 * 
 * @copyright Copyright (c) 2021
 * 
 */
#ifndef INCLUDED_LORA_SDR_DATA_SOURCE_SIM_IMPL_H
#define INCLUDED_LORA_SDR_DATA_SOURCE_SIM_IMPL_H

#include <lora_sdr/data_source_sim.h>
#include "helpers.h"

namespace gr {
namespace lora_sdr {

class data_source_sim_impl : public data_source_sim {
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
   * @brief Variables that holds the mean time of the uniform distribution
   *
   */
  uint32_t m_mean;

  /**
   * @brief : Input data source, if empty random generated data source is used.
   *
   */
  std::string m_string_input;

  /**
   * @brief bollean if we have to control multiple tx chains
   * 
   */
  bool m_multi_control;

  /**
   * @brief 
   * 
   */
  bool m_finished_wait;

  /**
   * @brief internal state variable to tell system 
   * if we have received ctrl_in and should send WORK_DONE to the rest of the blocks.
   * 
   */
  bool m_finished;

  /**
   * @brief 
   * 
   */
  bool m_wait;

  /**
   * @brief 
   * 
   */
  int m_n_send;

  /**
   * @brief returns a random string containing [a-z A-Z 0-9] for testing the
   * payload data
   *
   * @param nbytes : the number of char in the string
   * @return std::string : the random generated string
   */
  std::string random_string(int nbytes);


public:
  /**
   * @brief Construct a new data source impl object
   *
   * @param pay_len : payload length
   * @param n_frames : number of frames to generate data for
   * @param string_input : input string to be used
   * @param mean : Mean time for uniform distribution in ms
   */
  data_source_sim_impl(int pay_len, int n_frames, std::string string_input,
                       uint32_t mean, bool multi_control);

  /**
   * @brief Destroy the data source impl object
   *
   */
  ~data_source_sim_impl();

  /**
   * @brief Place holder function does not do anything for the data source.
   *
   * @param noutput_items
   * @param ninput_items_required
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief Main function, generates random ([a-z A-Z
   * 0-9]) data input to be sent over the network or if input_string set send this over the network.
   * The sim version of the data_source has an internal sleep function set by the parameter mean
   *
   * @param noutput_items : number of output items : 1
   * @param ninput_items : number of input items : 0
   * @param input_items : input item : 0
   * @param output_items : output items :
   * @return int : work status
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_DATA_SOURCE_SIM_IMPL_H */
