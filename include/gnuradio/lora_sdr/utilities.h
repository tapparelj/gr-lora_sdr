#ifndef UTILITIES_H
#define UTILITIES_H

#include <cstdint>
#include <string.h>
#include <iomanip>
#include <numeric>
#include <gnuradio/expj.h>
#include <volk/volk.h>
#include <algorithm>

// Undefine VOID macro (happens on Windows) so we can use VOID as a symbol type below
#ifdef VOID
#undef VOID
#endif

#define print(message) std::cout<< message <<std::endl
namespace gr {
    namespace lora_sdr {

        // #define THREAD_MEASURE
        
        #define RESET   "\033[0m"
        #define RED     "\033[31m"      /* Red */

        #define MIN_SF  5 //minimum and maximum SF
        #define MAX_SF  12 

        typedef double LLR;    ///< Log-Likelihood Ratio type
        //typedef long double LLR; // 16 Bytes 

        enum Symbol_type {
            VOID,
            UPCHIRP,
            SYNC_WORD,
            DOWNCHIRP,
            QUARTER_DOWN,
            PAYLOAD,
            UNDETERMINED
        };
        #define LDRO_MAX_DURATION_MS 16
        enum ldro_mode {
            DISABLE,
            ENABLE,
            AUTO
        };
        /**
         *  \brief  return the modulus a%b between 0 and (b-1)
         */
        inline long mod(long a, long b)
        { return (a%b+b)%b; }

        inline double double_mod(double a, long b)
        { return fmod(fmod(a,b)+b,b);}

        /**
         *  \brief  Convert an integer into a MSB first vector of bool
         *
         *  \param  integer
         *          The integer to convert
         *  \param  n_bits
         *          The output number of bits
         */
        inline std::vector<bool> int2bool(unsigned int integer,uint8_t n_bits){
                std::vector<bool> vec(n_bits,0);
                int j=n_bits;
                for(int i=0 ;i<n_bits;i++) {
                    vec[--j]=((integer>>i)& 1);
                }
            return vec;

        };
        /**
         *  \brief  Convert a MSB first vector of bool to a integer
         *
         *  \param  b
         *          The boolean vector to convert
         */
        inline uint32_t bool2int(std::vector<bool> b){
            uint32_t integer = std::accumulate(b.begin(), b.end(), 0, [](int x, int y) { return (x << 1) + y; });
            return integer;
        };
         /**
         *  \brief  Return an modulated upchirp using s_f=bw
         *
         *  \param  chirp
         *          The pointer to the modulated upchirp
         *  \param  id
         *          The number used to modulate the chirp
         * \param   sf
         *          The spreading factor to use
         * \param os_factor
         *          The oversampling factor used to generate the upchirp
         */
        inline void build_upchirp(gr_complex* chirp, uint32_t id, uint8_t sf, uint8_t os_factor = 1){
            double N = (1 << sf)  ;
            int n_fold = N* os_factor - id*os_factor;
            for(int n = 0; n < N* os_factor; n++){
                if(n<n_fold)
                    chirp[n] = gr_complex(1.0,0.0)*gr_expj(2.0*M_PI *(n*n/(2*N)/pow(os_factor,2)+(id/N-0.5)*n/os_factor));
                else
                    chirp[n] = gr_complex(1.0,0.0)*gr_expj(2.0*M_PI *(n*n/(2*N)/pow(os_factor,2)+(id/N-1.5)*n/os_factor));

            }
        }

