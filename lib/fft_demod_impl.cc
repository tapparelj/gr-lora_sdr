#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>

#include <boost/math/special_functions/bessel.hpp>  // to compute LLR
#include <limits>

#include "fft_demod_impl.h"
extern "C" {
#include "kiss_fft.h"
}

namespace gr {
    namespace lora_sdr {

        fft_demod::sptr
        fft_demod::make( bool soft_decoding, bool max_log_approx) {
            return gnuradio::get_initial_sptr(new fft_demod_impl(soft_decoding, max_log_approx));
        }

        /*
         * The private constructor
         */
        fft_demod_impl::fft_demod_impl(bool soft_decoding, bool max_log_approx)
            : gr::block("fft_demod",
                        gr::io_signature::make(1, 1, sizeof(gr_complex)),
                        gr::io_signature::make(1, 1, soft_decoding ? MAX_SF * sizeof(LLR) : sizeof(uint16_t))),
                        m_soft_decoding(soft_decoding), max_log_approx(max_log_approx), 
                        m_new_frame(true) {
            set_sf(MIN_SF);//accept any new sf
            m_symb_cnt = 0;
            // m_samples_per_symbol = (uint32_t)(1u << m_sf);
            m_ldro = false;

            set_tag_propagation_policy(TPP_DONT);
#ifdef GRLORA_MEASUREMENTS
            int num = 0;  // check next file name to use
            while (1) {
                std::ifstream infile("../../matlab/measurements/energy" + std::to_string(num) + ".txt");
                if (!infile.good())
                    break;
                num++;
            }
            energy_file.open("../../matlab/measurements/energy" + std::to_string(num) + ".txt", std::ios::out | std::ios::trunc);
#endif
#ifdef GRLORA_DEBUG
            idx_file.open("../data/idx.txt", std::ios::out | std::ios::trunc);
#endif
#ifdef GRLORA_SNR_MEASUREMENTS_SAVE
            SNRestim_file.open("../data/SNR_estimation.txt", std::ios::out | std::ios::trunc); //std::ios::trunc);
            //SNRestim_file << "New exp" << std::endl;
#endif
#ifdef GRLORA_BESSEL_MEASUREMENTS_SAVE
            bessel_file.open("../data/BesselArg.txt", std::ios::out | std::ios::trunc);
#endif
        }
        /*
         * Our virtual destructor.
         */
        fft_demod_impl::~fft_demod_impl() {}

        void fft_demod_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required) {
            ninput_items_required[0] = m_samples_per_symbol;
        }
        void fft_demod_impl::set_sf(int sf){//Set he new sf for the frame
        // std::cout<<"[fft_demod_impl.cc] new sf received "<<sf<<std::endl;
        m_sf = sf;
        m_samples_per_symbol = (uint32_t)(1u << m_sf);
        m_upchirp.resize(m_samples_per_symbol);
        m_downchirp.resize(m_samples_per_symbol);

        // FFT demodulation preparations
        m_fft.resize(m_samples_per_symbol);
        m_dechirped.resize(m_samples_per_symbol);
    }


        float *fft_demod_impl::compute_fft_mag(const gr_complex *samples) {
            float rec_en = 0;
            kiss_fft_cfg cfg = kiss_fft_alloc(m_samples_per_symbol, 0, 0, 0);
            kiss_fft_cpx *cx_in = new kiss_fft_cpx[m_samples_per_symbol];
            kiss_fft_cpx *cx_out = new kiss_fft_cpx[m_samples_per_symbol];

            // Multiply with ideal downchirp
            volk_32fc_x2_multiply_32fc(&m_dechirped[0], samples, &m_downchirp[0], m_samples_per_symbol);
            for (int i = 0; i < m_samples_per_symbol; i++) {
                cx_in[i].r = m_dechirped[i].real();
                cx_in[i].i = m_dechirped[i].imag();
            }
            // do the FFT
            kiss_fft(cfg, cx_in, cx_out);

            // Get magnitude squared
            float *m_fft_mag_sq = new float[m_samples_per_symbol];  // /!\ dynamic memory allocation
            for (uint32_t i = 0u; i < m_samples_per_symbol; i++) {
                m_fft_mag_sq[i] = cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i;
                rec_en += m_fft_mag_sq[i];
            }

            free(cfg);
            delete[] cx_in;
            delete[] cx_out;

            return m_fft_mag_sq;  // /!\ delete[] , release memory after !
        }

