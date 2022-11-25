#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "frame_sync_impl.h"

namespace gr
{
    namespace lora_sdr
    {

        frame_sync::sptr
        frame_sync::make(uint32_t center_freq, uint32_t bandwidth, uint8_t sf, bool impl_head, std::vector<uint16_t> sync_word, uint8_t os_factor, uint16_t preamble_len = 8)
        {
            return gnuradio::get_initial_sptr(new frame_sync_impl(center_freq, bandwidth, sf, impl_head, sync_word, os_factor, preamble_len));
        }

        /*
         * The private constructor
         */
        frame_sync_impl::frame_sync_impl(uint32_t center_freq, uint32_t bandwidth, uint8_t sf, bool impl_head, std::vector<uint16_t> sync_word, uint8_t os_factor, uint16_t preamble_len)
            : gr::block("frame_sync",
                        gr::io_signature::make(1, 1, sizeof(gr_complex)),
                        gr::io_signature::make2(1, 2, sizeof(gr_complex), sizeof(float)))
        {
            m_state = DETECT;
            m_center_freq = center_freq;
            m_bw = bandwidth;
            m_sf = sf;

            m_sync_words = sync_word;
            m_os_factor = os_factor;
            if (preamble_len < 5)
            {
                std::cerr << RED << " Preamble length should be greater than 5!" << RESET << std::endl;
            }

            m_preamb_len = preamble_len;
            net_ids.resize(2, 0);

            m_n_up_req = preamble_len - 3;
            up_symb_to_use = m_n_up_req - 1;

            m_sto_frac = 0.0;

            m_impl_head = impl_head;

            // Convert given sync word into the two modulated values in preamble
            if (m_sync_words.size() == 1)
            {
                uint16_t tmp = m_sync_words[0];
                m_sync_words.resize(2, 0);
                m_sync_words[0] = ((tmp & 0xF0) >> 4) << 3;
                m_sync_words[1] = (tmp & 0x0F) << 3;
            }

            m_number_of_bins = (uint32_t)(1u << m_sf);
            m_samples_per_symbol = m_number_of_bins * m_os_factor;
            additional_symbol_samp.resize(2 * m_samples_per_symbol);
            m_upchirp.resize(m_number_of_bins);
            m_downchirp.resize(m_number_of_bins);
            preamble_upchirps.resize(m_preamb_len * m_number_of_bins);
            preamble_raw_up.resize((m_preamb_len + 3) * m_samples_per_symbol);
            CFO_frac_correc.resize(m_number_of_bins);
            CFO_SFO_frac_correc.resize(m_number_of_bins);
            symb_corr.resize(m_number_of_bins);
            in_down.resize(m_number_of_bins);
            preamble_raw.resize(m_preamb_len * m_number_of_bins);
            net_id_samp.resize(m_samples_per_symbol * 2.5); // we should be able to move up to one quarter of symbol in each direction

            build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

            bin_idx = 0;
            symbol_cnt = 1;
            k_hat = 0;
            preamb_up_vals.resize(m_n_up_req, 0);
            frame_cnt = 0;

            cx_in = new kiss_fft_cpx[m_number_of_bins];
            cx_out = new kiss_fft_cpx[m_number_of_bins];
            // register message ports
            message_port_register_in(pmt::mp("frame_info"));
            set_msg_handler(pmt::mp("frame_info"), [this](pmt::pmt_t msg)
                            { this->frame_info_handler(msg); });

            message_port_register_in(pmt::mp("noise_est"));
            set_msg_handler(pmt::mp("noise_est"), [this](pmt::pmt_t msg)
                            { this->noise_est_handler(msg); });

#ifdef GRLORA_DEBUG
            preamb_file.open("../../matlab/SFO/preamb.txt", std::ios::out | std::ios::trunc);
#endif
            // start_off_file.open("../../matlab/Raspi_HAT/start_off_file.txt", std::ios::out | std::ios::trunc);
            // detect_file.open("../../matlab/SFO/detect.txt", std::ios::out | std::ios::trunc);
            // netid_file.open("../../matlab/SFO/net_id.txt", std::ios::out | std::ios::trunc);
            // netid_corr_file.open("../../matlab/SFO/net_id_corr.txt", std::ios::out | std::ios::trunc);
        }

        /*
         * Our virtual destructor.
         */
        frame_sync_impl::~frame_sync_impl()
        {
        }
        int frame_sync_impl::my_roundf(float number)
        {
            int ret_val = (int)(number > 0 ? int(number + 0.5) : std::ceil(number - 0.5));
            return ret_val;
        }
        void frame_sync_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
        {
            ninput_items_required[0] = (m_os_factor * (m_number_of_bins + 2));
        }

