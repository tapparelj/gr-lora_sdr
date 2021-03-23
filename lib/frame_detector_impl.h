/**
 * @file frame_detector_impl.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief 
 * @version 0.1
 * @date 2021-03-23
 * 
 * 
 */
#ifndef INCLUDED_LORA_SDR_FRAME_DETECTOR_IMPL_H
#define INCLUDED_LORA_SDR_FRAME_DETECTOR_IMPL_H

#include <lora_sdr/frame_detector.h>

namespace gr {
  namespace lora_sdr {

    class frame_detector_impl : public frame_detector
    {
     private:
      // Nothing to declare in this block.

     public:
     /**
      * @brief Construct a new frame detector impl object
      * 
      */
      frame_detector_impl();

      /**
       * @brief Destroy the frame detector impl object
       * 
       */
      ~frame_detector_impl();

      /**
       * @brief 
       * 
       * @param noutput_items : number of output items
       * @param ninput_items_required : required input items (how many items must we have for we can do something)
       */
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      /**
       * @brief General work function. 
       * Main gnuradio function that does the heavy lifting
       * 
       * @param noutput_items : number of output items
       * @param ninput_items : number of input items
       * @param input_items : input items
       * @param output_items : output items
       * @return int 
       */
      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_FRAME_DETECTOR_IMPL_H */

