/**
 * @file data_source_sim.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2021-01-05
 * 
 * @copyright Copyright (c) 2021
 * 
 */

#ifndef INCLUDED_LORA_SDR_DATA_SOURCE_SIM_H
#define INCLUDED_LORA_SDR_DATA_SOURCE_SIM_H

#include <lora_sdr/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief Data source that can both generate random strings or static strings, for more information about the implementation visit data_source_impl
     * Main difference from data_source is that this implementation uses an internal uniform distribution, for the timing of the msg pmt channel.
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API data_source_sim : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<data_source_sim> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::data_source.
       *
       * To avoid accidental use of raw pointers, lora_sdr::data_source's
       * constructor is in a private implementation
       * class. lora_sdr::data_source::make is the public interface for
       * creating new instances.
       */
      static sptr make(int pay_len,int n_frames, std::string string_input, uint32_t mean, bool multi_control);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_DATA_SOURCE_H */
