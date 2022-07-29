#ifndef INCLUDED_LORA_ADD_CRC_IMPL_H
#define INCLUDED_LORA_ADD_CRC_IMPL_H


#include <gnuradio/lora_sdr/add_crc.h>
#include <gnuradio/lora_sdr/utilities.h>
namespace gr {
  namespace lora_sdr {

    class add_crc_impl : public add_crc
    {
     private:
        bool m_has_crc; ///<indicate the presence of a payload CRC
        std::vector<uint8_t> m_payload; ///< payload data
        uint8_t m_payload_len; ///< length of the payload in Bytes
        int m_frame_len; ///< length of the frame in number of gnuradio items
        int m_cnt; ///< counter of the number of symbol in frame

        unsigned int crc16(unsigned int crcValue, unsigned char newByte);

     public:
      add_crc_impl(bool has_crc);
      ~add_crc_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_ADD_CRC_IMPL_H */
