#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "fft_demod_impl.h"
#include <gnuradio/io_signature.h>
extern "C" {
#include "kiss_fft.h"
}

namespace gr {
namespace lora_sdr {

fft_demod::sptr fft_demod::make(float samp_rate, uint32_t bandwidth, uint8_t sf,
                                bool impl_head) {
  return gnuradio::get_initial_sptr(
      new fft_demod_impl(samp_rate, bandwidth, sf, impl_head));
}

/**
 * @brief Construct a new fft demod impl object
 *
 * @param samp_rate : sampling rate
 * @param bandwidth : bandwith
 * @param sf : spreading factor
 * @param impl_head : impl_head mode
 */
fft_demod_impl::fft_demod_impl(float samp_rate, uint32_t bandwidth, uint8_t sf,
                               bool impl_head)
    : gr::block("fft_demod",
                gr::io_signature::make(1, 1, (1u << sf) * sizeof(gr_complex)),
                gr::io_signature::make(0, 1, sizeof(uint32_t))) {
  m_bw = bandwidth;
  m_samp_rate = samp_rate;
  m_sf = sf;

  m_number_of_bins = (uint32_t)(1u << m_sf);
  m_samples_per_symbol = (uint32_t)(m_samp_rate * m_number_of_bins / m_bw);
  m_upchirp.resize(m_samples_per_symbol);
  m_downchirp.resize(m_samples_per_symbol);

  // FFT demodulation preparations
  m_fft.resize(m_samples_per_symbol);
  m_dechirped.resize(m_samples_per_symbol);

  set_tag_propagation_policy(TPP_DONT);

#ifdef GRLORA_MEASUREMENTS
  int num = 0; // check next file name to use
  while (1) {
    std::ifstream infile("../../matlab/measurements/energy" +
                         std::to_string(num) + ".txt");
    if (!infile.good())
      break;
    num++;
  }
  energy_file.open("../../matlab/measurements/energy" + std::to_string(num) +
                       ".txt",
                   std::ios::out | std::ios::trunc);
#endif
#ifdef GRLORA_DEBUG
  idx_file.open("../../idx.txt", std::ios::out | std::ios::trunc);
#endif
}

/**
 * @brief Destroy the fft demod impl object
 *
 */
fft_demod_impl::~fft_demod_impl() {}

/**
 * @brief Standard gnuradio function to tell the system how many input and
 * output items are needed.
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of output items required
 */
void fft_demod_impl::forecast(int noutput_items,
                              gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 1;
}

/**
 * @brief Recover the lora symbol value using argmax of the dechirped symbol
 * FFT.
 *
 * @param samples The pointer to the symbol beginning.
 * @return int32_t
 */
int32_t fft_demod_impl::get_symbol_val(const gr_complex *samples) {
  float m_fft_mag[m_number_of_bins];
  float rec_en = 0;
  kiss_fft_cfg cfg = kiss_fft_alloc(m_samples_per_symbol, 0, 0, 0);
  kiss_fft_cpx *cx_in = new kiss_fft_cpx[m_samples_per_symbol];
  kiss_fft_cpx *cx_out = new kiss_fft_cpx[m_samples_per_symbol];

  // Multiply with ideal downchirp
  volk_32fc_x2_multiply_32fc(&m_dechirped[0], samples, &m_downchirp[0],
                             m_samples_per_symbol);
  for (int i = 0; i < m_samples_per_symbol; i++) {
    cx_in[i].r = m_dechirped[i].real();
    cx_in[i].i = m_dechirped[i].imag();
  }
  // do the FFT
  kiss_fft(cfg, cx_in, cx_out);
  // Get magnitude
  for (uint32_t i = 0u; i < m_number_of_bins; i++) {
    m_fft_mag[i] = cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i;
    rec_en += m_fft_mag[i];
  }

  free(cfg);
  delete[] cx_in;
  delete[] cx_out;
  // Return argmax

  int idx =
      std::max_element(m_fft_mag, m_fft_mag + m_number_of_bins) - m_fft_mag;
#ifdef GRLORA_MEASUREMENTS
  energy_file << std::fixed << std::setprecision(10) << m_fft_mag[idx] << ","
              << m_fft_mag[mod(idx - 1, m_number_of_bins)] << ","
              << m_fft_mag[mod(idx + 1, m_number_of_bins)] << "," << rec_en
              << "," << std::endl;
#endif
#ifdef GRLORA_DEBUG
  idx_file << idx << ", ";
#endif
  // std::cout<<idx<<", ";
  return (idx);
}

/**
 * @brief Reset the block variables when a new lora packet needs to be
 * decoded.
 *
 * @param id
 */
void fft_demod_impl::new_frame_handler(int cfo_int) {
#ifdef GRLORA_MEASUREMENTS
  energy_file << "\n";
#endif
#ifdef GRLORA_DEBUG
  idx_file << std::endl;
#endif
  // std::cout<<std::endl;

  // create downchirp taking CFOint into account

  build_upchirp(&m_upchirp[0], cfo_int, m_sf);
  volk_32fc_conjugate_32fc(&m_downchirp[0], &m_upchirp[0], m_number_of_bins);
  output.clear();
};

/**
 * @brief Handles the reception of the coding rate received by the
 * header_decoder block.
 *
 * @param cr
 */
void fft_demod_impl::header_cr_handler(pmt::pmt_t cr) {
  m_cr = pmt::to_long(cr);
};

/**
 * @brief Main function where the actual computation is done
 *
 * @param noutput_items : number of output items to produce
 * @param ninput_items : number of input items
 * @param input_items : input item (i.e. output of the frame sync stage)
 * @param output_items : output data
 * @return int
 */
int fft_demod_impl::general_work(int noutput_items, gr_vector_int &ninput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items) {
  const gr_complex *in = (const gr_complex *)input_items[0];
  uint32_t *out = (uint32_t *)output_items[0];

  // std::cout<<"buffer_fft_demod"<<ninput_items[0]<<"/"<<noutput_items<<std::endl;
  int to_output = 0;
  std::vector<tag_t> tags;
  get_tags_in_window(tags, 0, 0, 1, pmt::string_to_symbol("frame_info"));
  if (tags.size()) {
    pmt::pmt_t err = pmt::string_to_symbol("error");
    is_header = pmt::to_bool(
        pmt::dict_ref(tags[0].value, pmt::string_to_symbol("is_header"), err));
    if (is_header) {
      int cfo_int = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cfo_int"), err));
      new_frame_handler(cfo_int);
      // std::cout<<"\nfft_header "<<tags[0].offset<<" - cfo:"<<cfo_int<<"\n";
    } else {
      m_cr = pmt::to_long(
          pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cr"), err));

      // std::cout<<"\nfft_cr "<<tags[0].offset<<" - cr: "<<(int)m_cr<<"\n";
    }
    tags[0].offset = nitems_written(0);
    add_item_tag(0, tags[0]); // 8 LoRa symbols in the header
  }

  // shift by -1 and use reduce rate if first block (header)
  output.push_back(mod(get_symbol_val(in) - 1, (1 << m_sf)) /
                   (is_header ? 4 : 1));
  block_size = 4 + (is_header ? 4 : m_cr);
  if ((output.size() == block_size)) {
    memcpy(&out[0], &output[0], block_size * sizeof(uint32_t));
    for (int i = 0; i < output.size(); i++) {
    }

    output.clear();
    to_output = block_size;
  } else
    to_output = 0;
  consume_each(1);

  return to_output;
}

} /* namespace lora_sdr */
} /* namespace gr */
