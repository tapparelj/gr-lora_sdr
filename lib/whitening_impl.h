

#ifndef INCLUDED_LORA_WHITENING_IMPL_H
#define INCLUDED_LORA_WHITENING_IMPL_H


#include <gnuradio/lora_sdr/whitening.h>
#include <gnuradio/lora_sdr/utilities.h>
namespace gr {
  namespace lora_sdr {

    class whitening_impl : public whitening
    {
     private:
         bool m_is_hex; ///< indicate that the payload is given by a string of hex values
         char m_separator; ///< the separator for file inputs
         std::vector<uint8_t> m_payload; ///< store the payload bytes
         std::vector<std::string> payload_str;
         bool m_file_source; ///< indicate that the payload are provided by a file through an input stream
         void msg_handler(pmt::pmt_t message);
         bool m_use_length_tag;
         std::string m_length_tag_name;
         int m_input_byte_cnt;
         uint64_t m_tag_offset;
         

     public:
      whitening_impl(bool is_hex, bool use_length_tag, char separator, std::string length_tag_name);
      ~whitening_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };
  } // namespace lora
} // namespace gr

#endif /* INCLUDED_LORA_WHITENING_IMPL_H */
