#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "modulate_impl.h"

namespace gr
{
    namespace lora_sdr
    {

        modulate::sptr
        modulate::make(uint8_t sf, uint32_t samp_rate, uint32_t bw, std::vector<uint16_t> sync_words, uint32_t frame_zero_padd, uint16_t preamble_len = 8)
        {
            return gnuradio::get_initial_sptr(new modulate_impl(sf, samp_rate, bw, sync_words, frame_zero_padd, preamble_len));
        }
        /*
     * The private constructor
     */
        modulate_impl::modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw, std::vector<uint16_t> sync_words, uint32_t frame_zero_padd, uint16_t preamble_len)
            : gr::block("modulate",
                        gr::io_signature::make(1, 1, sizeof(uint32_t)),
                        gr::io_signature::make(1, 1, sizeof(gr_complex)))
        {
            m_sf = sf;
            m_samp_rate = samp_rate;
            m_bw = bw;
            m_sync_words = sync_words;

            m_number_of_bins = (uint32_t)(1u << m_sf);
            m_os_factor = m_samp_rate / m_bw;
            m_samples_per_symbol = (uint32_t)(m_number_of_bins*m_os_factor);
            m_ninput_items_required = 1;

            m_inter_frame_padding = frame_zero_padd; // add some empty samples at the end of a frame important for transmission with LimeSDR Mini or simulation

            m_downchirp.resize(m_samples_per_symbol);
            m_upchirp.resize(m_samples_per_symbol);

            frame_end = true;

            build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf,m_os_factor);

            //Convert given sync word into the two modulated values in preamble
            if(m_sync_words.size()==1){
                uint16_t tmp = m_sync_words[0];
                m_sync_words.resize(2,0);
                m_sync_words[0] = ((tmp&0xF0)>>4)<<3;
                m_sync_words[1] = (tmp&0x0F)<<3;
            }
            if (preamble_len<5)
            {
               std::cerr<<RED<<" Preamble length should be greater than 5!"<<RESET<<std::endl;
            }
            m_preamb_len = preamble_len;
            samp_cnt = -1;
            preamb_samp_cnt = 0;
            frame_cnt = 0;
            padd_cnt = m_inter_frame_padding;

