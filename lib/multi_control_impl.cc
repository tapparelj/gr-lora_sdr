/**
 * @file multi_control_impl.cc
 * @author your name (you@domain.com)
 * @brief
 * @version 0.1
 * @date 2021-01-08
 *
 * @copyright Copyright (c) 2021
 *
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "multi_control_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

multi_control::sptr multi_control::make(int num_ctrl) {
  return gnuradio::get_initial_sptr(new multi_control_impl(num_ctrl));
}

multi_control_impl::multi_control_impl(int num_ctrl)
    : gr::block("multi_control", gr::io_signature::make(0, 0, 0),
                gr::io_signature::make(0, 0, 0)) {
  m_num_ctrl = num_ctrl;
  m_finished = false;
  m_cur_msg = 0;
  // Generate ports and port msg handler
  std::string ctrl_in, ctrl_out;
  for (int i = 0; i < m_num_ctrl; i++) {
    // generate the input and output ports
    ctrl_in = "ctrl_in" + std::to_string(i);
    ctrl_out = "ctrl_out" + std::to_string(i);
    message_port_register_out(pmt::mp(ctrl_out));
    message_port_register_in(pmt::mp(ctrl_in));
    // set msg handler for the input port to be the ctrl_in_handler
    set_msg_handler(pmt::mp(ctrl_in),
                    [this](pmt::pmt_t msg) { this->ctrl_in_handler(msg); });
  }
}

/**
 * @brief Destroy the multi control impl::multi control impl object
 *
 */
multi_control_impl::~multi_control_impl() {}

void multi_control_impl::ctrl_in_handler(pmt::pmt_t msg) {
  m_cur_msg++;

  std::cout << "Got a work_done" << std::endl;
  std::cout << m_finished << std::endl;
  std::cout << m_cur_msg << std::endl;
  std::cout << m_num_ctrl<< std::endl;

  // If the number of ctrl messages is the same as we need, we can send
  // WORK_DONE to all and stop this thread.
  if (m_cur_msg == m_num_ctrl ) {

    std::string ctrl_out;
    // iterate over all output ports and send done there
    for (int i = 0; i < m_num_ctrl; i++) {
      std::cout << "Publicating work_done" << std::endl;
      ctrl_out = "ctrl_out" + std::to_string(i);
      std::cout << ctrl_out << std::endl;
      message_port_pub(pmt::mp(ctrl_out), d_pmt_done);
    }

    // set internal state to finished, so we can close this thread
    m_finished = true;
  }
}

/**
 * @brief Standard sync block placeholder function
 *
 * @param noutput_items : number output items
 * @param ninput_items_required : number of items required
 */
void multi_control_impl::forecast(int noutput_items,
                                  gr_vector_int &ninput_items_required) {
  /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
}

/**
 * @brief General work function, used to close this block in the end
 *
 * @param noutput_items : number of output items : 0
 * @param ninput_items : number of input items : 0
 * @param input_items : input items (none)
 * @param output_items : output items (none)
 * @return int
 */
int multi_control_impl::general_work(int noutput_items,
                                     gr_vector_int &ninput_items,
                                     gr_vector_const_void_star &input_items,
                                     gr_vector_void_star &output_items) {
  // const <+ITYPE+> *in = (const <+ITYPE+> *) input_items[0];
  // <+OTYPE+> *out = (<+OTYPE+> *) output_items[0];

  // if internal state is done
  if (m_finished == true) {
    // close this thread
    return WORK_DONE;
  } else {
    // return 0
    noutput_items = 0;
    // Tell runtime system how many input items we consumed on
    // each input stream.
    consume_each(noutput_items);

    // Tell runtime system how many output items we produced.
    return noutput_items;
  }
}

} /* namespace lora_sdr */
} /* namespace gr */
