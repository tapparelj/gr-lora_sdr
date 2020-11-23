#ifndef INCLUDED_LORA_MODULATE_IMPL_H
#define INCLUDED_LORA_MODULATE_IMPL_H

#include <fstream>
#include <gnuradio/io_signature.h>
#include <iostream>
#include <lora_sdr/modulate.h>

#include <lora_sdr/utilities.h>

namespace gr {
namespace lora_sdr {

class modulate_impl : public modulate {
private:
  /**
   * @brief Transmission spreading factor
   * 
   */
  uint8_t m_sf;     

  /**
   * @brief Transmission sampling rate
   * 
   */
  uint32_t m_samp_rate; 

  /**
   * @brief Transmission bandwidth (Works only for samp_rate=bw)
   * 
   */
  uint32_t m_bw; 

  /**
   * @brief number of bin per lora symbol
   * 
   */
  uint32_t m_number_of_bins;

  /**
   * @brief lora symbols per second
   * 
   */
  double m_symbols_per_second;  

  /**
   * @brief samples per symbols(Works only for 2^sf)
   * 
   */
  uint32_t m_samples_per_symbol; 

  /**
   * @brief reference upchirp
   * 
   */
  std::vector<gr_complex> m_upchirp;  

  /**
   * @brief reference downchirp
   * 
   */
  std::vector<gr_complex> m_downchirp; 

  /**
   * @brief number of upchirps in the preamble
   * 
   */
  uint n_up;    

  /**
   * @brief counter of the number of lora symbols sent
   * 
   */
  uint32_t symb_cnt;

  /**
   * @brief 
   * 
   * @param message 
   */
  void msg_handler(pmt::pmt_t message);

public:
  /**
   * @brief Construct a new modulate impl object
   * 
   * @param sf spreading factor
   * @param samp_rate sampling rate
   * @param bw bandwith
   */
  modulate_impl(uint8_t sf, uint32_t samp_rate, uint32_t bw);

  /**
   * @brief Destroy the modulate impl object
   * 
   */
  ~modulate_impl();

  /**
   * @brief 
   * 
   * @param noutput_items 
   * @param ninput_items_required 
   */
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  /**
   * @brief 
   * 
   * @param noutput_items 
   * @param ninput_items 
   * @param input_items 
   * @param output_items 
   * @return int 
   */
  int general_work(int noutput_items, gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_MODULATE_IMPL_H */
