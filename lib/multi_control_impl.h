/**
 * @file multi_control_impl.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-01-08
 *
 * @copyright Copyright (c) 2021
 *
 */

#ifndef INCLUDED_LORA_SDR_MULTI_CONTROL_IMPL_H
#define INCLUDED_LORA_SDR_MULTI_CONTROL_IMPL_H

#include <lora_sdr/multi_control.h>

namespace gr {
namespace lora_sdr {

class multi_control_impl : public multi_control {
private:
  /**
   * @brief Number of control inputs and outputs
   *
   */
  int m_num_ctrl;

  /**
   * @brief Number of triggers from the control input
   * Each trigger is one transmitting chain signalling completion
   * 
   */
  int m_cur_msg;

  /**
   * @brief Internal state variabel to close the thread of this block.
   * 
   */
  bool m_finished;
  
  /**
   * @brief Ctrl input handler, this function will be executed on trigger from the ctrl_in port
   * 
   * @param msg : pmt message (should be d_pmt_done)
   */
  void ctrl_in_handler(pmt::pmt_t msg);

public:
  /**
   * @brief Construct a new multi control impl object
   *
   * @param num_ctrl : number of control in and outputs being handled
   */
  multi_control_impl(int num_ctrl);

  /**
   * @brief Destroy the multi control impl object
   * 
   */
  ~multi_control_impl();

  /**
   * @brief Standard sync block placeholder function
   * 
   * @param noutput_items : number output items
   * @param ninput_items_required : number of items required
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief General work function, used to close this block in the end
   * 
   * @param noutput_items : number of output items : 0 
   * @param ninput_items : number of input items : 0
   * @param input_items : input items (none)
   * @param output_items : output items (none)
   * @return int 
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_MULTI_CONTROL_IMPL_H */
