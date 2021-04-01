#ifndef INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H
#define INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H

#include <lora_sdr/data_source.h>
#include <lora_sdr/utilities.h>

namespace gr {
  namespace lora_sdr {

    class data_source_impl : public data_source
    {
     private:
         int frame_cnt; ///< count the number of frame sent
         int m_n_frames;///< The maximal number of frame to send
         int m_pay_len; ///< The payload length

         /**
          *  \brief  return a random string containing [a-z A-Z 0-9]
          *
          *  \param  nbytes
          *          The number of char in the string
          */
         std::string random_string(int nbytes);
         /**
          *  \brief  Handles trigger messages
          */
         void trigg_handler(pmt::pmt_t id);

     public:
      data_source_impl(int pay_len,int n_frames);
      ~data_source_impl();

      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };
  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_DATA_SOURCE_IMPL_H */
