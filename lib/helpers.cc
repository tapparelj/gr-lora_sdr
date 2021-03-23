/**
 * @file helpers.cc
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-03-23
 * Helper functions that make life a little bit easier :)
 *
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "helpers.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

/**
 * @brief Function that gets the symbol from the received samples
 *
 * @param samples : the complex samples
 * @param ref_chirp The reference chirp to use to dechirp the lora symbol.
 * @return uint32_t
 */
uint32_t get_symbol_val(const gr_complex *samples, gr_complex *ref_chirp,
                        uint32_t m_number_of_bins,
                        uint32_t m_samples_per_symbol, kiss_fft_cpx *cx_in,
                        kiss_fft_cpx *cx_out) {
  double sig_en = 0;
  float fft_mag[m_number_of_bins];
  std::vector<gr_complex> dechirped(m_number_of_bins);

  kiss_fft_cfg cfg = kiss_fft_alloc(m_samples_per_symbol, 0, 0, 0);

  // Multiply with ideal downchirp
  volk_32fc_x2_multiply_32fc(&dechirped[0], samples, ref_chirp,
                             m_samples_per_symbol);

  for (int i = 0; i < m_samples_per_symbol; i++) {
    cx_in[i].r = dechirped[i].real();
    cx_in[i].i = dechirped[i].imag();
  }
  // do the FFT
  kiss_fft(cfg, cx_in, cx_out);

  // Get magnitude
  for (uint32_t i = 0u; i < m_number_of_bins; i++) {
    fft_mag[i] = cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i;
    sig_en += fft_mag[i];
  }
  free(cfg);
  // Return argmax here
  return ((std::max_element(fft_mag, fft_mag + m_number_of_bins) - fft_mag));
}

/**
 * @brief Determine the energy of a symbol.
 *
 * @param samples the complex symbol to analyse.
 * @return float
 */
float determine_energy(const gr_complex *samples,
                       uint32_t m_samples_per_symbol) {
  float magsq_chirp[m_samples_per_symbol];
  float energy_chirp = 0;
  volk_32fc_magnitude_squared_32f(magsq_chirp, samples, m_samples_per_symbol);
  volk_32f_accumulator_s32f(&energy_chirp, magsq_chirp, m_samples_per_symbol);
  return energy_chirp;
}

/**
 * @brief Convert an integer into a MSB first vector of bool
 *
 * @param integer : The integer to convert
 * @param n_bits : The output number of bits
 * @return std::vector<bool>
 */
std::vector<bool> int2bool(uint integer, uint8_t n_bits) {
  std::vector<bool> vec(n_bits, 0);
  int j = n_bits;
  for (int i = 0; i < n_bits; i++) {
    vec[--j] = ((integer >> i) & 1);
  }
  return vec;
}

/**
 * @brief Convert a MSB first vector of bool to a integer
 *
 * @param b The boolean vector to convert
 * @return uint32_t
 */
uint32_t bool2int(std::vector<bool> b) {
  uint32_t integer = std::accumulate(b.begin(), b.end(), 0,
                                     [](int x, int y) { return (x << 1) + y; });
  return integer;
}

/**
 *  @brief  return the modulus a%b between 0 and (b-1)
 */
long mod(long a, long b) { return (a % b + b) % b; }

/**
 * @brief Return the reference chirps using s_f=bw
 *
 * @param upchirp : The pointer to the reference upchirp
 * @param downchirp : The pointer to the reference downchirp
 * @param sf : The spreading factor to use
 */
void build_ref_chirps(gr_complex *upchirp, gr_complex *downchirp, uint8_t sf) {
  double N = (1 << sf);
  for (uint n = 0; n < N; n++) {
    // the scaling factor of 0.9 is here to avoid to saturate the USRP_SINK
    upchirp[n] = gr_complex(0.9f, 0.0f) *
                 gr_expj(2.0 * M_PI * (n * n / (2 * N) - 0.5 * n));
    downchirp[n] = gr_complex(0.9f, 0.0f) *
                   gr_expj(-2.0 * M_PI * (n * n / (2 * N) - 0.5 * n));
  }
}

/**
 * @brief Return an modulated upchirp using s_f=bw
 *
 * @param chirp : The pointer to the modulated upchirp
 * @param id : The number used to modulate the chirp
 * @param sf : The spreading factor to use
 */
void build_upchirp(gr_complex *chirp, uint32_t id, uint8_t sf) {
  double N = 1 << sf;
  // procces all samples
  for (uint n = 0; n < N; n++) {
    // the scaling factor of 0.9 is here to avoid to saturate the USRP_SINK
    chirp[n] = gr_complex(0.9f, 0.0f) *
               gr_expj(2.0 * M_PI * (n * n / (2 * N) + (id / N - 0.5) * n));
  }
}

} /* namespace lora_sdr */
} /* namespace gr */
