#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "hamming_enc_impl.h"
#include <gnuradio/lora_sdr/utilities.h>

namespace gr
{
  namespace lora_sdr
  {

    hamming_enc::sptr
    hamming_enc::make(uint8_t cr, uint8_t sf)
    {
      return gnuradio::get_initial_sptr(new hamming_enc_impl(cr, sf));
    }

    /*
     * The private constructor
     */
    hamming_enc_impl::hamming_enc_impl(uint8_t cr, uint8_t sf)
        : gr::sync_block("hamming_enc",
                         gr::io_signature::make(1, 1, sizeof(uint8_t)),
                         gr::io_signature::make(1, 1, sizeof(uint8_t)))
    {
      m_cr = cr;
      m_sf = sf;
      set_tag_propagation_policy(TPP_ONE_TO_ONE);
    }


        void hamming_enc_impl::set_cr(uint8_t cr){
            m_cr = cr;
        } 

      void hamming_enc_impl::set_sf(uint8_t sf){
          m_sf = sf;
      } 

        uint8_t hamming_enc_impl::get_cr(){
            return m_cr;
        } 


    /*
     * Our virtual destructor.
     */
    hamming_enc_impl::~hamming_enc_impl()
    {
    }

    int
    hamming_enc_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items)
    {
      const uint8_t *in_data = (const uint8_t *)input_items[0];
      uint8_t *out = (uint8_t *)output_items[0];

      int nitems_to_process = noutput_items;

      // read tags
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, noutput_items, pmt::string_to_symbol("frame_len"));
      if (tags.size())
      {
        if (tags[0].offset != nitems_read(0))
          nitems_to_process = tags[0].offset - nitems_read(0);
        else
        {
          if (tags.size() >= 2)
            nitems_to_process = tags[1].offset - tags[0].offset;
          m_cnt = 0;
        }
      }


      std::vector<bool> data_bin;
      bool p0, p1, p2, p3, p4;
      for (int i = 0; i < nitems_to_process; i++)
      {
#ifdef GRLORA_DEBUG
        std::cout << std::hex << (int)in_data[i] << "   ";
#endif
        uint8_t cr_app = (m_cnt < m_sf - 2) ? 4 : m_cr;
        data_bin = int2bool(in_data[i], 4);

        //the data_bin is msb first
        if (cr_app != 1)
        { //need hamming parity bits
          p0 = data_bin[3] ^ data_bin[2] ^ data_bin[1];
          p1 = data_bin[2] ^ data_bin[1] ^ data_bin[0];
          p2 = data_bin[3] ^ data_bin[2] ^ data_bin[0];
          p3 = data_bin[3] ^ data_bin[1] ^ data_bin[0];
          //we put the data LSB first and append the parity bits
          out[i] = (data_bin[3] << 7 | data_bin[2] << 6 | data_bin[1] << 5 | data_bin[0] << 4 | p0 << 3 | p1 << 2 | p2 << 1 | p3) >> (4 - cr_app);
        }
        else
        { // coding rate = 4/5 we add a parity bit
          p4 = data_bin[0] ^ data_bin[1] ^ data_bin[2] ^ data_bin[3];
          out[i] = (data_bin[3] << 4 | data_bin[2] << 3 | data_bin[1] << 2 | data_bin[0] << 1 | p4);
        }
#ifdef GRLORA_DEBUG
        std::cout << std::hex << (int)out[i] << std::dec << std::endl;
#endif
        m_cnt++;
      }

      return nitems_to_process;
    }

  } /* namespace lora */
} /* namespace gr */