        // Use in Hard-decoding
        uint16_t fft_demod_impl::get_symbol_val(const gr_complex *samples) {
            float *m_fft_mag_sq = compute_fft_mag(samples);

            // Return argmax
            uint16_t idx = std::max_element(m_fft_mag_sq, m_fft_mag_sq + m_samples_per_symbol) - m_fft_mag_sq;
            // std::cout << " hard-dec idx " << idx /*<< " m_fft_mag_sq " << m_fft_mag_sq[0] */<< std::endl;

#ifdef GRLORA_MEASUREMENTS
            energy_file << std::fixed << std::setprecision(10) << m_fft_mag_sq[idx] << "," << m_fft_mag_sq[mod(idx - 1, m_samples_per_symbol)] << "," << m_fft_mag_sq[mod(idx + 1, m_samples_per_symbol)] << "," << rec_en << "," << std::endl;
#endif
            // std::cout<<"SNR est = "<<m_fft_mag_sq[idx]<<","<<rec_en<<","<<10*log10(m_fft_mag_sq[idx]/(rec_en-m_fft_mag_sq[idx]))<<std::endl;

#ifdef GRLORA_DEBUG
            idx_file << idx << ", ";
#endif
            //  std::cout<<idx<<", ";
            delete[] m_fft_mag_sq;

            return idx;
        }