        float frame_sync_impl::estimate_CFO_frac(gr_complex *samples)
        {
            int k0;
            float cfo_frac;
            double Y_1, Y0, Y1, u, v, ka, wa, k_residual;
            std::vector<gr_complex> CFO_frac_correc_aug(up_symb_to_use * m_number_of_bins); ///< CFO frac correction vector
            std::vector<gr_complex> dechirped(up_symb_to_use * m_number_of_bins);
            kiss_fft_cpx *cx_in_cfo = new kiss_fft_cpx[2 * up_symb_to_use * m_number_of_bins];
            kiss_fft_cpx *cx_out_cfo = new kiss_fft_cpx[2 * up_symb_to_use * m_number_of_bins];

            float fft_mag_sq[2 * up_symb_to_use * m_number_of_bins];
            kiss_fft_cfg cfg_cfo = kiss_fft_alloc(2 * up_symb_to_use * m_number_of_bins, 0, 0, 0);
            // create longer downchirp
            std::vector<gr_complex> downchirp_aug(up_symb_to_use * m_number_of_bins);
            for (int i = 0; i < up_symb_to_use; i++)
            {
                memcpy(&downchirp_aug[i * m_number_of_bins], &m_downchirp[0], m_number_of_bins * sizeof(gr_complex));
            }

            // Dechirping
            volk_32fc_x2_multiply_32fc(&dechirped[0], samples, &downchirp_aug[0], up_symb_to_use * m_number_of_bins);
            // prepare FFT
            for (int i = 0; i < 2 * up_symb_to_use * m_number_of_bins; i++)
            {
                if (i < up_symb_to_use * m_number_of_bins)
                {
                    cx_in_cfo[i].r = dechirped[i].real();
                    cx_in_cfo[i].i = dechirped[i].imag();
                }
                else
                { // add padding
                    cx_in_cfo[i].r = 0;
                    cx_in_cfo[i].i = 0;
                }
            }
            // do the FFT
            kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);
            // Get magnitude
            for (uint32_t i = 0u; i < 2 * up_symb_to_use * m_number_of_bins; i++)
            {
                fft_mag_sq[i] = cx_out_cfo[i].r * cx_out_cfo[i].r + cx_out_cfo[i].i * cx_out_cfo[i].i;
            }
            free(cfg_cfo);
            delete[] cx_in_cfo;
            delete[] cx_out_cfo;
            // get argmax here
            k0 = ((std::max_element(fft_mag_sq, fft_mag_sq + 2 * up_symb_to_use * m_number_of_bins) - fft_mag_sq));

            // get three spectral lines
            Y_1 = fft_mag_sq[mod(k0 - 1, 2 * up_symb_to_use * m_number_of_bins)];
            Y0 = fft_mag_sq[k0];
            Y1 = fft_mag_sq[mod(k0 + 1, 2 * up_symb_to_use * m_number_of_bins)];
            // set constant coeff
            u = 64 * m_number_of_bins / 406.5506497; // from Cui yang (15)
            v = u * 2.4674;
            // RCTSL
            wa = (Y1 - Y_1) / (u * (Y1 + Y_1) + v * Y0);
            ka = wa * m_number_of_bins / M_PI;
            k_residual = fmod((k0 + ka) / 2 / up_symb_to_use, 1);
            cfo_frac = k_residual - (k_residual > 0.5 ? 1 : 0);
            // Correct CFO frac in preamble
            for (int n = 0; n < up_symb_to_use * m_number_of_bins; n++)
            {
                CFO_frac_correc_aug[n] = gr_expj(-2 * M_PI * (cfo_frac) / m_number_of_bins * n);
            }

            volk_32fc_x2_multiply_32fc(&preamble_upchirps[0], samples, &CFO_frac_correc_aug[0], up_symb_to_use * m_number_of_bins);

            return cfo_frac;
        }
        float frame_sync_impl::estimate_CFO_frac_Bernier(gr_complex *samples)
        {
            int k0[up_symb_to_use];
            float cfo_frac;
            std::vector<gr_complex> CFO_frac_correc_aug(up_symb_to_use * m_number_of_bins); ///< CFO frac correction vector
            double k0_mag[up_symb_to_use];
            std::vector<gr_complex> fft_val(up_symb_to_use * m_number_of_bins);

            std::vector<gr_complex> dechirped(m_number_of_bins);
            kiss_fft_cpx *cx_in_cfo = new kiss_fft_cpx[m_number_of_bins];
            kiss_fft_cpx *cx_out_cfo = new kiss_fft_cpx[m_number_of_bins];
            float fft_mag_sq[m_number_of_bins];
            for (size_t i = 0; i < m_number_of_bins; i++)
            {
                fft_mag_sq[i] = 0;
            }
            kiss_fft_cfg cfg_cfo = kiss_fft_alloc(m_number_of_bins, 0, 0, 0);
            for (int i = 0; i < up_symb_to_use; i++)
            {
                // Dechirping
                volk_32fc_x2_multiply_32fc(&dechirped[0], &samples[m_number_of_bins * i], &m_downchirp[0], m_number_of_bins);
                // prepare FFT
                for (int j = 0; j < m_number_of_bins; j++)
                {
                    cx_in_cfo[j].r = dechirped[j].real();
                    cx_in_cfo[j].i = dechirped[j].imag();
                }
                // do the FFT
                kiss_fft(cfg_cfo, cx_in_cfo, cx_out_cfo);
                // Get magnitude

                for (uint32_t j = 0u; j < m_number_of_bins; j++)
                {
                    fft_mag_sq[j] = cx_out_cfo[j].r * cx_out_cfo[j].r + cx_out_cfo[j].i * cx_out_cfo[j].i;
                    fft_val[j + i * m_number_of_bins] = gr_complex(cx_out_cfo[j].r, cx_out_cfo[j].i);
                }
                k0[i] = std::max_element(fft_mag_sq, fft_mag_sq + m_number_of_bins) - fft_mag_sq;

                k0_mag[i] = fft_mag_sq[k0[i]];
            }
            free(cfg_cfo);
            delete[] cx_in_cfo;
            delete[] cx_out_cfo;
            // get argmax
            int idx_max = k0[std::max_element(k0_mag, k0_mag + up_symb_to_use) - k0_mag];
            gr_complex four_cum(0.0f, 0.0f);
            for (int i = 0; i < up_symb_to_use - 1; i++)
            {
                four_cum += fft_val[idx_max + m_number_of_bins * i] * std::conj(fft_val[idx_max + m_number_of_bins * (i + 1)]);
            }
            cfo_frac = -std::arg(four_cum) / 2 / M_PI;
            // Correct CFO in preamble
            for (int n = 0; n < up_symb_to_use * m_number_of_bins; n++)
            {
                CFO_frac_correc_aug[n] = gr_expj(-2 * M_PI * cfo_frac / m_number_of_bins * n);
            }
            volk_32fc_x2_multiply_32fc(&preamble_upchirps[0], samples, &CFO_frac_correc_aug[0], up_symb_to_use * m_number_of_bins);
            return cfo_frac;
        }

