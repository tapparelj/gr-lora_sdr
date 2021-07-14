/**
 * @file frame_detector_timeout.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief 
 * @version 0.1
 * @date 2021-06-21
 * 
 * 
 */

#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_TIMEOUT_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_TIMEOUT_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief Frame detector block, looks for a LoRa frame given SF, sapling rate and BW.
     Once this block has found the preamble upchirps the block will output n_bytes to its output.
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API frame_detector_timeout : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<frame_detector_timeout> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::frame_detector_timeout.
       *
       * To avoid accidental use of raw pointers, lora_sdr::frame_detector_timeout's
       * constructor is in a private implementation
       * class. lora_sdr::frame_detector_timeout::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t sf, uint32_t samp_rate, uint32_t bw,
                              uint8_t n_bytes);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_TIMEOUT_H */

