/**
 * @file frame_detector_impl.cc
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.2
 * @date 2021-03-23
 *
 *
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "frame_detector_impl.h"
#include "helpers.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

frame_detector::sptr frame_detector::make(uint8_t sf, uint32_t threshold) {
  return gnuradio::get_initial_sptr(new frame_detector_impl(sf, threshold));
}

/**
 * @brief Construct a new frame detector impl object
 *
 * @param samp_rate : sampling rate
 * @param bandwidth : bandwith
 * @param sf : spreading factor
 */
frame_detector_impl::frame_detector_impl(uint8_t sf, uint32_t threshold)
    : gr::block("frame_detector",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {
  // set internal variables
  // spreading factor
  m_sf = sf;
  // threshold value
  m_threshold = threshold;

  // calculate derived variables
  m_N = (uint32_t)(1u << m_sf);
  m_samples_per_symbol = m_N;

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

  // set buffer reserve
  buffer.reserve(m_N * n_up);

  // initialize values of variables
  bin_idx = 0;
  symbol_cnt = 0;
  m_power = 0;
  // set initial state to find preamble
  m_state = FIND_PREAMBLE;
  // set tag propagation
  set_tag_propagation_policy(TPP_ONE_TO_ONE);
}

/**
 * @brief Get the symbol object value (aka decoded LoRa symbol value)
 *
 * @param input : complex samples
 * @return int32_t : LoRa symbol value
 */
int32_t frame_detector_impl::get_symbol_val(const gr_complex *input) {
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
 * @brief Checks if current samples have the right
 *
 * @param input
 * @return true : we are in a LoRa frame
 * @return false : we are not in a LoRa frame
 */
bool frame_detector_impl::check_in_frame(const gr_complex *input) {
  // temporary variables
  // current power of frame
  float current_power = 0;
  // compare power to compare against
  float compare_power = 0;

  // get current power
  current_power = frame_detector_impl::calc_power(input);
  compare_power = m_power - m_threshold;
  return true;
  // if current power is higher then the set power - threshold we are in the
  // LoRa frame
  if (current_power > compare_power) {
    return true;
  } else {
#ifdef GRLORA_DEBUG
    GR_LOG_DEBUG(this->d_logger, "DEBUG:Outside LoRa frame");
    GR_LOG_DEBUG(this->d_logger,
                 "DEBUG: current power:" + std::to_string(current_power) +
                     "compare power:" + std::to_string(compare_power));
#endif
    // we are not inside safe margin of threshold (not in a LoRa frame)
    return false;
  }
}

/**
 * @brief Calculates the LoRa frame peak power
 *
 * @param input : input samples
 * @return float : peak power
 */
float frame_detector_impl::calc_power(const gr_complex *input) {
  // temporary variables
  // variable to hold the signal power
  float signal_power = 0;
  // number of bins to check around (3 for +-1)
  int n_bin = 3;
  // get maximum argument
  int32_t arg_max = get_symbol_val(input);
  // calculate power around peak +-1 symbol
  for (int j = -n_bin / 2; j <= n_bin / 2; j++) {
    signal_power += std::abs(m_dfts_mag[(arg_max + j)]);
  }

  float peak_power = 0;
  peak_power = signal_power;
  // divide by three to compensate for the +-1 bins
  signal_power = signal_power / 3;

  // loop over the entire dft spectrum and sum the power of all noise
  float noise_level = 0;

  unsigned int alignment = volk_get_alignment();
  float *out = (float *)volk_malloc(sizeof(float), m_N);
  volk_32f_accumulator_s32f(out, &m_dfts_mag[0], m_N);
  // disregard the power of the peak signal and divide by the length
  noise_level = (*out - peak_power) / ((float)(m_N - n_bin));

#ifdef GRLORA_DEBUG
  // calculate snr value
  float snr = 0;
  snr = 10 * log10(signal_power / noise_level);
  GR_LOG_DEBUG(this->d_logger,
               "DEBUG:signal power: " + std::to_string(signal_power));
  GR_LOG_DEBUG(this->d_logger, "DEBUG:noise: " + std::to_string(noise_level));
  GR_LOG_DEBUG(this->d_logger, "DEBUG:snr: " + std::to_string(snr));
#endif

  if (noise_level > 1) {
    signal_power = signal_power / noise_level;
  } else {
    signal_power = signal_power / 2;
  }

  volk_free(out);
  return signal_power;
}

/**
 * @brief Set the current LoRa frame power
 *
 * @param input : complex samples
 */
void frame_detector_impl::set_power(const gr_complex *input) {
  m_power = calc_power(input);
}

/**
 * @brief Destroy the frame detector impl::frame detector impl object
 *
 */
frame_detector_impl::~frame_detector_impl() {}

/**
 * @brief
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : required input items (how many items must we
 * have for we can do something)
 */
void frame_detector_impl::forecast(int noutput_items,
                                   gr_vector_int &ninput_items_required) {
  /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
  // we need at least the preamble symbols to start working
  ninput_items_required[0] = m_samples_per_symbol + 2;
}

/**
 * @brief General work function.
 * Main gnuradio function that does the heavy lifting
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input items
 * @param output_items : output items
 * @return int
 */
int frame_detector_impl::general_work(int noutput_items,
                                      gr_vector_int &ninput_items,
                                      gr_vector_const_void_star &input_items,
                                      gr_vector_void_star &output_items) {
  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

  // search for work_done tags and if found add them to the stream
  std::vector<tag_t> work_done_tags;
  get_tags_in_window(work_done_tags, 0, 0, ninput_items[0],
                     pmt::string_to_symbol("work_done"));
  if (work_done_tags.size()) {
    add_item_tag(0, nitems_written(0), pmt::intern("work_done"),
                 pmt::intern("done"), pmt::intern("frame_detector"));
    consume_each(ninput_items[0]);
    return 1;
  }

  switch (m_state) {
  case FIND_PREAMBLE: {
#ifdef GRLORA_DEBUG
    GR_LOG_DEBUG(this->d_logger, "DEBUG:Finding preamble");
#endif
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
      // set symbol value to be 1
      symbol_cnt = 1;
    }
    // number of preambles needed
    int nR_up = (int)(n_up - 1);
    // if we have n_up-1 symbols counted we have found the preamble
    if (symbol_cnt == nR_up) {
#ifdef GRLORA_DEBUG
      GR_LOG_DEBUG(this->d_logger, "DEBUG:Found preamble!");
#endif
      // store the current power level in m_power
      set_power(&in[0]);
      // set state to be sending LoRa frame packets
      m_state = SEND_FRAMES;
      // set symbol count back to zero
      symbol_cnt = 0;
      break;
    }
    return 0;
  }
  case SEND_FRAMES: {
    // actual sending of samples in split packets (due to gnuradio scheduler)

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
    }

    // clear used items from buffer
    buffer.erase(buffer.begin(), buffer.begin() + end_vec);

    // check the first symbol of the input is we are still in a LoRa frame
    bool in_frame = check_in_frame(&in[0]);

    // if we are still in a frame
    if (in_frame == true) {
      // append input to the buffer
      for (int i = 0; i < ninput_items[0]; i++) {
        buffer.push_back(in[i]);
      }
    } else {
      // if the buffer is empty (all stored items have been send)
      if (buffer.empty()) {
        // go to finding the preamble
        m_state = FIND_PREAMBLE;
      }
    }
    // tell the gnuradio scheduler how many items we have used.
    consume_each(ninput_items[0]);
    // return the number of items produced by the system
    return end_vec;
  }

  default: {
    GR_LOG_WARN(this->d_logger, "WARNING : No state! Shouldn't happen");
    return 0;
  }
  }
}

} /* namespace lora_sdr */
} /* namespace gr */