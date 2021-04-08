/**
 * @file frame_detector_impl.cc
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
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

    void Temporary_buffer::push_value(gr_complex input) {
        temp_mem_vec.push_back(input);
    }

    int Temporary_buffer::get_size() {
        return temp_mem_vec.size();
    }

    void Temporary_buffer::clear() {
        temp_mem_vec.clear();
    }

    void Temporary_buffer::erase(int end) {
        temp_mem_vec.erase(temp_mem_vec.begin(),temp_mem_vec.begin()+end);
    }

    bool Temporary_buffer::empty() {
        return temp_mem_vec.empty();
    }

    gr_complex Temporary_buffer::get_value(int i) {
        return temp_mem_vec.at(i);
    }

frame_detector::sptr frame_detector::make(float samp_rate, uint32_t bandwidth,
                                          uint8_t sf) {
  return gnuradio::get_initial_sptr(
      new frame_detector_impl(samp_rate, bandwidth, sf));
}

/**
 * @brief Construct a new frame detector impl object
 *
 * @param samp_rate : sampling rate
 * @param bandwidth : bandwith
 * @param sf : spreading factor
 */
frame_detector_impl::frame_detector_impl(float samp_rate, uint32_t bandwidth,
                                         uint8_t sf)
    : gr::block("frame_detector",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {
  // set internal variables
  m_sf = sf;
  m_os_factor = 1;
  m_threshold = 200;
  m_margin = 0;
  m_fft_symb = 4;
  m_mul_out = 4;

  m_N = (uint32_t)(1u << m_sf);
  m_samples_per_symbol = m_N * m_os_factor;

  //  mem_vec.reserve(m_N * m_fft_symb*10);
  // initialise all vector values and make sure they have the same length
  fft_cfg = kiss_fft_alloc(m_N * m_fft_symb, 0, NULL, NULL);
  cx_out.resize(m_N * m_fft_symb, 0.0);
  m_input_downsampled.resize(m_N, 0);
  m_dfts_mag.resize(m_N * m_fft_symb, 0);
  m_dechirped.resize(m_N * m_fft_symb, 0);
  // set downchrip and generate downchirp
  m_downchirp.resize(m_N);
  for (uint n = 0; n < m_N; n++) {
    m_downchirp[n] = gr_expj(-2.0 * M_PI * (pow(n, 2) / (2 * m_N) - 0.5 * n));
  }
  // number of consecutive up chrips a preamble has
  n_up = 8;
  // initialize values of variables
  bin_idx = 0;
  symbol_cnt = 0;
  m_power = 0;
  // set inital state to find preamble
  m_state = FIND_PREAMBLE;

        set_tag_propagation_policy(TPP_ONE_TO_ONE);
}

/**
 * @brief Get the symbol object value (aka decoded LoRa symbol value)
 *
 * @param input : complex samples
 * @return int32_t : LoRa symbol value
 */
int32_t frame_detector_impl::get_symbol(gr_complex *input){
    // dechirp the new potential symbol
    volk_32fc_x2_multiply_32fc(&m_dechirped[(m_fft_symb - 1) * m_N],
                               input, &m_downchirp[0], m_N);
    // do the FFT
    kiss_fft(fft_cfg, (kiss_fft_cpx *)&m_dechirped[0],
             (kiss_fft_cpx *)&cx_out[0]);
    // get abs value of each fft value
    for (int i = 0; i < m_N * m_fft_symb; i++) {
        m_dfts_mag[i] = std::abs(cx_out[i]);
    }
    // get the maximum element from the fft values
    m_max_it = std::max_element(m_dfts_mag.begin(), m_dfts_mag.end());
    int32_t arg_max = std::distance(m_dfts_mag.begin(), m_max_it);
    return arg_max;
}

/**
 * @brief Checks if current samples have the right
 *
 * @param input
 * @return true : we are in a LoRa frame
 * @return false : we are not in a LoRa frame
 */
bool frame_detector_impl::check_in_frame(gr_complex *input){
    //temporary variables
    //current power of frame
    float current_power = 0;
    //compare power to compare against
    float compare_power = 0;
    //get current power
    current_power = frame_detector_impl::calc_power(input);
    //TODO find out how to compare ?
    compare_power = current_power*m_threshold;

    //if current power higher or the current power we are still in a frame
    if(compare_power >= m_power){
        return true;
    }else{
        //we are not inside safe margin of threshold (not in a LoRa frame)
        return false;
    }
}

/**
 * @brief Calculates the LoRa frame peak power
 *
 * @param input : input samples
 * @return float : peak power
 */
float frame_detector_impl::calc_power(gr_complex *input){
    //temporary variables
    //variable to hold the signal power
    float signal_power = 0;
    //number of bins to check around (3 for +-1)
    int n_bin = 3;
    //get maximum argument
    int32_t arg_max = get_symbol(input);
    //calculate power around peak +-1 symbol
    for (int j = -n_bin / 2; j <= n_bin / 2; j++) {
        signal_power  += m_dfts_mag[mod(arg_max + j, m_N * m_fft_symb)];
    }
    //TODO just absolute power or as ratio of noise ?
    //return the maximum power
    return signal_power;
}

/**
 * @brief Set the current LoRa frame power
 *
 * @param input : complex samples
 */
void frame_detector_impl::set_power(gr_complex *input){
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
  ninput_items_required[0] = m_samples_per_symbol* (m_margin + m_fft_symb);
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


  // downsample input (if needed)
  for (int i = 0; i < m_N; i++) {
      m_input_downsampled[i] = in[(int)(m_os_factor - 1 + m_os_factor * i)];
  }

  switch (m_state) {
  case FIND_PREAMBLE: {
#ifdef GRLORA_DEBUG
    GR_LOG_DEBUG(this->d_logger, "DEBUG:Finding preamble");
#endif
    // copy input to memory vector for later use.
    for (int i = 0; i < ninput_items[0]; i++) {
        mem_vec.push_value(m_input_downsampled[i]);
    }
    //calculate symbols to process
    //TODO find out how to stream line this
    int n_symb_to_process =
        std::min(std::floor(ninput_items[0] / m_samples_per_symbol) - m_margin -
                     m_fft_symb + 1,
                 std::floor(noutput_items / m_samples_per_symbol));

      consume_each(m_samples_per_symbol * n_symb_to_process);
    for (int n = 0; n < n_symb_to_process; n++) {
      // down sample the new symbol with a stride of m_os_factor
      for (int i = 0; i < m_N; i++) {
        m_input_downsampled[i] =
            in[(n + m_margin + m_fft_symb - 1) * m_samples_per_symbol +
               m_os_factor * i];
      }
      // shift left
      std::rotate(m_dechirped.begin(), m_dechirped.begin() + m_N,
                  m_dechirped.end());
      //get symbol value of input
      bin_idx_new = get_symbol(&m_input_downsampled[0]);
      // calculate difference between this value and previous symbol value
      if ((bin_idx_new - bin_idx) <= 1) {
        // increase the number of symbols counted
        symbol_cnt++;
      }
      // is symbol value are not close to each other start over
      else {
        // clear memory vector
        mem_vec.clear();
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
        //store the current power level in m_power
        set_power(&m_input_downsampled[0]);
        // set state to be sending LoRa frame packets
        m_state = SEND_FRAMES;
        // set symbol count back to zero
        symbol_cnt = 0;
        break;
      }
    }
    return 0;
  }
  case SEND_FRAMES: {
    // actual sending of samples in split packets (due to gnuradio scheduler)
#ifdef GRLORA_DEBUG
    GR_LOG_DEBUG(this->d_logger, "DEBUG:sending packets!");
#endif
     consume_each(ninput_items[0]);

    //the end of the vector to be eqaul to the vector size (number of elements in vector)
    int end_vec = mem_vec.get_size();
    //if the current vector size is less then number of output items times multiplier
    if (mem_vec.get_size() > m_mul_out*noutput_items) {
        //set the number of elements
      end_vec = m_mul_out*noutput_items;
    }
    //loop over the output vector and set output to the right values
    for (int i = 0; i < end_vec; i++) {
      out[i] = mem_vec.get_value(i);
    }
     //clear all vector values that have been used
      mem_vec.erase(end_vec);

    //check with the current input if we are still in a LoRa frame
    bool in_frame = check_in_frame(&m_input_downsampled[0]);
    //if we are still in a frame
    if(in_frame == true){
        //append input to the memory vector
        for (int i = 0; i < ninput_items[0]; i++) {
            mem_vec.push_value(m_input_downsampled[i]);
        }
    }else{
        //if the memory vector is empty (all stored items have been send)
        if (mem_vec.empty()) {
            //go to finding the preamble
            m_state = FIND_PREAMBLE;
        }
    }
      //return the number of items produced by the system
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