        /**
         *  \brief  Return the reference chirps using s_f=bw
         *
         *  \param  upchirp
         *          The pointer to the reference upchirp
         *  \param  downchirp
         *          The pointer to the reference downchirp
         * \param   sf
         *          The spreading factor to use
         */
        inline void build_ref_chirps(gr_complex* upchirp, gr_complex* downchirp, uint8_t sf, uint8_t os_factor = 1){
            double N = (1 << sf);
            build_upchirp(upchirp,0,sf,os_factor);
            volk_32fc_conjugate_32fc(&downchirp[0], &upchirp[0], N*os_factor);

            // for(uint32_t n = 0; n < N ;n++){
            //     //the scaling factor of 0.9 is here to avoid to saturate the USRP_SINK
            //     upchirp[n] =  gr_complex(0.9f, 0.0f)*gr_expj(2.0 * M_PI * (n*n/(2*N)-0.5*n));
            //     downchirp[n] = gr_complex(0.9f, 0.0f)*gr_expj(-2.0 * M_PI * (n*n/(2*N)-0.5*n));
            // }
        }
         // find most frequency number in vector
        inline int most_frequent(int arr[], int n)
        {
            // Insert all elements in hash.
            std::unordered_map<int, int> hash;
            for (int i = 0; i < n; i++)
                hash[arr[i]]++;
        
            // find the max frequency
            int max_count = 0, res = -1;
            for (auto i : hash) {
                if (max_count < i.second) {
                    res = i.first;
                    max_count = i.second;
                }
            }
        
            return res;
        }

       
        inline std::string random_string(int Nbytes){
        const char* charmap = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        const size_t charmapLength = strlen(charmap);
        auto generator = [&](){ return charmap[rand()%charmapLength]; };
        std::string result;
        result.reserve(Nbytes);
        std::generate_n(std::back_inserter(result), Nbytes, generator);
        return result;
    }

        /**
         * @brief Long interleaving (LI) of the SX128x coding rates 4/6LI and 4/8LI: bit layout.
         *
         * In LI mode the n_cw codewords of a frame form a single interleaving block.
         * The codewords, in this module's layout (4 + cr bits, MSB first, as hamming_enc
         * produces them), are read out bit-position-major: bit 0 (MSB) of every
         * codeword, then bit 1, and so on. The resulting stream fills the symbols least
         * significant bit first. At SF7 and above the first 8 symbols carry sf - 2 bits
         * (reduced rate, like the first block of a regular frame); all other symbols
         * carry sf bits. The last symbol is padded with copies of stream bits 1, 2, ...
         * Reverse-engineered from SX1280 frames of ExpressLRS 4.1 at 2.4 GHz
         * (812.5 kHz, implicit header, no CRC): 4/6LI at SF5 with 8-byte payloads, 4/8LI
         * at SF5, SF6, SF7 and SF8 with 8- and 13-byte payloads. 4/5LI and SF9 to SF12
         * are assumed to follow the same rule but are not verified.
         */
        inline uint32_t li_reduced_symbols(uint8_t sf)
        {
            return sf >= 7 ? 8 : 0;
        }

        inline uint32_t li_symbol_count(uint32_t n_cw, uint8_t cr, uint8_t sf)
        {
            const uint32_t bits = (4 + cr) * n_cw;
            const uint32_t reduced_bits = li_reduced_symbols(sf) * (sf - 2);
            const uint32_t rest = bits > reduced_bits ? bits - reduced_bits : 0;
            return li_reduced_symbols(sf) + (rest + sf - 1) / sf;
        }

        /// Position of codeword bit `cw_bit` (MSB-first index) of codeword `cw_idx` in the LI stream.
        inline uint32_t li_stream_index(uint32_t cw_idx, uint8_t cw_bit, uint32_t n_cw)
        {
            return cw_bit * n_cw + cw_idx;
        }

        /// Symbol and LSB-first bit index within that symbol's value (sf - 2 bits for a reduced-rate symbol) of LI stream position `t`.
        inline void li_stream_position(uint32_t t, uint8_t sf, uint32_t &symbol, uint8_t &bit)
        {
            const uint32_t reduced_bits = li_reduced_symbols(sf) * (sf - 2);
            if (t < reduced_bits)
            {
                symbol = t / (sf - 2);
                bit = t % (sf - 2);
            }
            else
            {
                symbol = li_reduced_symbols(sf) + (t - reduced_bits) / sf;
                bit = (t - reduced_bits) % sf;
            }
        }
    }
}
#endif /* UTILITIES_H */