        // Use in Soft-decoding
        std::vector<LLR> fft_demod_impl::get_LLRs(const gr_complex *samples) {
            float *m_fft_mag_sq = compute_fft_mag(samples); // from dynamic memory alloc

            // Compute LLRs of the SF bits
            double LLs[m_samples_per_symbol];   // 2**sf  Log-Likelihood
            std::vector<LLR> LLRs(MAX_SF,0);        //      Log-Likelihood Ratios

            
            //static double Ps_frame = 0; // Signal Power estimation updated at each rx new frame
            //static double Pn_frame = 0; // Signal Power estimation updated at each rx new frame

            // compute SNR estimate at each received symbol as SNR remains constant during 1 simulation run
            // Estimate signal power
            int symbol_idx = std::max_element(m_fft_mag_sq, m_fft_mag_sq + m_samples_per_symbol) - m_fft_mag_sq;

            // Estimate noise power
            double signal_energy = 0;
            double noise_energy = 0;

            int n_adjacent_bins = 1; // Put '0' for best accurate SNR estimation but if symbols energy splitted in 2 bins, put '1' for safety
            for (int i = 0; i < m_samples_per_symbol; i++) {
                if ( mod(std::abs(i - symbol_idx), m_samples_per_symbol-1) < 1 + n_adjacent_bins ) 
                    signal_energy += m_fft_mag_sq[i];
                else
                    noise_energy += m_fft_mag_sq[i];   
            }
            // If you want to use a normalized constant identical to all symbols within a frame, but it leads to same performance
            // Lowpass filter update
            //double p = 0.99; // proportion to keep
            //Ps_est = p*Ps_est + (1-p)*  signal_energy / m_samples_per_symbol;
            //Pn_est = p*Pn_est + (1-p)* noise_energy / (m_samples_per_symbol-1-2*n_adjacent_bins); // remove used bins for better estimation
            // Signal and noise power estimation for each received symbol
            m_Ps_est = signal_energy / m_samples_per_symbol;
            m_Pn_est = noise_energy / (m_samples_per_symbol-1-2*n_adjacent_bins);
            
#ifdef GRLORA_SNR_MEASUREMENTS_SAVE
            SNRestim_file << std::setprecision(6) << m_Ps_est << "," << m_Pn_est << std::endl;
#endif
            /*static int num_frames = 0;
            if (m_new_frame) { 
                Ps_frame = Ps_est;
                Pn_frame = Pn_est;
                m_new_frame = false; // will be set back to True by new_frame_handler()
                num_frames++;
                //if (num_frames % 100 == 0) std::cout << "-----> SNRdB estim: " << 10*std::log10(Ps_frame/Pn_frame) << std::endl;
            }*/

#ifdef GRLORA_BESSEL_MEASUREMENTS_SAVE
            for (uint32_t n = 0; n < m_samples_per_symbol; n++) {
                bessel_file << std::setprecision(8) << std::sqrt(Ps_frame) / Pn_frame * std::sqrt(m_fft_mag_sq[n]) << ","  << Ps_frame << "," << Pn_frame << "," << m_fft_mag_sq[n] << std::endl;
            }            
#endif
            //double SNRdB_estimate = 10*std::log10(Ps_frame/Pn_frame);
            double SNRdB_estimate = 10*std::log10(m_Ps_est/m_Pn_est);
            //std::cout << "SNR " << SNRdB_estimate << std::endl;
            //  Normalize fft_mag to 1 to avoid Bessel overflow
            for (int i = 0; i < m_samples_per_symbol; i++) {  // upgrade to avoid for loop
                m_fft_mag_sq[i] *= m_samples_per_symbol; // Normalized |Y[n]| * sqrt(N) => |Y[n]|² * N (depends on kiss FFT library)
                //m_fft_mag_sq[i] /= Ps_frame; // // Normalize to avoid Bessel overflow (does not change the performances)
            }

            bool clipping = false;
            for (uint32_t n = 0; n < m_samples_per_symbol; n++) {
                double bessel_arg = std::sqrt(m_Ps_est) / m_Pn_est * std::sqrt(m_fft_mag_sq[n]);
                // Manage overflow of Bessel function
                if (bessel_arg < 713)  // 713 ~ log(std::numeric_limits<LLR>::max())
                    LLs[n] = boost::math::cyl_bessel_i(0, bessel_arg);  // compute Bessel safely
                else {
                    //std::cerr << RED << "Log-Likelihood clipping :-( SNR: " << SNRdB_estimate << " |Y|: " << std::sqrt(m_fft_mag_sq[n]) << RESET << std::endl;
                    //LLs[n] = std::numeric_limits<LLR>::max();  // clipping
                    clipping = true;
                }
                if (max_log_approx) LLs[n] = std::log(LLs[n]);  // Log-Likelihood
                //LLs[n] = m_fft_mag_sq[n]; // same performance with just |Y[n]| or |Y[n]|²
            }

            if (clipping) // change to max-log formula with only |Y[n]|² to avoid overflows, solve LLR computation incapacity in high SNR
                for (uint32_t n = 0; n < m_samples_per_symbol; n++) LLs[n] = m_fft_mag_sq[n];

            // Log-Likelihood Ratio estimations
            if (max_log_approx) {
                for (uint32_t i = 0; i < m_sf; i++) { // sf bits => sf LLRs
                    double max_X1(0), max_X0(0); // X1 = set of symbols where i-th bit is '1'
                    for (uint32_t n = 0; n < m_samples_per_symbol; n++) {  // for all symbols n : 0 --> 2^sf
                        // LoRa: shift by -1 and use reduce rate if first block (header)
                        uint32_t s = mod(n - 1, (1 << m_sf)) / ((is_header||m_ldro )? 4 : 1);
                        s = (s ^ (s >> 1u));  // Gray encoding formula               // Gray demap before (in this block)
                        if (s & (1u << i)) {  // if i-th bit of symbol n is '1'
                            if (LLs[n] > max_X1) max_X1 = LLs[n];
                        } else {              // if i-th bit of symbol n is '0'
                            if (LLs[n] > max_X0) max_X0 = LLs[n];
                        }
                    }
                    LLRs[m_sf - 1 - i] = max_X1 - max_X0;  // [MSB ... ... LSB]
                }
            } else {
                // Without max-log approximation of the LLR estimation
                for (uint32_t i = 0; i < m_sf; i++) {
                    double sum_X1(0), sum_X0(0); // X1 = set of symbols where i-th bit is '1'
                    for (uint32_t n = 0; n < m_samples_per_symbol; n++) {  // for all symbols n : 0 --> 2^sf
                        uint32_t s = mod(n - 1, (1 << m_sf)) / ((is_header||m_ldro)? 4 : 1);
                        s = (s ^ (s >> 1u));  // Gray demap
                        if (s & (1u << i)) sum_X1 += LLs[n]; // Likelihood
                        else sum_X0 += LLs[n];
                    }
                    LLRs[m_sf - 1 - i] = std::log(sum_X1) - std::log(sum_X0); // [MSB ... ... LSB]
                }
            }

#ifdef GRLORA_LLR_MEASUREMENTS_SAVE
            // Save Log-Likelihood and LLR for debug
            std::ofstream LL_file, LLR_file;
            LL_file.open("../data/fft_LL.txt", std::ios::out | std::ios::trunc);
            LLR_file.open("../data/LLR.txt", std::ios::out | std::ios::trunc);

            for (uint32_t n = 0; n < m_samples_per_symbol; n++) 
                LL_file << std::fixed << std::setprecision(10) << m_fft_mag_sq[n] << "," << LLs[n] << std::endl;
            LL_file.close();
            for (uint32_t i = 0; i < m_sf; i++) LLR_file << std::fixed << std::setprecision(10) << LLRs[i] << std::endl;
            LLR_file.close();
#endif

            delete[] m_fft_mag_sq; // release memory
            return LLRs;
        }

