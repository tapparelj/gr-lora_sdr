#ifndef UTILITIES_H
#define UTILITIES_H

#include <cstdint>
#include <string.h>
#include <iomanip>
#include <numeric>
#include <gnuradio/expj.h>

namespace gr {
    namespace lora_sdr {
        /**
         *  \brief  return the modulus a%b between 0 and (b-1)
         */
        inline long mod(long a, long b)
        { return (a%b+b)%b; }
        /**
         *  \brief  Convert an integer into a MSB first vector of bool
         *
         *  \param  integer
         *          The integer to convert
         *  \param  n_bits
         *          The output number of bits
         */
        inline std::vector<bool> int2bool(uint integer,uint8_t n_bits){
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
         *  \brief  Return the reference chirps using s_f=bw
         *
         *  \param  upchirp
         *          The pointer to the reference upchirp
         *  \param  downchirp
         *          The pointer to the reference downchirp
         * \param   sf
         *          The spreading factor to use
         */
        inline void build_ref_chirps(gr_complex* upchirp, gr_complex* downchirp, uint8_t sf){
            double N = (1 << sf);
            for(uint n = 0; n < N ;n++){
                //the scaling factor of 0.9 is here to avoid to saturate the USRP_SINK
                upchirp[n] =  gr_complex(0.9f, 0.0f)*gr_expj(2.0 * M_PI * (n*n/(2*N)-0.5*n));
                downchirp[n] = gr_complex(0.9f, 0.0f)*gr_expj(-2.0 * M_PI * (n*n/(2*N)-0.5*n));
            }
        }
        /**
         *  \brief  Return an modulated upchirp using s_f=bw
         *
         *  \param  chirp
         *          The pointer to the modulated upchirp
         *  \param  id
         *          The number used to modulate the chirp
         * \param   sf
         *          The spreading factor to use
         */
        inline void build_upchirp(gr_complex* chirp, uint32_t id, uint8_t sf){
            double N = 1 << sf;
            for(uint n = 0; n < N; n++){
                //the scaling factor of 0.9 is here to avoid to saturate the USRP_SINK
                chirp[n]=gr_complex(0.9f, 0.0f)*gr_expj(2.0 * M_PI *(n*n/(2*N)+(id/N-0.5)*n));
            }
        }
    }
}
#endif /* UTILITIES_H */
