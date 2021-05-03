/**
 * @file frame_detector.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief 
 * @version 0.1
 * @date 2021-03-23
 * 
 * 
 */
#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief LoRa frame detector, this block detects a LoRa frames using a preamble detection to find the start of the frame
     * and a SNR energy based detector to detect the end of the frame.
     * If a frame is detected the frame is outputted to the output.
     * 
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API frame_detector : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<frame_detector> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::frame_detector.
       *
       * To avoid accidental use of raw pointers, lora_sdr::frame_detector's
       * constructor is in a private implementation
       * class. lora_sdr::frame_detector::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t sf, uint32_t samp_rate, uint32_t bw, uint32_t threshold);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_H */

