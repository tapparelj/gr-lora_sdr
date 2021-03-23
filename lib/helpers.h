/**
 * @file helpers.h
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-03-23
 * Header file for helper functions that make life a little bit easier :)
 *
 */
#include <cstdint>
#include <gnuradio/expj.h>
#include <gnuradio/io_signature.h>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string.h>
#include <volk/volk.h>

extern "C" {
#include "kiss_fft.h"
}

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
                        kiss_fft_cpx *cx_out);

/**
 * @brief Determine the energy of a symbol.
 *
 * @param samples The complex symbol to analyse.
 * @return float
 */
float determine_energy(const gr_complex *samples,
                       uint32_t m_samples_per_symbol);

/**
 *  @brief  return the modulus a%b between 0 and (b-1)
 */
long mod(long a, long b);

/**
 * @brief Convert an integer into a MSB first vector of bool
 *
 * @param integer : The integer to convert
 * @param n_bits : The output number of bits
 * @return std::vector<bool>
 */
std::vector<bool> int2bool(uint integer, uint8_t n_bits);

/**
 * @brief Convert a MSB first vector of bool to a integer
 *
 * @param b The boolean vector to convert
 * @return uint32_t
 */
uint32_t bool2int(std::vector<bool> b);

/**
 * @brief Return the reference chirps using s_f=bw
 *
 * @param upchirp : The pointer to the reference upchirp
 * @param downchirp : The pointer to the reference downchirp
 * @param sf : The spreading factor to use
 */
void build_ref_chirps(gr_complex *upchirp, gr_complex *downchirp, uint8_t sf);

/**
 * @brief Return an modulated upchirp using s_f=bw
 *
 * @param chirp : The pointer to the modulated upchirp
 * @param id : The number used to modulate the chirp
 * @param sf : The spreading factor to use
 */
void build_upchirp(gr_complex *chirp, uint32_t id, uint8_t sf);

} // namespace lora_sdr
} // namespace gr
