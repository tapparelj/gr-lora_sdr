/**
 * @file frame_detector_timeout_impl.cc
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-06-21
 *
 *
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "frame_detector_timeout_impl.h"
#include <gnuradio/expj.h>
#include <gnuradio/io_signature.h>
#include <volk/volk.h>

namespace gr {
namespace lora_sdr {

frame_detector_timeout::sptr frame_detector_timeout::make(uint8_t sf,
                                                          uint32_t samp_rate,
                                                          uint32_t bw,
                                                          uint8_t n_bytes,
                                                          bool detect_second_packet) {
  return gnuradio::get_initial_sptr(
      new frame_detector_timeout_impl(sf, samp_rate, bw, n_bytes, detect_second_packet));
}

/**
 * @brief Construct a new frame detector timeout impl::frame detector timeout
 * impl object
 *
 * @param sf : spreading factor
 * @param samp_rate : sampling rate
 * @param bw : bandwith
 * @param n_bytes : number of bytes
 * @param detect_second_packet : if systems needs to detect second frame inside the window
 */
frame_detector_timeout_impl::frame_detector_timeout_impl(uint8_t sf,
                                                         uint32_t samp_rate,
                                                         uint32_t bw,
                                                         uint8_t n_bytes,
                                                         bool detect_second_packet)
    : gr::block("frame_detector_timeout",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {
  // store input variables
  m_sf = sf;
  m_samp_rate = samp_rate;
  m_bw = bw;
  m_n_bytes = (u_int16_t) n_bytes;
  m_store_n_bytes = m_n_bytes;

  // calculate derived variables number of samples per symbol
  m_N = (uint32_t)(1u << m_sf);
  m_symbols_per_second = (double)m_bw / m_N;
  m_samples_per_symbol = (uint32_t)(m_samp_rate / m_symbols_per_second);

  // initialise all vector values and make sure they have the same length
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

  // initialize values of variables in the frame detector
  bin_idx = 0;
  symbol_cnt = 0;
  m_cnt = 0;
  m_state = FIND_PREAMBLE;
  m_detect_second_packet = detect_second_packet;

  // set buffer reserve
  buffer.reserve(m_N * n_up);
  // set tag propagation
  set_tag_propagation_policy(TPP_ALL_TO_ALL);
}

/**
 * @brief Destroy the frame detector timeout impl::frame detector timeout impl
 * object
 *
 */
frame_detector_timeout_impl::~frame_detector_timeout_impl() {}

/**
 * @brief
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : required input items (how many items must we
 * have for we can do something)
 */
void frame_detector_timeout_impl::forecast(
    int noutput_items, gr_vector_int &ninput_items_required) {
    //frame detector needs at least a sample per symbol to operate
  ninput_items_required[0] = m_samples_per_symbol;
}

/**
 * @brief Get the symbol object value (aka decoded LoRa symbol value)
 *
 * @param input : complex samples
 * @return int32_t : LoRa symbol value
 */
int32_t frame_detector_timeout_impl::get_symbol_val(const gr_complex *input) {
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


int frame_detector_timeout_impl::general_work(
    int noutput_items, gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items, gr_vector_void_star &output_items) {
    //transofrm in and output
  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

    //search for work_done tags and if found add them to the stream
    std::vector<tag_t> work_done_tags;
    get_tags_in_window(work_done_tags, 0, 0, ninput_items[0],
                       pmt::string_to_symbol("work_done"));
    if (work_done_tags.size()) {
        add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
                     pmt::intern("done"), pmt::intern("modulate"));
        consume_each(ninput_items[0]);
        return 1;
    }


  //excute actual logic behind frame detector
  switch (m_state) {

  case FIND_PREAMBLE: {
    // copy input to memory vector for later use.
    for (int i = 0; i < m_samples_per_symbol; i++) {
      buffer.push_back(in[i]);
    }
    // tell scheduler how many items have been used
    consume_each(m_samples_per_symbol);

    // get symbol value of input
    bin_idx_new = get_symbol_val(&in[0]);

    // calculate difference between this value and previous symbol value
    if (std::abs(bin_idx_new - bin_idx) <= 1 && bin_idx_new != -1) {
      // increase the number of symbols counted
      symbol_cnt++;
    } // is symbol value are not close to each other start over
    else {
      // clear the buffer input
      buffer.clear();
      bin_idx = bin_idx_new;
      // set symbol value to be 1
      symbol_cnt = 1;
    }
    // number of preambles needed
    int nR_up = (int)(n_up);
    // if we have n_up symbols counted we have found the preamble
    if (symbol_cnt == nR_up) {
      // store the current power level in m_power
      // set state to be sending LoRa frame packets
      m_state = SEND_PREAMBLE;
      add_item_tag(0, nitems_written(0)+1,
                   pmt::intern("frame"), pmt::intern("start"),
                   pmt::intern("frame_detector_timeout"));
#ifdef GRLORA_DEBUGV
        GR_LOG_DEBUG(this->d_logger, "DEBUG:Done PREAMBLE -> SEND_PREAMBLE");
#endif
      // set symbol count back to zero
      symbol_cnt = 0;
    }
    // return 0 items to the scheduler
    return 0;
  }

  case SEND_PREAMBLE: {
    // send the preamble symbols
    // set the end of the vector to be or the maximum number of items we can
    // output or the maximum of the vector
    int end_vec = buffer.size();
    if (end_vec > noutput_items) {
      end_vec = noutput_items;
    }

    // set output to be the buffer
    for (int i = 0; i < end_vec; i++) {
      out[i] = buffer.at(i);
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

    // if there is enough output buffer to hold a byte
    if (noutput_items > m_samples_per_symbol) {


        if (m_detect_second_packet) {
            //if we need to detect a second packet inside the window.

            // copy input to buffer
            for (int i = 0; i < m_samples_per_symbol; i++) {
                buffer.push_back(in[i]);
            }

            consume_each(m_samples_per_symbol);

            //get symbol value of input
            bin_idx_new = get_symbol_val(&in[0]);

            // calculate difference between this value and previous symbol value
            if (std::abs(bin_idx_new - bin_idx) <= 1 && bin_idx_new != -1) {
                symbol_cnt++;
            }
            else {
                // is symbol value are not close to each other start over
                bin_idx = bin_idx_new;
                // set symbol value to be 1
                symbol_cnt = 1;
            }
            // number of preambles needed
            int nR_up = (int) (n_up);
            if (symbol_cnt == nR_up) {
                // if we have n_up symbols counted we have found the preamble
#ifdef GRLORA_DEBUGV
                GR_LOG_DEBUG(this->d_logger, "DEBUG:Detected second packet inside the timeout window");
                GR_LOG_DEBUG(this->d_logger, "DEBUG:temp:"+std::to_string(m_cnt)+" :"+std::to_string(m_n_bytes)+ ":"+std::to_string(m_store_n_bytes));
#endif
                //offset the number of bytes to be send with new timeout window calculated relative to this point
                m_n_bytes = m_cnt + m_store_n_bytes;
#ifdef GRLORA_DEBUGV
                GR_LOG_DEBUG(this->d_logger, "DEBUG:temp:"+std::to_string(m_cnt)+" :"+std::to_string(m_n_bytes)+ ":"+std::to_string(m_store_n_bytes));
#endif
                //we have found a new preamble, so we know the old pakcet has already ended tag the end and tag the new beginning of the packet
                //create zero to hold the tag propagation
                out[0] = gr_complex(0,0);
                out[1] = gr_complex(0,0);
                add_item_tag(0, nitems_written(0),
                             pmt::intern("frame"), pmt::intern("end"),
                             pmt::intern("frame_detector_timeout"));
                add_item_tag(0, nitems_written(0),
                             pmt::intern("frame"), pmt::intern("start"),
                             pmt::intern("frame_detector_timeout"));
                //reset variables and go to sending the buffer and then return
                symbol_cnt = 0;
                m_state = SEND_PREAMBLE;
                return 2;
            }else {
                //if we did not get an preamble sym
                //get size of buffered input
                int end_vec = buffer.size();

                if (end_vec > n_up*m_samples_per_symbol) {
                    //we have buffered n_pr symbols and did not found a preamble

                    if (m_cnt == m_n_bytes) {
                        //we are at the last part of the
#ifdef GRLORA_DEBUGV
                        GR_LOG_DEBUG(this->d_logger,
                                     "DEBUG:Done SEND_FRAME -> FINDING_PREAMBLE");
                        GR_LOG_DEBUG(this->d_logger, "DEBUG:temp found end of frame:" + std::to_string(m_cnt) + " :" +
                                                     std::to_string(m_n_bytes) + ":" + std::to_string(m_store_n_bytes));
#endif
                        add_item_tag(0, nitems_written(0) + m_samples_per_symbol,
                                     pmt::intern("frame"), pmt::intern("end"),
                                     pmt::intern("frame_detector_timeout"));
                        buffer.clear();
                        m_state = FIND_PREAMBLE;
                        m_cnt = 0;
                        symbol_cnt = 0;
                        m_n_bytes = m_store_n_bytes;
                        //pad byte padding between detected frames (to allow propagation of end tag)
                        consume_each(0);
                        out[0] = gr_complex(0.0, 0.0);
                        return 1;
                    }
                    else {
                        if (end_vec > m_samples_per_symbol) {
                            end_vec = m_samples_per_symbol;
                        }
                        // set output to be the buffer
                        for (int i = 0; i < m_samples_per_symbol; i++) {
                            out[i] = buffer.at(i);
                        }
                        m_cnt++;
                        //clear the items used in the buffer
                        buffer.erase(buffer.begin(), buffer.begin() + end_vec);
                        return m_samples_per_symbol;
                    }

                }
                return 0;

            }

        } else {
            //we do not need to search for extra packet we can processed everything as its streamed in

            //if the output buffer can hold the input
            if (m_cnt == 0) {
                // send over the quarter symbol in the preamble
                consume_each((m_samples_per_symbol / 4));
                memcpy(&out[0], &in[0],
                       sizeof(gr_complex) * (m_samples_per_symbol / 4));
                m_cnt++;
                return (m_samples_per_symbol / 4);
            }
            //if we processed the number of bytes in the timeout window
            if (m_cnt == m_n_bytes) {
#ifdef GRLORA_DEBUGV
                GR_LOG_DEBUG(this->d_logger,
                             "DEBUG:Done SEND_FRAME -> FINDING_PREAMBLE");
                GR_LOG_DEBUG(this->d_logger, "DEBUG:temp found end of frame:" + std::to_string(m_cnt) + " :" +
                                             std::to_string(m_n_bytes) + ":" + std::to_string(m_store_n_bytes));
#endif
                add_item_tag(0, nitems_written(0) + m_samples_per_symbol,
                             pmt::intern("frame"), pmt::intern("end"),
                             pmt::intern("frame_detector_timeout"));
                m_state = FIND_PREAMBLE;
                m_cnt = 0;
                symbol_cnt = 0;
                m_n_bytes = m_store_n_bytes;
                //pad byte padding between detected frames (to allow propagation of end tag)
                consume_each(0);
                out[0] = gr_complex(0.0, 0.0);
                return 1;
            } else {
                // copy input to output
                consume_each(m_samples_per_symbol);
                memcpy(&out[0], &in[0], sizeof(gr_complex) * m_samples_per_symbol);
                // increase the number of symbols transmitted
                m_cnt++;
                return m_samples_per_symbol;
            }
        }
    }else {
        //wait for the output buffer to handle the input
      consume_each(0);
      return 0;
    }
  }
  default: {
    GR_LOG_WARN(this->d_logger, "WARNING : No state! Shouldn't happen");
    consume_each(m_samples_per_symbol);
    return 0;
  }
  }
}

} /* namespace lora_sdr */
} /* namespace gr */