        float frame_sync_impl::estimate_STO_frac()
        {
            int k0;
            double Y_1, Y0, Y1, u, v, ka, wa, k_residual;
            float sto_frac = 0;

            std::vector<gr_complex> dechirped(m_number_of_bins);
            kiss_fft_cpx *cx_in_sto = new kiss_fft_cpx[2 * m_number_of_bins];
            kiss_fft_cpx *cx_out_sto = new kiss_fft_cpx[2 * m_number_of_bins];

            float fft_mag_sq[2 * m_number_of_bins];
            for (size_t i = 0; i < 2 * m_number_of_bins; i++)
            {
                fft_mag_sq[i] = 0;
            }
            kiss_fft_cfg cfg_sto = kiss_fft_alloc(2 * m_number_of_bins, 0, 0, 0);

            for (int i = 0; i < up_symb_to_use; i++)
            {
                // Dechirping
                volk_32fc_x2_multiply_32fc(&dechirped[0], &preamble_upchirps[m_number_of_bins * i], &m_downchirp[0], m_number_of_bins);

                // prepare FFT
                for (int j = 0; j < 2 * m_number_of_bins; j++)
                {
                    if (j < m_number_of_bins)
                    {
                        cx_in_sto[j].r = dechirped[j].real();
                        cx_in_sto[j].i = dechirped[j].imag();
                    }
                    else
                    { // add padding
                        cx_in_sto[j].r = 0;
                        cx_in_sto[j].i = 0;
                    }
                }
                // do the FFT
                kiss_fft(cfg_sto, cx_in_sto, cx_out_sto);
                // Get magnitude
                for (uint32_t j = 0u; j < 2 * m_number_of_bins; j++)
                {
                    fft_mag_sq[j] += cx_out_sto[j].r * cx_out_sto[j].r + cx_out_sto[j].i * cx_out_sto[j].i;
                }
            }
            free(cfg_sto);
            delete[] cx_in_sto;
            delete[] cx_out_sto;

            // get argmax here
            k0 = std::max_element(fft_mag_sq, fft_mag_sq + 2 * m_number_of_bins) - fft_mag_sq;

            // get three spectral lines
            Y_1 = fft_mag_sq[mod(k0 - 1, 2 * m_number_of_bins)];
            Y0 = fft_mag_sq[k0];
            Y1 = fft_mag_sq[mod(k0 + 1, 2 * m_number_of_bins)];

            // set constant coeff
            u = 64 * m_number_of_bins / 406.5506497; // from Cui yang (eq.15)
            v = u * 2.4674;
            // RCTSL
            wa = (Y1 - Y_1) / (u * (Y1 + Y_1) + v * Y0);
            ka = wa * m_number_of_bins / M_PI;
            k_residual = fmod((k0 + ka) / 2, 1);
            sto_frac = k_residual - (k_residual > 0.5 ? 1 : 0);

            return sto_frac;
        }

        uint32_t frame_sync_impl::get_symbol_val(const gr_complex *samples, gr_complex *ref_chirp)
        {
            double sig_en = 0;
            float fft_mag[m_number_of_bins];
            std::vector<gr_complex> dechirped(m_number_of_bins);

            kiss_fft_cfg cfg = kiss_fft_alloc(m_number_of_bins, 0, 0, 0);

            // Multiply with ideal downchirp
            volk_32fc_x2_multiply_32fc(&dechirped[0], samples, ref_chirp, m_number_of_bins);

            for (int i = 0; i < m_number_of_bins; i++)
            {
                cx_in[i].r = dechirped[i].real();
                cx_in[i].i = dechirped[i].imag();
            }
            // do the FFT
            kiss_fft(cfg, cx_in, cx_out);

            // Get magnitude
            for (uint32_t i = 0u; i < m_number_of_bins; i++)
            {
                fft_mag[i] = cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i;
                sig_en += fft_mag[i];
            }
            free(cfg);
            // Return argmax here

            return sig_en ? ((std::max_element(fft_mag, fft_mag + m_number_of_bins) - fft_mag)) : -1;
        }

