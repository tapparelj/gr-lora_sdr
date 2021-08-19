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


#define RESET "\033[0m"
#define RED "\033[31m" /* Red */

/**
 * @brief Simple modulo the modulus a%b between 0 and (b-1)
 *
 * @param a
 * @param b
 * @return long modulo of a%b
 */
long mod(long a, long b);

/**
 * @brief Simple modulo the modulus a%b between 0 and (b-1) for doubles
 *
 * @param a
 * @param b
 * @return double
 */
double double_mod(double a, long b);

/**
 * @brief Convert an integer into a MSB first vector of bool
 *
 * @param integer The integer to convert
 * @param n_bits The output number of bits
 * @return std::vector<bool>
 */
std::vector<bool> int2bool(uint8_t integer, uint8_t n_bits);

/**
 * @brief Generates a random string of given length
 *
 * @param Nbytes : Number of bytes in the string
 * @return std::string
 */
std::string random_string(int Nbytes);

/**
 * @brief Function that gets the symbol from the received samples
 *
 * @param samples : the complex samples
 * @param ref_chirp : the reference chirp to use to dechirp the lora symbol.
 * @param m_number_of_bins : number of bings
 * @param m_samples_per_symbol : number of samples per LoRa symbol
 * @param cx_in : fft in
 * @param cx_out : fft out
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
 * @param m_samples_per_symbol : number of samples per LoRa symbol
 * @return float
 */
float determine_energy(const gr_complex *samples,
                       uint32_t m_samples_per_symbol);

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

/**
 * @brief Return an modulated upchirp using s_f=bw with over sampling factor
 *
 * @param chirp : The pointer to the modulated upchirp
 * @param id : The number used to modulate the chirp
 * @param sf : The spreading factor to use
 * @param os_factor : oversmapling factor
 */
void build_upchirp_os_factor(gr_complex *chirp, uint32_t id, uint8_t sf,uint8_t os_factor);

} // namespace lora_sdr
} // namespace gr
