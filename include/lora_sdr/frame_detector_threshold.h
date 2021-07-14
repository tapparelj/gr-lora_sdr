/**
 * @file frame_detector_threshold.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief 
 * @version 3
 * @date 2021-03-23
 * 
 * 
 */
#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_THRESHOLD_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_THRESHOLD_H

#include <lora_sdr/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    /*!
     * \brief LoRa frame detector threshold, this block detects a LoRa frames using a preamble detection to find the start of the frame
     * and a SNR energy based detector to detect the end of the frame.
     * If a frame is detected the frame is outputted to the output.
     * 
     * \ingroup lora_sdr
     *
     */
    class LORA_SDR_API frame_detector_threshold : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<frame_detector_threshold> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of lora_sdr::frame_detector_threshold.
       *
       * To avoid accidental use of raw pointers, lora_sdr::frame_detector_threshold's
       * constructor is in a private implementation
       * class. lora_sdr::frame_detector_threshold::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint8_t sf, uint32_t samp_rate, uint32_t bw, float threshold);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_THRESHOLD_H */

