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
  m_bw = bandwidth;
  m_samp_rate = samp_rate;
  m_sf = sf;

  // calculate deducted variables.
  m_number_of_bins = (uint32_t)(1u << m_sf);
  m_samples_per_symbol = (uint32_t)(m_samp_rate * m_number_of_bins / m_bw);

  // resize downchrips
  m_downchirp.resize(m_samples_per_symbol);

  // fft input and outpout variables
  cx_in = new kiss_fft_cpx[m_samples_per_symbol];
  cx_out = new kiss_fft_cpx[m_samples_per_symbol];

  // number of consecutive up chrips a preamble has
  n_up = 8;

  // initialize values of variables
  bin_idx = 0;
  symbol_cnt = 0;
  // set inital state to find preamble
  m_state = FIND_PREAMBLE;
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
  //we need at least the preamble symbols to start working
  ninput_items_required[0] = n_up*m_samples_per_symbol;
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

  //zero value gr_complex
        gr_complex zero = gr_complex(0,0);
    //copy input to memory vector for later use.
  for(int i = 0; i < noutput_items; i++) {
      gr_complex temp = in[i];
      //if input is zero do nut copy onto memory vector (limits memory usage)
      if(temp != zero) {
          mem_vec.push_back(temp);
      }
  }

  consume_each(noutput_items);
  if(m_state == FIND_PREAMBLE) {
      bin_idx_new = get_symbol_val(in, &m_downchirp[0], m_number_of_bins,
                                   m_samples_per_symbol, cx_in, cx_out);
      // calculate difference between this value and previous value
      if ((bin_idx_new - bin_idx) <= 1) {
          // increase the number of symbols counted
          symbol_cnt++;
      }
          // is symbol value are not close to each other start over
      else {
          // set symbol value to be 1
          symbol_cnt = 1;
      }
      int nR_up = (int) (n_up - 1);
      // if we have n_up-1 symbols counted we have found the preamble

      if (symbol_cnt == nR_up) {
          GR_LOG_DEBUG(this->d_logger, "DEBUG:Found preamble!");
          std::cout << symbol_cnt << std::endl;
          std::cout << m_number_of_bins << std::endl;
          std::cout << m_samples_per_symbol << std::endl;
          std::cout << "TEst3" << std::endl;
          int out_i = 0;
          int begin = (int) ((n_up - 1) * m_samples_per_symbol);
          int end = (int) noutput_items;
          int vector_size = mem_vec.size();
          std::cout << begin << std::endl;
          std::cout << end << std::endl;
          m_state = SEND_FRAMES;
          // return noutput_items - ((n_up - 1)*m_samples_per_symbol);
      }
      return 0;
  }
  if(m_state == SEND_FRAMES) {
          //actual sending of samples in split packets
          GR_LOG_DEBUG(this->d_logger, "DEBUG:sending packets!");
      int end_vec = mem_vec.size();
      if (mem_vec.size() > noutput_items) {
          end_vec = noutput_items;
      }
      for (int i = 0; i < end_vec; i++) {
          gr_complex test = mem_vec[i];
          out[i] = mem_vec.at(i);
          std::cout << i << std::endl;
      }
      //clear all vector values
      mem_vec.erase(mem_vec.begin(), mem_vec.begin() + end_vec);
      //check if vector is empty
      if (mem_vec.empty()) {
          m_state = FIND_END_FRAME;
          return noutput_items;
      }
      return noutput_items;
  }
  if(m_state == FIND_END_FRAME) {
      GR_LOG_DEBUG(this->d_logger, "DEBUG:finding end of frame");
      return 0;
  }
  else {
      GR_LOG_WARN(this->d_logger, "WARNING : No state! Shouldn't happen");
      return 0;
  }

  // switch (m_state) {
  // case FIND_PREAMBLE:
  //   // get value of symbol

  //   // m_state = FIND_END_FRAME;
  //   //   break;

  //   // case FIND_END_FRAME: {
  //   //   GR_LOG_DEBUG(this->d_logger, "DEBUG:Going to find end of frame");
  //   //   m_state = FIND_PREAMBLE;
  //   //   break;
  //   // }

  // default: {
  //   GR_LOG_WARN(this->d_logger, "WARNING : No state! Shouldn't happen");
  //   break;
  // }
  // }

  // Do <+signal processing+>
  // Tell runtime system how many input items we consumed on
  // each input stream.
  

  // Tell runtime system how many output items we produced.
  // return noutput_items;
}

} /* namespace lora_sdr */
} /* namespace gr */
