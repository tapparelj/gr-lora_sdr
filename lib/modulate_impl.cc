#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "modulate_impl.h"

namespace gr {
namespace lora_sdr {

modulate::sptr modulate::make(uint8_t sf, uint32_t samp_rate, uint32_t bw,
                              std::vector<uint16_t> sync_words,
                              bool create_zeros) {
  return gnuradio::get_initial_sptr(
      new modulate_impl(sf, samp_rate, bw, sync_words, create_zeros));
}

/**
 * @brief Construct a new modulate impl::modulate impl object
 *
 * @param sf
 * @param samp_rate
 * @param bw
 * @param sync_words
 * @param create_zeros
 */
modulate_impl::modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw,
                             std::vector<uint16_t> sync_words,
                             bool create_zeros)
    : gr::block("modulate", gr::io_signature::make(1, 1, sizeof(uint32_t)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {
  m_sf = sf;
  m_samp_rate = samp_rate;
  m_bw = bw;
  m_sync_words = sync_words;

  m_number_of_bins = (uint32_t)(1u << m_sf);
  m_symbols_per_second = (double)m_bw / m_number_of_bins;
  m_samples_per_symbol = (uint32_t)(m_samp_rate / m_symbols_per_second);

  m_inter_frame_padding = 40; // add 4 empty symbols at the end of a frame

  m_downchirp.resize(m_samples_per_symbol);
  m_upchirp.resize(m_samples_per_symbol);

  build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

  n_up = 8;
  symb_cnt = 0;
  preamb_symb_cnt = 0;
  padd_cnt = m_inter_frame_padding;

  set_tag_propagation_policy(TPP_DONT);
  set_output_multiple(m_number_of_bins);
}

/**
 * @brief Destroy the modulate impl::modulate impl object
 *
 */
modulate_impl::~modulate_impl() {}

/**
 * @brief 
 * 
 * @param noutput_items 
 * @param ninput_items_required 
 */
void modulate_impl::forecast(int noutput_items,
                             gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 1;
}

/**
 * @brief Main function where all the processing happens
 * 
 * @param noutput_items 
 * @param ninput_items 
 * @param input_items 
 * @param output_items 
 * @return int 
 */
int modulate_impl::general_work(int noutput_items, gr_vector_int &ninput_items,
                                gr_vector_const_void_star &input_items,
                                gr_vector_void_star &output_items) {
  const uint32_t *in = (const uint32_t *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];
  int nitems_to_process = ninput_items[0];
  int output_offset = 0;

  //search for work_done tags and if found add them to the stream
  std::vector<tag_t> work_done_tags;
  get_tags_in_window(work_done_tags, 0, 0, ninput_items[0],
                     pmt::string_to_symbol("work_done"));
  if (work_done_tags.size()) {
    add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
                 pmt::intern("done"), pmt::intern("modulate"));
    return 1;
  }

  // read tags
  std::vector<tag_t> tags;

  get_tags_in_window(tags, 0, 0, ninput_items[0],
                     pmt::string_to_symbol("frame_len"));
  if (tags.size()) {
    if (tags[0].offset != nitems_read(0))
      nitems_to_process =
          std::min(tags[0].offset - nitems_read(0),
                   (uint64_t)(float)noutput_items / m_samples_per_symbol);
    else {
      if (tags.size() >= 2)
        nitems_to_process =
            std::min(tags[1].offset - tags[0].offset,
                     (uint64_t)(float)noutput_items / m_samples_per_symbol);
      if (nitems_to_process && padd_cnt == m_inter_frame_padding) {
        m_frame_len = pmt::to_long(tags[0].value);
        tags[0].offset = nitems_written(0);

        tags[0].value = pmt::from_long(
            int((m_frame_len + m_inter_frame_padding + n_up + 4.25) *
                m_samples_per_symbol));

//        add_item_tag(0, tags[0]);

        symb_cnt = 0;
        preamb_symb_cnt = 0;
        padd_cnt = 0;
      }
    }
  }

  if (!symb_cnt) // in preamble
  {
    for (int i = 0; i < noutput_items / m_samples_per_symbol; i++) {
      if (preamb_symb_cnt < n_up + 5) // should output preamble part
      {
          if(preamb_symb_cnt == 1) {
              //tag the beginning of a new frame
              add_item_tag(0, nitems_written(0), pmt::intern("frame"),
                           pmt::intern("start"), pmt::intern("modulate"));
          }
        if (preamb_symb_cnt < n_up) { // upchirps
          memcpy(&out[output_offset], &m_upchirp[0],
                 m_samples_per_symbol * sizeof(gr_complex));
        } else if (preamb_symb_cnt == n_up) // sync words
          build_upchirp(&out[output_offset], m_sync_words[0], m_sf);
        else if (preamb_symb_cnt == n_up + 1)
          build_upchirp(&out[output_offset], m_sync_words[1], m_sf);

        else if (preamb_symb_cnt < n_up + 4) // 2.25 downchirps
          memcpy(&out[output_offset], &m_downchirp[0],
                 m_samples_per_symbol * sizeof(gr_complex));
        else if (preamb_symb_cnt == n_up + 4) {
          memcpy(&out[output_offset], &m_downchirp[0],
                 m_samples_per_symbol / 4 * sizeof(gr_complex));
          // correct offset dur to quarter of downchirp
          output_offset -= 3 * m_samples_per_symbol / 4;
        }
        output_offset += m_samples_per_symbol;
        preamb_symb_cnt++;
      }
    }
  }

  if (symb_cnt < m_frame_len && preamb_symb_cnt == n_up + 5) // output payload
  {
    nitems_to_process =
        std::min(nitems_to_process, int((float)(noutput_items - output_offset) /
                                        m_samples_per_symbol));
    nitems_to_process = std::min(nitems_to_process, ninput_items[0]);
    for (int i = 0; i < nitems_to_process; i++) {
      build_upchirp(&out[output_offset], in[i], m_sf);
      output_offset += m_samples_per_symbol;
      symb_cnt++;
    }
      consume_each(nitems_to_process);
      return output_offset;
  } else {
    nitems_to_process = 0;
  }
  if(symb_cnt == m_frame_len){
      //tag the end of a frame
      add_item_tag(0, nitems_written(0), pmt::intern("frame"),
                   pmt::intern("end"), pmt::intern("modulate"));
  }

  if (symb_cnt >= m_frame_len) // padd frame end with zeros
  {
    for (int i = 0; i < (noutput_items - output_offset) / m_samples_per_symbol;
         i++) {
              if (symb_cnt >= m_frame_len &&
                  symb_cnt < m_frame_len + m_inter_frame_padding) {
                    for (int i = 0; i < m_samples_per_symbol; i++) {
                      out[output_offset + i] = gr_complex(0.0, 0.0);
                    }
                    output_offset += m_samples_per_symbol;
                    symb_cnt++;
                    padd_cnt++;
              }
    }
  }
//  std::cout << symb_cnt << std::endl;
//        test += (output_offset/((float)m_samples_per_symbol));
//        std::cout << test << std::endl;
  consume_each(nitems_to_process);
  return output_offset;
}

} // namespace lora_sdr
} /* namespace gr */