        float frame_sync_impl::determine_energy(const gr_complex *samples, int length = 1)
        {
            float magsq_chirp[m_number_of_bins * length];
            float energy_chirp = 0;
            volk_32fc_magnitude_squared_32f(magsq_chirp, samples, m_number_of_bins * length);
            volk_32f_accumulator_s32f(&energy_chirp, magsq_chirp, m_number_of_bins * length);
            return energy_chirp / m_number_of_bins / length;
        }
        float frame_sync_impl::determine_snr(const gr_complex *samples)
        {
            double tot_en = 0;
            float fft_mag[m_number_of_bins];
            std::vector<gr_complex> dechirped(m_number_of_bins);

            kiss_fft_cfg cfg = kiss_fft_alloc(m_number_of_bins, 0, 0, 0);

            // Multiply with ideal downchirp
            volk_32fc_x2_multiply_32fc(&dechirped[0], samples, &m_downchirp[0], m_number_of_bins);

            for (int i = 0; i < m_number_of_bins; i++)
            {
                cx_in[i].r = dechirped[i].real();
                cx_in[i].i = dechirped[i].imag();
            }
            // do the FFT
            kiss_fft(cfg, cx_in, cx_out);

            // Get magnitude
            for (uint32_t i = 0u; i < m_number_of_bins; i++)
            {
                fft_mag[i] = cx_out[i].r * cx_out[i].r + cx_out[i].i * cx_out[i].i;
                tot_en += fft_mag[i];
            }
            free(cfg);

            int max_idx = (std::max_element(fft_mag, fft_mag + m_number_of_bins) - fft_mag);
            float sig_en = fft_mag[max_idx];
            return 10 * log10(sig_en / (tot_en - sig_en));
        }

        void frame_sync_impl::noise_est_handler(pmt::pmt_t noise_est)
        {
            m_noise_est = pmt::to_double(noise_est);
        }
        void frame_sync_impl::frame_info_handler(pmt::pmt_t frame_info)
        {
            pmt::pmt_t err = pmt::string_to_symbol("error");

            m_cr = pmt::to_long(pmt::dict_ref(frame_info, pmt::string_to_symbol("cr"), err));
            m_pay_len = pmt::to_double(pmt::dict_ref(frame_info, pmt::string_to_symbol("pay_len"), err));
            m_has_crc = pmt::to_long(pmt::dict_ref(frame_info, pmt::string_to_symbol("crc"), err));
            uint8_t ldro_mode = pmt::to_long(pmt::dict_ref(frame_info, pmt::string_to_symbol("ldro_mode"), err));
            m_invalid_header = pmt::to_double(pmt::dict_ref(frame_info, pmt::string_to_symbol("err"), err));

            if (m_invalid_header)
            {
                m_state = DETECT;
                symbol_cnt = 1;
                k_hat = 0;
                m_sto_frac = 0;
            }
            else
            {
                if (ldro_mode == AUTO)
                    m_ldro = (float)(1u << m_sf) * 1e3 / m_bw > LDRO_MAX_DURATION_MS;
                else
                    m_ldro = ldro_mode;

                m_symb_numb = 8 + ceil((double)(2 * m_pay_len - m_sf + 2 + !m_impl_head * 5 + m_has_crc * 4) / (m_sf - 2 * m_ldro)) * (4 + m_cr);
                m_received_head = true;
                frame_info = pmt::dict_add(frame_info, pmt::intern("is_header"), pmt::from_bool(false));
                frame_info = pmt::dict_add(frame_info, pmt::intern("symb_numb"), pmt::from_long(m_symb_numb));
                frame_info = pmt::dict_delete(frame_info, pmt::intern("ldro_mode"));

                frame_info = pmt::dict_add(frame_info, pmt::intern("ldro"), pmt::from_bool(m_ldro));
                add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_info"), frame_info);
            }
        }

        void frame_sync_impl::set_sf(int sf)
        {
            m_sf = sf;
            m_number_of_bins = (uint32_t)(1u << m_sf);
            m_samples_per_symbol = m_number_of_bins * m_os_factor;
            additional_symbol_samp.resize(2 * m_samples_per_symbol);
            m_upchirp.resize(m_number_of_bins);
            m_downchirp.resize(m_number_of_bins);
            preamble_upchirps.resize(m_preamb_len * m_number_of_bins);
            preamble_raw_up.resize((m_preamb_len + 3) * m_samples_per_symbol);
            CFO_frac_correc.resize(m_number_of_bins);
            CFO_SFO_frac_correc.resize(m_number_of_bins);
            symb_corr.resize(m_number_of_bins);
            in_down.resize(m_number_of_bins);
            preamble_raw.resize(m_preamb_len * m_number_of_bins);
            net_id_samp.resize(m_samples_per_symbol * 2.5); // we should be able to move up to one quarter of symbol in each direction
            build_ref_chirps(&m_upchirp[0], &m_downchirp[0], m_sf);

            cx_in = new kiss_fft_cpx[m_number_of_bins];
            cx_out = new kiss_fft_cpx[m_number_of_bins];
            set_output_multiple(m_number_of_bins);
        }

