#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "interleaver_impl.h"
#include <gnuradio/lora_sdr/utilities.h>

namespace gr
{
  namespace lora_sdr
  {

    interleaver::sptr
    interleaver::make(uint8_t cr, uint8_t sf, uint8_t ldro, int bw)
    {
      return gnuradio::get_initial_sptr(new interleaver_impl(cr, sf, ldro, bw));
    }

    /*
     * The private constructor
     */
    interleaver_impl::interleaver_impl(uint8_t cr, uint8_t sf, uint8_t ldro, int bw)
        : gr::block("interleaver",
                    gr::io_signature::make(1, 1, sizeof(uint8_t)),
                    gr::io_signature::make(1, 1, sizeof(uint32_t)))
    {
      m_sf = sf;
      m_cr = cr;
      m_bw = bw;
      if (ldro == AUTO){
        m_ldro = (float)(1u<<sf)*1e3/bw > LDRO_MAX_DURATION_MS;
      } 
      else
      {
        m_ldro = ldro;
      }
      ldro_pass = ldro;
      cw_cnt = 0;

      set_tag_propagation_policy(TPP_DONT);
      m_has_config_tag = false;
    }

    void interleaver_impl::set_cr(uint8_t cr){
      m_cr = cr;
    } 

    void interleaver_impl::set_sf(uint8_t sf){
      m_sf = sf;
    } 

    uint8_t interleaver_impl::get_cr(){
      return m_cr;
    } 

    /*
     * Our virtual destructor.
     */
    interleaver_impl::~interleaver_impl()
    {
    }

    void
    interleaver_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = 1;
    }

    void interleaver_impl::update_var(int new_cr, int new_sf, int new_bw, bool ldro_pass)
    {
      if (new_cr != m_cr) {
          m_cr = new_cr;
          // std::cout<<"New cr Interleaver "<< static_cast<int>(m_cr) <<std::endl;
      }
      if (new_sf != m_sf) {
          m_sf = new_sf;
          // std::cout<<"New sf Interleaver "<< static_cast<int>(m_sf) <<std::endl;
      }
      if (new_bw != m_bw) {
          m_bw = new_bw;
          // std::cout<<"New bw Interleaver "<< static_cast<int>(m_bw) <<std::endl;
      }
      if (ldro_pass == AUTO){
        //m_ldro = (float)(1u<<sf)*1e3/bw > LDRO_MAX_DURATION_MS;
        m_ldro = (float)(1u<<m_sf)*1e3/m_bw > LDRO_MAX_DURATION_MS;
      }
      else {
        m_ldro = ldro_pass;
      }
    }