            set_tag_propagation_policy(TPP_DONT);
            set_output_multiple(m_samples_per_symbol);
        }
        void modulate_impl::set_sf(uint8_t sf){
            m_sf = sf;
            m_number_of_bins = (uint32_t)(1u << m_sf);
            m_os_factor = m_samp_rate / m_bw;
            m_samples_per_symbol = (uint32_t)(m_number_of_bins*m_os_factor);


            m_downchirp.resize(m_samples_per_symbol);
            m_upchirp.resize(m_samples_per_symbol);

            build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf,m_os_factor);
            


        } 

        /*
     * Our virtual destructor.
     */
        modulate_impl::~modulate_impl()
        {
        }

        void
        modulate_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
        {
            ninput_items_required[0] = m_ninput_items_required;
        }

        int modulate_impl::general_work(int noutput_items,
                                        gr_vector_int &ninput_items,
                                        gr_vector_const_void_star &input_items,
                                        gr_vector_void_star &output_items)
        {
            const uint32_t *in = (const uint32_t *)input_items[0];
            gr_complex *out = (gr_complex *)output_items[0];
            int nitems_to_process = ninput_items[0];
            int output_offset = 0;
            // read tags
            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, ninput_items[0], pmt::string_to_symbol("frame_len"));
            if (tags.size())
            {
                if (tags[0].offset != nitems_read(0)){
                    nitems_to_process = std::min(tags[0].offset - nitems_read(0), (uint64_t)(float)noutput_items / m_samples_per_symbol);
                }
                else
                {
                    if (tags.size() >= 2)
                        nitems_to_process = std::min(tags[1].offset - tags[0].offset, (uint64_t)(float)noutput_items / m_samples_per_symbol);
                    if (frame_end)
                    {
                        m_frame_len = pmt::to_long(tags[0].value);
                        tags[0].offset = nitems_written(0);

                        tags[0].value = pmt::from_long(int((m_frame_len + m_preamb_len + 4.25) * m_samples_per_symbol + m_inter_frame_padding ));

                        add_item_tag(0, tags[0]);

                        samp_cnt = -1;
                        preamb_samp_cnt = 0;
                        padd_cnt = 0;
                        frame_end = false;
                    }
                }
            }

            if (samp_cnt == -1) // preamble
            {
                
                for (int i = 0; i < noutput_items / m_samples_per_symbol; i++)
                {
                    if (preamb_samp_cnt < (m_preamb_len + 5)*m_samples_per_symbol) //should output preamble part
                    {
                        if (preamb_samp_cnt < (m_preamb_len*m_samples_per_symbol))
                        { //upchirps
                            memcpy(&out[output_offset], &m_upchirp[0], m_samples_per_symbol * sizeof(gr_complex));
                        }
                        else if (preamb_samp_cnt == (m_preamb_len*m_samples_per_symbol)) //sync words
                            build_upchirp(&out[output_offset], m_sync_words[0], m_sf,m_os_factor);
                        else if (preamb_samp_cnt == (m_preamb_len + 1)*m_samples_per_symbol)
                            build_upchirp(&out[output_offset], m_sync_words[1], m_sf,m_os_factor);
                        else if (preamb_samp_cnt < (m_preamb_len + 4)*m_samples_per_symbol) //2.25 downchirps
                            memcpy(&out[output_offset], &m_downchirp[0], m_samples_per_symbol * sizeof(gr_complex));
                        else if (preamb_samp_cnt == (m_preamb_len + 4)*m_samples_per_symbol)
                        {
                            memcpy(&out[output_offset], &m_downchirp[0], m_samples_per_symbol / 4 * sizeof(gr_complex));
                            //correct offset dur to quarter of downchirp
                            output_offset -= 3 * m_samples_per_symbol / 4;
                            samp_cnt = 0;
                            
                        }
                        output_offset += m_samples_per_symbol;
                        preamb_samp_cnt += m_samples_per_symbol;
                    }
                }
            }
            
            if ( samp_cnt < m_frame_len*m_samples_per_symbol && samp_cnt>-1) //output payload
            {
                nitems_to_process = std::min(nitems_to_process, int((float)(noutput_items - output_offset) / m_samples_per_symbol));
                nitems_to_process = std::min(nitems_to_process, ninput_items[0]);
                for (int i = 0; i < nitems_to_process; i++)
                {
                    build_upchirp(&out[output_offset], in[i], m_sf,m_os_factor);
                    output_offset += m_samples_per_symbol;
                    samp_cnt += m_samples_per_symbol;
                }
            }
            else
            {
                nitems_to_process = 0;
            }

            if ((samp_cnt >= (m_frame_len*m_samples_per_symbol)) && 
                (samp_cnt < m_frame_len*m_samples_per_symbol + m_inter_frame_padding)) //padd frame end with zeros
            {
                m_ninput_items_required = 0;
                int padd_size = std::min(uint32_t(noutput_items - output_offset), m_frame_len*m_samples_per_symbol + m_inter_frame_padding - samp_cnt );
                fill(out+output_offset, out+output_offset+padd_size, gr_complex(0.0, 0.0));
                samp_cnt += padd_size;
                padd_cnt += padd_size;
                output_offset += padd_size;
                // for (int i = 0; i < (noutput_items - output_offset); i++)
                // {
                //     if (samp_cnt < m_frame_len*m_samples_per_symbol + m_inter_frame_padding)
                //     {

                //         out[output_offset + i] = gr_complex(0.0, 0.0);
                //         output_offset += m_samples_per_symbol;
                //         symb_cnt++;
                //         padd_cnt++;
                //     }
                // }
            }
            if ( samp_cnt == m_frame_len*m_samples_per_symbol + m_inter_frame_padding)
            {
                samp_cnt++;
                frame_cnt++;
                m_ninput_items_required = 1;
                frame_end = true;
            
#ifdef GR_LORA_PRINT_INFO              
                std::cout << "Frame " << frame_cnt << " sent\n";
#endif
            }
            // if (nitems_to_process)
            //     std::cout << ninput_items[0] << " " << nitems_to_process << " " << output_offset << " " << noutput_items << std::endl;
            consume_each(nitems_to_process);
            return output_offset;
        }

    } /* namespace lora */
} /* namespace gr */
