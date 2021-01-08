/**
 * @file multi_control.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2021-01-08
 * 
 * @copyright Copyright (c) 2021
 * 
 */

#ifndef INCLUDED_LORA_SDR_MULTI_CONTROL_H
#define INCLUDED_LORA_SDR_MULTI_CONTROL_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * This block is only needed when running lora_sdr in multi streaming mode (aka multiple transmitting chains)
     * This block is intended to ensure all done signals from all the transmitting blocks are gathered and once all transmitting blocks are done,
     * send the done signal to all transmitting blocks, and thus ensuring the entire flowgraph is closed correctly.
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API multi_control : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<multi_control> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::multi_control.
       *
       * To avoid accidental use of raw pointers, lora_sdr::multi_control's
       * constructor is in a private implementation
       * class. lora_sdr::multi_control::make is the public interface for
       * creating new instances.
       */
      static sptr make(int num_ctrl);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_MULTI_CONTROL_H */