        int frame_sync_impl::general_work(int noutput_items,
                                          gr_vector_int &ninput_items,
                                          gr_vector_const_void_star &input_items,
                                          gr_vector_void_star &output_items)
        {
            const gr_complex *in = (const gr_complex *)input_items[0];
            gr_complex *out = (gr_complex *)output_items[0];
            int items_to_output = 0;

            // check if there is enough space in the output buffer
            if (noutput_items < m_number_of_bins)
            {
                return 0;
            }

            float *sync_log_out = NULL;
            if (output_items.size() == 2)
            {
                sync_log_out = (float *)output_items[1];
                m_should_log = true;
            }
            else
                m_should_log = false;
            int nitems_to_process = ninput_items[0];

            std::vector<tag_t> tags;
            get_tags_in_window(tags, 0, 0, ninput_items[0], pmt::string_to_symbol("new_frame"));
            if (tags.size())
            {
                if (tags[0].offset != nitems_read(0))
                    nitems_to_process = tags[0].offset - nitems_read(0); // only use symbol until the next frame begin (SF might change)

                else
                {
                    if (tags.size() >= 2)
                        nitems_to_process = tags[1].offset - tags[0].offset;

                    pmt::pmt_t err = pmt::string_to_symbol("error");

                    int sf = pmt::to_long(pmt::dict_ref(tags[0].value, pmt::string_to_symbol("sf"), err));
                    set_sf(sf);

                    // std::cout<<"\nhamming_cr "<<tags[0].offset<<" - cr: "<<(int)m_cr<<"\n";
                }
            }

            // downsampling
            for (int ii = 0; ii < m_number_of_bins; ii++)
                in_down[ii] = in[(int)(m_os_factor / 2 + m_os_factor * ii - my_roundf(m_sto_frac * m_os_factor))];

            switch (m_state)
            {
            case DETECT:
            {
                bin_idx_new = get_symbol_val(&in_down[0], &m_downchirp[0]);

                if (abs(mod(abs(bin_idx_new - bin_idx) + 1, m_number_of_bins) - 1) <= 1 && bin_idx_new != -1) // look for consecutive reference upchirps(with a margin of ±1)
                {
                    if (symbol_cnt == 1 && bin_idx != -1)
                        preamb_up_vals[0] = bin_idx;

                    preamb_up_vals[symbol_cnt] = bin_idx_new;
                    memcpy(&preamble_raw[m_number_of_bins * symbol_cnt], &in_down[0], m_number_of_bins * sizeof(gr_complex));
                    memcpy(&preamble_raw_up[m_samples_per_symbol * symbol_cnt], &in[(int)(m_os_factor / 2)], m_samples_per_symbol * sizeof(gr_complex));

                    symbol_cnt++;
                }
                else
                {
                    memcpy(&preamble_raw[0], &in_down[0], m_number_of_bins * sizeof(gr_complex));
                    memcpy(&preamble_raw_up[0], &in[(int)(m_os_factor / 2)], m_samples_per_symbol * sizeof(gr_complex));

                    symbol_cnt = 1;
                }
                bin_idx = bin_idx_new;
                if (symbol_cnt == (int)(m_n_up_req))
                {
                    additional_upchirps = 0;
                    m_state = SYNC;
                    symbol_cnt = 0;
                    cfo_frac_sto_frac_est = false;
                    k_hat = most_frequent(&preamb_up_vals[0], preamb_up_vals.size());
                    memcpy(&net_id_samp[0], &in[int(0.75 * m_samples_per_symbol - k_hat * m_os_factor)], sizeof(gr_complex) * 0.25 * m_samples_per_symbol);

                    // perform the coarse synchronization
                    items_to_consume = m_os_factor * ((int)(m_number_of_bins - k_hat));
                }
                else
                    items_to_consume = m_samples_per_symbol;
                items_to_output = 0;
                break;
            }
            case SYNC:
            {
                items_to_output = 0;
                if (!cfo_frac_sto_frac_est)
                {
                    m_cfo_frac = estimate_CFO_frac_Bernier(&preamble_raw[m_number_of_bins - k_hat]);
                    m_sto_frac = estimate_STO_frac();
                    // create correction vector
                    for (int n = 0; n < m_number_of_bins; n++)
                    {
                        CFO_frac_correc[n] = gr_expj(-2 * M_PI * m_cfo_frac / m_number_of_bins * n);
                    }
                    cfo_frac_sto_frac_est = true;
                }
                items_to_consume = m_samples_per_symbol;
                // apply cfo correction
                volk_32fc_x2_multiply_32fc(&symb_corr[0], &in_down[0], &CFO_frac_correc[0], m_number_of_bins);

                bin_idx = get_symbol_val(&symb_corr[0], &m_downchirp[0]);
                switch (symbol_cnt)
                {
                case NET_ID1:
                {
                    if (bin_idx == 0 || bin_idx == 1 || bin_idx == m_number_of_bins - 1)
                    { // look for additional upchirps. Won't work if network identifier 1 equals 2^sf-1, 0 or 1!
                        memcpy(&net_id_samp[0], &in[(int)0.75 * m_samples_per_symbol], sizeof(gr_complex) * 0.25 * m_samples_per_symbol);
                        if (additional_upchirps >= 3)
                        {
                            std::rotate(preamble_raw_up.begin(), preamble_raw_up.begin() + m_samples_per_symbol, preamble_raw_up.end());
                            memcpy(&preamble_raw_up[m_samples_per_symbol * (m_n_up_req + 3)], &in[(int)(m_os_factor / 2) + k_hat * m_os_factor], m_samples_per_symbol * sizeof(gr_complex));
                        }
                        else
                        {
                            memcpy(&preamble_raw_up[m_samples_per_symbol * (m_n_up_req + additional_upchirps)], &in[(int)(m_os_factor / 2) + k_hat * m_os_factor], m_samples_per_symbol * sizeof(gr_complex));
                            additional_upchirps++;
                        }
                    }
                    else
                    { // network identifier 1 correct or off by one
                        symbol_cnt = NET_ID2;
                        memcpy(&net_id_samp[0.25 * m_samples_per_symbol], &in[0], sizeof(gr_complex) * m_samples_per_symbol);
                        net_ids[0] = bin_idx;
                    }
                    break;
                }
                case NET_ID2:
                {

                    symbol_cnt = DOWNCHIRP1;
                    memcpy(&net_id_samp[1.25 * m_samples_per_symbol], &in[0], sizeof(gr_complex) * (m_number_of_bins + 1) * m_os_factor);
                    net_ids[1] = bin_idx;

                    break;
                }
                case DOWNCHIRP1:
                {
                    memcpy(&net_id_samp[2.25 * m_samples_per_symbol], &in[0], sizeof(gr_complex) * 0.25 * m_samples_per_symbol);
                    symbol_cnt = DOWNCHIRP2;
                    break;
                }
                case DOWNCHIRP2:
                {
                    down_val = get_symbol_val(&symb_corr[0], &m_upchirp[0]);
                    memcpy(&additional_symbol_samp[0], &in[0], sizeof(gr_complex) * m_samples_per_symbol);
                    symbol_cnt = QUARTER_DOWN;
                    break;
                }
                case QUARTER_DOWN:
                {
                    memcpy(&additional_symbol_samp[m_samples_per_symbol], &in[0], sizeof(gr_complex) * m_samples_per_symbol);
                    if (down_val < m_number_of_bins / 2)
                    {
                        m_cfo_int = floor(down_val / 2);
                    }
                    else
                    {
                        m_cfo_int = floor(double(down_val - (int)m_number_of_bins) / 2);
                    }

                    // correct STOint and CFOint in the preamble upchirps
                    std::rotate(preamble_upchirps.begin(), preamble_upchirps.begin() + mod(m_cfo_int, m_number_of_bins), preamble_upchirps.end());

                    std::vector<gr_complex> CFO_int_correc;
                    CFO_int_correc.resize((m_n_up_req + additional_upchirps) * m_number_of_bins);
                    for (int n = 0; n < (m_n_up_req + additional_upchirps) * m_number_of_bins; n++)
                    {
                        CFO_int_correc[n] = gr_expj(-2 * M_PI * (m_cfo_int) / m_number_of_bins * n);
                    }

                    volk_32fc_x2_multiply_32fc(&preamble_upchirps[0], &preamble_upchirps[0], &CFO_int_correc[0], up_symb_to_use * m_number_of_bins);

                    // correct SFO in the preamble upchirps

                    sfo_hat = float((m_cfo_int + m_cfo_frac) * m_bw) / m_center_freq;
                    double clk_off = sfo_hat / m_number_of_bins;
                    double fs = m_bw;
                    double fs_p = m_bw * (1 - clk_off);
                    int N = m_number_of_bins;
                    std::vector<gr_complex> sfo_corr_vect;
                    sfo_corr_vect.resize((m_n_up_req + additional_upchirps) * m_number_of_bins, 0);
                    for (int n = 0; n < (m_n_up_req + additional_upchirps) * m_number_of_bins; n++)
                    {
                        sfo_corr_vect[n] = gr_expj(-2 * M_PI * (pow(mod(n, N), 2) / 2 / N * (m_bw / fs_p * m_bw / fs_p - m_bw / fs * m_bw / fs) + (std::floor((float)n / N) * (m_bw / fs_p * m_bw / fs_p - m_bw / fs_p) + m_bw / 2 * (1 / fs - 1 / fs_p)) * mod(n, N)));
                    }

                    volk_32fc_x2_multiply_32fc(&preamble_upchirps[0], &preamble_upchirps[0], &sfo_corr_vect[0], up_symb_to_use * m_number_of_bins);

                    float tmp_sto_frac = estimate_STO_frac(); // better estimation of sto_frac in the beginning of the upchirps
                    float diff_sto_frac = m_sto_frac - tmp_sto_frac;

                    if (abs(diff_sto_frac) <= float(m_os_factor - 1) / m_os_factor) // avoid introducing off-by-one errors by estimating fine_sto=-0.499 , rough_sto=0.499
                        m_sto_frac = tmp_sto_frac;

                    // get SNR estimate from preamble
                    // downsample preab_raw
                    std::vector<gr_complex> corr_preamb;
                    corr_preamb.resize((m_n_up_req + additional_upchirps) * m_number_of_bins, 0);
                    // apply sto correction
                    for (int i = 0; i < (m_n_up_req + additional_upchirps) * m_number_of_bins; i++)
                    {
                        corr_preamb[i] = preamble_raw_up[m_os_factor * (m_number_of_bins - k_hat + i) - int(my_roundf(m_os_factor * m_sto_frac))];
                    }
                    std::rotate(corr_preamb.begin(), corr_preamb.begin() + mod(m_cfo_int, m_number_of_bins), corr_preamb.end());
                    // apply cfo correction
                    volk_32fc_x2_multiply_32fc(&corr_preamb[0], &corr_preamb[0], &CFO_int_correc[0], (m_n_up_req + additional_upchirps) * m_number_of_bins);
                    for (int i = 0; i < (m_n_up_req + additional_upchirps); i++)
                    {
                        volk_32fc_x2_multiply_32fc(&corr_preamb[m_number_of_bins * i], &corr_preamb[m_number_of_bins * i], &CFO_frac_correc[0], m_number_of_bins);
                    }

                    // //apply sfo correction
                    volk_32fc_x2_multiply_32fc(&corr_preamb[0], &corr_preamb[0], &sfo_corr_vect[0], (m_n_up_req + additional_upchirps) * m_number_of_bins);

                    float snr_est = 0;
                    for (int i = 0; i < up_symb_to_use; i++)
                    {
                        snr_est += determine_snr(&corr_preamb[i * m_number_of_bins]);
                    }
                    snr_est /= up_symb_to_use;

                    // update sto_frac to its value at the beginning of the net id
                    m_sto_frac += sfo_hat * m_preamb_len;
                    // ensure that m_sto_frac is in [-0.5,0.5]
                    if (abs(m_sto_frac) > 0.5)
                    {
                        m_sto_frac = m_sto_frac + (m_sto_frac > 0 ? -1 : 1);
                    }
                    // decim net id according to new sto_frac and sto int
                    std::vector<gr_complex> net_ids_samp_dec;
                    net_ids_samp_dec.resize(2 * m_number_of_bins, 0);
                    // start_off gives the offset in the net_id_samp vector required to be aligned in time (CFOint is equivalent to STOint since upchirp_val was forced to 0)
                    int start_off = (int)m_os_factor / 2 - (my_roundf(m_sto_frac * m_os_factor)) + m_os_factor * (.25 * m_number_of_bins + m_cfo_int);
                    for (int i = 0; i < m_number_of_bins * 2; i++)
                    {
                        net_ids_samp_dec[i] = net_id_samp[start_off + i * m_os_factor];
                    }
                    volk_32fc_x2_multiply_32fc(&net_ids_samp_dec[0], &net_ids_samp_dec[0], &CFO_int_correc[0], 2 * m_number_of_bins);

                    // correct CFO_frac in the network ids
                    volk_32fc_x2_multiply_32fc(&net_ids_samp_dec[0], &net_ids_samp_dec[0], &CFO_frac_correc[0], m_number_of_bins);
                    volk_32fc_x2_multiply_32fc(&net_ids_samp_dec[m_number_of_bins], &net_ids_samp_dec[m_number_of_bins], &CFO_frac_correc[0], m_number_of_bins);

                    int netid1 = get_symbol_val(&net_ids_samp_dec[0], &m_downchirp[0]);
                    int netid2 = get_symbol_val(&net_ids_samp_dec[m_number_of_bins], &m_downchirp[0]);
                    one_symbol_off = 0;

                    if (abs(netid1 - (int32_t)m_sync_words[0]) > 2) // wrong id 1, (we allow an offset of 2)
                    {

                        // check if we are in fact checking the second net ID and that the first one was considered as a preamble upchirp
                        if (abs(netid1 - (int32_t)m_sync_words[1]) <= 2)
                        {
                            net_id_off = netid1 - (int32_t)m_sync_words[1];
                            for (int i = m_preamb_len - 2; i < (m_n_up_req + additional_upchirps); i++)
                            {
                                if (get_symbol_val(&corr_preamb[i * m_number_of_bins], &m_downchirp[0]) + net_id_off == m_sync_words[0]) // found the first netID
                                {
                                    one_symbol_off = 1;
                                    if (net_id_off != 0 && abs(net_id_off) > 1)
                                        std::cout << RED << "[frame_sync_impl.cc] net id offset >1: " << net_id_off << RESET << std::endl;
                                    if (m_should_log)
                                        off_by_one_id = net_id_off != 0;
                                    items_to_consume = -m_os_factor * net_id_off;
                                    // the first symbol was mistaken for the end of the downchirp. we should correct and output it.

                                    int start_off = (int)m_os_factor / 2 - my_roundf(m_sto_frac * m_os_factor) + m_os_factor * (0.25 * m_number_of_bins + m_cfo_int);
                                    for (int i = start_off; i < 1.25 * m_samples_per_symbol; i += m_os_factor)
                                    {

                                        out[int((i - start_off) / m_os_factor)] = additional_symbol_samp[i];
                                    }
                                    items_to_output = m_number_of_bins;
                                    m_state = SFO_COMPENSATION;
                                    symbol_cnt = 1;
                                    frame_cnt++;
                                }
                            }
                            if (!one_symbol_off)
                            {
                                m_state = DETECT;
                                symbol_cnt = 1;
                                items_to_output = 0;
                                k_hat = 0;
                                m_sto_frac = 0;
                                items_to_consume = 0;
                            }
                        }
                        else
                        {
                            m_state = DETECT;
                            symbol_cnt = 1;
                            items_to_output = 0;
                            k_hat = 0;
                            m_sto_frac = 0;
                            items_to_consume = 0;
                        }
                    }
                    else // net ID 1 valid
                    {
                        net_id_off = netid1 - (int32_t)m_sync_words[0];
                        if (mod(netid2 - net_id_off, m_number_of_bins) != (int32_t)m_sync_words[1]) // wrong id 2
                        {
                            m_state = DETECT;
                            symbol_cnt = 1;
                            items_to_output = 0;
                            k_hat = 0;
                            m_sto_frac = 0;
                            items_to_consume = 0;
                        }
                        else
                        {
                            if (net_id_off != 0 && abs(net_id_off) > 1)
                                std::cout << RED << "[frame_sync_impl.cc] net id offset >1: " << net_id_off << RESET << std::endl;
                            if (m_should_log)
                                off_by_one_id = net_id_off != 0;
                            items_to_consume = -m_os_factor * net_id_off;
                            m_state = SFO_COMPENSATION;
                            frame_cnt++;
                        }
                    }
                    if (m_state != DETECT)
                    {
                        // update sto_frac to its value at the payload beginning
                        m_sto_frac += sfo_hat * 4.25;
                        sfo_cum = ((m_sto_frac * m_os_factor) - my_roundf(m_sto_frac * m_os_factor)) / m_os_factor;

                        pmt::pmt_t frame_info = pmt::make_dict();
                        frame_info = pmt::dict_add(frame_info, pmt::intern("is_header"), pmt::from_bool(true));
                        frame_info = pmt::dict_add(frame_info, pmt::intern("cfo_int"), pmt::mp((long)m_cfo_int));
                        frame_info = pmt::dict_add(frame_info, pmt::intern("cfo_frac"), pmt::mp((float)m_cfo_frac));
                        frame_info = pmt::dict_add(frame_info, pmt::intern("sf"), pmt::mp((long)m_sf));

                        add_item_tag(0, nitems_written(0), pmt::string_to_symbol("frame_info"), frame_info);

                        m_received_head = false;
                        items_to_consume += m_samples_per_symbol / 4 + m_os_factor * m_cfo_int;
                        symbol_cnt = one_symbol_off;
                        float snr_est2 = 0;

                        if (m_should_log)
                        {
                            // estimate SNR

                            for (int i = 0; i < up_symb_to_use; i++)
                            {
                                snr_est2 += determine_snr(&preamble_upchirps[i * m_number_of_bins]);
                            }
                            snr_est2 /= up_symb_to_use;
                            float cfo_log = m_cfo_int + m_cfo_frac;
                            float sto_log = k_hat - m_cfo_int + m_sto_frac;
                            float srn_log = snr_est;
                            float sfo_log = sfo_hat;

                            sync_log_out[0] = srn_log;
                            sync_log_out[1] = cfo_log;
                            sync_log_out[2] = sto_log;
                            sync_log_out[3] = sfo_log;
                            sync_log_out[4] = off_by_one_id;
                            produce(1, 5);
                        }
#ifdef PRINT_INFO

                        std::cout << "[frame_sync_impl.cc] " << frame_cnt << " CFO estimate: " << m_cfo_int + m_cfo_frac << ", STO estimate: " << k_hat - m_cfo_int + m_sto_frac << " snr est: " << snr_est << std::endl;
#endif
                    }
                }
                }

                break;
            }
            case SFO_COMPENSATION:
            {
                // transmit only useful symbols (at least 8 symbol for PHY header)

                if (symbol_cnt < 8 || (symbol_cnt < m_symb_numb && m_received_head))
                {
                    // output downsampled signal (with no STO but with CFO)
                    memcpy(&out[0], &in_down[0], m_number_of_bins * sizeof(gr_complex));
                    items_to_consume = m_samples_per_symbol;

                    //   update sfo evolution
                    if (abs(sfo_cum) > 1.0 / 2 / m_os_factor)
                    {
                        items_to_consume -= (-2 * signbit(sfo_cum) + 1);
                        sfo_cum -= (-2 * signbit(sfo_cum) + 1) * 1.0 / m_os_factor;
                    }

                    sfo_cum += sfo_hat;

                    items_to_output = m_number_of_bins;
                    symbol_cnt++;
                }
                else if (!m_received_head)
                { // Wait for the header to be decoded
                    items_to_consume = 0;
                    items_to_output = 0;
                }
                else
                {
                    m_state = DETECT;
                    symbol_cnt = 1;
                    items_to_consume = m_samples_per_symbol;
                    items_to_output = 0;
                    k_hat = 0;
                    m_sto_frac = 0;
                }
                break;
            }
            default:
            {
                std::cerr << "[LoRa sync] WARNING : No state! Shouldn't happen\n";
                break;
            }
            }
            consume_each(items_to_consume);
            produce(0, items_to_output);
            return WORK_CALLED_PRODUCE;
        }
    } /* namespace lora_sdr */
} /* namespace gr */
