#ifndef INCLUDED_LORA_SDR_RH_RF95_HEADER_IMPL_H
#define INCLUDED_LORA_SDR_RH_RF95_HEADER_IMPL_H

#include <lora_sdr/RH_RF95_header.h>

namespace gr {
  namespace lora_sdr {

    class RH_RF95_header_impl : public RH_RF95_header
    {
     private:
      char m_to;    ///< radiohead specific header field "to"
      char m_from;  ///< radiohead specific header field "from"
      char m_id;    ///< radiohead specific header field "id"
      char m_flags; ///< radiohead specific header field "flags"
      std::vector<uint8_t> m_payload; ///<payload bytes
      void msg_handler(pmt::pmt_t message);


     public:
      RH_RF95_header_impl(uint8_t _to, uint8_t _from, uint8_t _id, uint8_t _flags);
      ~RH_RF95_header_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_RH_RF95_HEADER_IMPL_H */