        void fft_demod_impl::header_cr_handler(pmt::pmt_t cr) {
            m_cr = pmt::to_long(cr);
        };

        int fft_demod_impl::general_work(int noutput_items,
                                         gr_vector_int &ninput_items,
                                         gr_vector_const_void_star &input_items,
                                         gr_vector_void_star &output_items) {
            const gr_complex *in = (const gr_complex *)input_items[0];
            uint16_t *out1 = (uint16_t *)output_items[0];
            LLR *out2 = (LLR *)output_items[0];
            int to_output = 0;
            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, m_samples_per_symbol, pmt::string_to_symbol("frame_info"));
            if (tags.size()) 
            {
                pmt::pmt_t err = pmt::string_to_symbol("error");
                is_header = pmt::to_bool(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("is_header"), err));
                if (is_header) // new frame beginning
                {
                    int cfo_int = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cfo_int"), err));
                    float cfo_frac = pmt::to_float(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cfo_frac"), err));
                    int sf = pmt::to_double(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("sf"), err));
                    if(sf != m_sf)
                        set_sf(sf);
                     //create downchirp taking CFO_int into account
                    build_upchirp(&m_upchirp[0], mod(cfo_int, m_samples_per_symbol), m_sf);
                    volk_32fc_conjugate_32fc(&m_downchirp[0], &m_upchirp[0], m_samples_per_symbol);
                    // adapt the downchirp to the cfo_frac of the frame
                    for (int n = 0; n < m_samples_per_symbol; n++)
                    {
                        m_downchirp[n] = m_downchirp[n] * gr_expj(-2 * M_PI * cfo_frac / m_samples_per_symbol * n);
                    }
                    output.clear();
                } 
                else
                {
                    m_cr = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("cr"), err));
                    m_ldro = pmt::to_bool(pmt::dict_ref(tags[0].value,pmt::string_to_symbol("ldro"),err));
                    m_symb_numb = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("symb_numb"), err));                
                }
            }
            if(ninput_items[0]>=m_samples_per_symbol)//check if we have enough samples at the input
            {
                if (tags.size()){
                        tags[0].offset = nitems_written(0);
                        add_item_tag(0, tags[0]);  // 8 LoRa symbols in the header
                }

                block_size = 4 + (is_header ? 4 : m_cr);

                if (m_soft_decoding) {
                    LLRs_block.push_back(get_LLRs(in));  // Store 'sf' LLRs
                } else {                                 // Hard decoding
                    // shift by -1 and use reduce rate if first block (header)
                    output.push_back(mod(get_symbol_val(in) - 1, (1 << m_sf)) / ((is_header||m_ldro) ? 4 : 1));
                }

                if (output.size() == block_size || LLRs_block.size() == block_size) {
                    if (m_soft_decoding) {
                        for (int i = 0; i < block_size; i++)
                            memcpy(out2 + i * m_sf, LLRs_block[i].data(), m_sf * sizeof(LLR));
                        LLRs_block.clear();
                    } else {  // Hard decoding
                        memcpy(out1, output.data(), block_size * sizeof(uint16_t));
                        output.clear();
                    }
                    to_output = block_size;
                } 
                else
                {
                    to_output = 0;
                }
                consume_each(m_samples_per_symbol);
                m_symb_cnt += 1;
                if(m_symb_cnt == m_symb_numb){
                // std::cout<<"fft_demod_impl.cc end of frame\n";
                // set_sf(0);
                m_symb_cnt = 0;
                }
            }
            else{
                to_output = 0;
            }
            if (noutput_items < to_output)
            {
                print(RED<<"fft_demod not enough space in output buffer!!"<<RESET);
            }
            
            return to_output;
        }

    } /* namespace lora_sdr */
} /* namespace gr */
