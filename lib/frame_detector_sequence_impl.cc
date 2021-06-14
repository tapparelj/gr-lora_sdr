/**
 * @file frame_detector_sequence_impl.cc
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-06-14
 *
 *
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "frame_detector_sequence_impl.h"
#include "helpers.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

frame_detector_sequence::sptr frame_detector_sequence::make(uint8_t sf,
                                                            uint32_t samp_rate,
                                                            uint32_t bw,
                                                            uint8_t n_seq) {
  return gnuradio::get_initial_sptr(
      new frame_detector_sequence_impl(sf, samp_rate, bw, n_seq));
}

/**
 * @brief Construct a new frame detector sequence impl object
 *
 * @param sf : spreading factor
 * @param samp_rate : sampling rate
 * @param bw : bandwith
 * @param n_seq : number of consecitive symbols for the end
 */
frame_detector_sequence_impl::frame_detector_sequence_impl(uint8_t sf,
                                                           uint32_t samp_rate,
                                                           uint32_t bw,
                                                           uint8_t n_seq)
    : gr::block("frame_detector_sequence",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {

  gr::block::set_thread_priority(90);
  // set internal variables
  // spreading factor
  m_sf = sf;
  m_samp_rate = samp_rate;
  m_bw = bw;
  // calculate derived variables number of samples per symbol
  m_N = (uint32_t)(1u << m_sf);
  m_symbols_per_second = (double)m_bw / m_N;
  m_samples_per_symbol = (uint32_t)(m_samp_rate / m_symbols_per_second);

  // initialise all vector values and make sure they have the same length and
  // are initialized
  fft_cfg = kiss_fft_alloc(m_N, 0, NULL, NULL);
  cx_out.resize(m_N, 0.0);
  m_dfts_mag.resize(m_N, 0);
  m_dechirped.resize(m_N, 0);

  // set downchirp and generate downchirp
  m_downchirp.resize(m_N);
  for (uint n = 0; n < m_N; n++) {
    m_downchirp[n] = gr_expj(-2.0 * M_PI * (pow(n, 2) / (2 * m_N) - 0.5 * n));
  }
  // number of consecutive up chrips a preamble has
  n_up = 8;

  // set buffer reserve
  buffer.reserve(m_N * n_up);

  // initialize values of variables
  bin_idx = 2;
  symbol_cnt = 0;
  m_state = FIND_PREAMBLE;

  // set tag propagation
  set_tag_propagation_policy(TPP_ONE_TO_ONE);
}

/**
 * @brief Destroy the frame detector sequence impl object
 *
 */
frame_detector_sequence_impl::~frame_detector_sequence_impl() {}

/**
 * @brief Get the symbol object value (aka decoded LoRa symbol value)
 *
 * @param input : complex samples
 * @return int32_t : LoRa symbol value
 */
int32_t frame_detector_sequence_impl::get_symbol_val(const gr_complex *input) {
  // dechirp the new potential symbol
  volk_32fc_x2_multiply_32fc(&m_dechirped[0], input, &m_downchirp[0], m_N);
  // do the FFT
  kiss_fft(fft_cfg, (kiss_fft_cpx *)&m_dechirped[0],
           (kiss_fft_cpx *)&cx_out[0]);
  // get abs value of each fft value
  for (int i = 0; i < m_N; i++) {
    m_dfts_mag[i] = std::abs(cx_out[i]);
  }
  // get the maximum element from the fft values
  m_max_it = std::max_element(m_dfts_mag.begin(), m_dfts_mag.end());
  int32_t arg_max = std::distance(m_dfts_mag.begin(), m_max_it);
  // return the maximum dft bin containing the LoRa symbol
  return arg_max;
}

/**
 * @brief Function to tell scheduler how many items we need
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of required input itens
 */
void frame_detector_sequence_impl::forecast(
    int noutput_items, gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = m_samples_per_symbol;
}

/**
 * @brief General function where all the stuff happens
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input items
 * @param output_items : output items
 * @return int
 */
int frame_detector_sequence_impl::general_work(
    int noutput_items, gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items, gr_vector_void_star &output_items) {
  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

  //        // search for work_done tags and if found add them to the stream
  //        std::vector<tag_t> work_done_tags;
  //        get_tags_in_window(work_done_tags, 0, 0, ninput_items[0],
  //                           pmt::string_to_symbol("work_done"));
  //        if (work_done_tags.size()) {
  //            add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
  //                         pmt::intern("done"),
  //                         pmt::intern("frame_detector_threshold"));
  //            consume_each(ninput_items[0]);
  //            return 1;
  //        }

  switch (m_state) {
  case FIND_PREAMBLE: {
    // copy input to memory vector for later use.
    for (int i = 0; i < m_N; i++) {
      buffer.push_back(in[i]);
    }
    // tell scheduler how many items have been used
    consume_each(m_N);

    // get symbol value of input
    bin_idx_new = get_symbol_val(&in[0]);

    // calculate difference between this value and previous symbol value
    if ((bin_idx_new - bin_idx) <= 1) {
      // increase the number of symbols counted
      symbol_cnt++;
    }
    // is symbol value are not close to each other start over
    else {
      // clear memory vector
      buffer.clear();
      bin_idx = bin_idx_new;
      // set symbol value to be 1
      symbol_cnt = 1;
    }
    // number of preambles needed
    int nR_up = (int)(n_up - 1);
    // if we have n_up-1 symbols counted we have found the preamble
    if (symbol_cnt == nR_up) {
#ifdef GRLORA_DEBUGV
      GR_LOG_DEBUG(this->d_logger, "DEBUG:Found PREAMBLE -> SEND PREAMBLE!");
#endif
#ifdef GRLORA_SIM
      // find the frame info tag
      get_tags_in_range(m_tags_vector, 0, nitems_written(0),
                        nitems_read(0) + m_samples_per_symbol,
                        pmt::string_to_symbol("frame"));
      if (m_tags_vector.size()) {
        if (pmt::symbol_to_string(m_tags_vector[0].value) == "start") {
#ifdef GRLORA_DEBUGV
          GR_LOG_DEBUG(this->d_logger,
                       "DEBUG:Found correct beginning tag at offset:" +
                           std::to_string(m_tags_vector[0].offset));
#endif
          m_detected_tag_begin = true;
        }
      }
#endif
      // set state to be sending LoRa frame packets
      m_state = SEND_PREAMBLE;
#ifdef GRLORA_DEBUGV
      GR_LOG_DEBUG(this->d_logger, "DEBUG:Tagging start of frame at :" +
                                       std::to_string(nitems_written(0)));
      GR_LOG_DEBUG(this->d_logger,
                   "DEBUG:set power at:" + std::to_string(m_power));
#endif
      //      add_item_tag(0, nitems_written(0), pmt::intern("frame"),
      //                   pmt::intern("start"),
      //                   pmt::intern("frame_detector_threshold"));

      // set symbol count back to zero
      symbol_cnt = 0;
      return 0;
      break;
    }
    return 0;
  }
  case SEND_PREAMBLE: {
    // send the preamble symbols
#ifdef GRLORA_DEBUGV
    GR_LOG_DEBUG(this->d_logger, "DEBUG:Starting sending preamble");
#endif
    // set the end of the vector to be or the maximum number of items we can
    // output or the maximum of the vector
    int end_vec = buffer.size();
    if (end_vec > noutput_items) {
      end_vec = noutput_items;
    }

    // set output to be the buffer
    // TODO could maybe use memcpy for speed
    for (int i = 0; i < end_vec; i++) {
      out[i] = buffer.at(i);
#ifdef GRLORA_log
      output_log_after << out[i] << std::endl;
#endif
    }

    // clear used items from buffer
    buffer.erase(buffer.begin(), buffer.begin() + end_vec);
    if (buffer.empty()) {
      // go to sending the rest of the symbols
      m_state = SEND_FRAME;
#ifdef GRLORA_DEBUGV
      GR_LOG_DEBUG(this->d_logger, "DEBUG:Done SEND_PREAMBLE -> SEND_FRAME");
#endif
    }
    // tell the gnuradio scheduler how many items we have used.
    consume_each(0);
    // return the number of items produced by the system
    return end_vec;
  }

  case SEND_FRAME: {
    // Computing power of input and checking if this is below the preamble power
    // - threshold

    if (noutput_items < m_samples_per_symbol) {
      consume_each(0);
      return 0;
    }

//    if (m_cnt < 10) {
//      // after we have found the preamble there are 5 symbols containing the
//      // network identifiers and
//      // downchrips we skip these in calculation because they make
//      // life/computations hard and are always there in the frame
//      in_frame = true;
//    } else {
//      // if we are past the symbols containing network and downchirps
//      // check if we are still in the frame
//      in_frame = check_in_frame(&in[0]);
//    }
//    // increment proceed symbol counter
//    m_cnt++;
//    // tell the gnuradio scheduler how many items we have used.
//    // if we are still in a frame
//    if (in_frame == true) {
//      consume_each(m_samples_per_symbol);
//
//      // copy input to output
//      memcpy(&out[0], &in[0], sizeof(gr_complex) * m_samples_per_symbol);
//      // return the number of items produced by the system
//      return m_samples_per_symbol;
//    } else {
//      consume_each(0);
//#ifdef GRLORA_SIM
//      if (nitems_read(0) >= m_end_offset) {
//#ifdef GRLORA_DEBUGV
//        GR_LOG_DEBUG(this->d_logger,
//                     "DEBUG:Correct end tag:" +
//                         std::to_string(m_tags_vector[0].offset));
//#endif
//        m_detected_tag_end = true;
//      }
//#endif
//
//#ifdef GRLORA_DEBUGV
//      GR_LOG_DEBUG(this->d_logger, "DEBUG:Done SEND_FRAME -> SEND_END_FRAME");
//#endif

      // we consume items but do not output any items (if its outside the frame)
      // return the number of items produced by the system
      return 0;
    }
      default: {
          GR_LOG_WARN(this->d_logger, "WARNING : No state! Shouldn't happen");
          return 0;
      }
  }

}

} /* namespace lora_sdr */
} /* namespace gr */