    int
    interleaver_impl::general_work(int noutput_items,
                                   gr_vector_int &ninput_items,
                                   gr_vector_const_void_star &input_items,
                                   gr_vector_void_star &output_items)
    {
      const uint8_t *in = (const uint8_t *)input_items[0];
      uint32_t *out = (uint32_t *)output_items[0];
      int nitems_to_process = ninput_items[0];

      // read tags
      std::vector<tag_t> tags;
      get_tags_in_window(tags, 0, 0, ninput_items[0], pmt::string_to_symbol("frame_len"));
      if (tags.size())
      {
        if (tags[0].offset != nitems_read(0))
          nitems_to_process = tags[0].offset - nitems_read(0);
        else
        {
          if (tags.size() >= 2){
            nitems_to_process = tags[1].offset - tags[0].offset;
          }
          cw_cnt = 0;
          m_frame_len = pmt::to_long(tags[0].value);
          m_framelen_tag =  tags[0];
          get_tags_in_window(tags, 0, 0, 1, pmt::string_to_symbol("configuration"));
          if(tags.size()>0)
          {
            m_has_config_tag = true;
            m_config_tag = tags[0];
            m_config_tag.offset = nitems_written(0); 

            pmt::pmt_t err_cr = pmt::string_to_symbol("error");
            pmt::pmt_t err_sf = pmt::string_to_symbol("error");
            pmt::pmt_t err_bw = pmt::string_to_symbol("error");
            int new_cr = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cr"), err_cr));
            int new_sf = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("sf"), err_sf));
            int new_bw = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("bw"), err_bw));
            update_var(new_cr, new_sf, new_bw, ldro_pass);
          }
          // std::cout<<"update tag"<<std::endl;
          // std::cout<<"Sf Interleaver inside "<< static_cast<int>(m_sf) <<std::endl;
          m_framelen_tag.value = pmt::from_long(8 + std::max((int)std::ceil((double)(m_frame_len - m_sf + 2) / (m_sf-2*m_ldro)) * (m_cr + 4), 0)); //get number of items in frame
          m_framelen_tag.offset = nitems_written(0); 
        }
      }

      

      // nitems_to_process = std::min(nitems_to_process)
      // handle the first interleaved block special case
      uint8_t cw_len = 4 + (((int)cw_cnt < m_sf - 2) ? 4 : m_cr);
      uint8_t sf_app = (((int)cw_cnt < m_sf - 2) ||m_ldro) ? m_sf - 2 : m_sf;

      nitems_to_process = std::min(nitems_to_process,(int)sf_app);
      if(std::floor((float)noutput_items/cw_len)==0)
      {
        return 0;
      }

      if (nitems_to_process >= sf_app || cw_cnt + nitems_to_process == (uint32_t)m_frame_len)
      {        
        //propagate tag
        if(!cw_cnt){
          add_item_tag(0, m_framelen_tag);
          if(m_has_config_tag){
            add_item_tag(0, m_config_tag);
            m_has_config_tag = false;
          }

        }
        //Create the empty matrices
        std::vector<std::vector<bool>> cw_bin(sf_app);
        std::vector<bool> init_bit(m_sf, 0);
        std::vector<std::vector<bool>> inter_bin(cw_len, init_bit);

        //convert to input codewords to binary vector of vector
        for (int i = 0; i < sf_app; i++)
        {
          if (i >= nitems_to_process)//ninput_items[0])
            cw_bin[i] = int2bool(0, cw_len);
          else
            cw_bin[i] = int2bool(in[i], cw_len);
          cw_cnt++;
        }

#ifdef GRLORA_DEBUG
        std::cout << "codewords---- " << std::endl;
        for (uint32_t i = 0u; i < sf_app; i++)
        {
          for (int j = 0; j < int(cw_len); j++)
          {
            std::cout << cw_bin[i][j];
          }
          std::cout << " 0x" << std::hex << (int)in[i] << std::dec << std::endl;
        }
        std::cout << std::endl;
#endif
        //Do the actual interleaving
        for (int32_t i = 0; i < cw_len; i++)
        {
          for (int32_t j = 0; j < int(sf_app); j++)
          {
            inter_bin[i][j] = cw_bin[mod((i - j - 1), sf_app)][i];
          }
          //For the first bloc we add a parity bit and a zero in the end of the lora symbol(reduced rate)
          if (((int)cw_cnt == m_sf - 2)||m_ldro)
            inter_bin[i][sf_app] = accumulate(inter_bin[i].begin(), inter_bin[i].end(), 0) % 2;

          out[i] = bool2int(inter_bin[i]);
        }

#ifdef GRLORA_DEBUG
        std::cout << "interleaved------" << std::endl;
        for (uint32_t i = 0u; i < cw_len; i++)
        {
          for (int j = 0; j < int(m_sf); j++)
          {
            std::cout << inter_bin[i][j];
          }
          std::cout << " " << out[i] << std::endl;
        }
        std::cout << std::endl;
#endif
        consume_each(nitems_to_process > sf_app ? sf_app : nitems_to_process);
        return cw_len;
      }
      else
        return 0;
    }

  } /* namespace lora */
} /* namespace gr */
