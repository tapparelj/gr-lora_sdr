#ifndef UTILITIES_H
#define UTILITIES_H

#include <cstdint>
#include <string.h>
#include <iomanip>
#include <numeric>
#include <gnuradio/expj.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <volk/volk.h>
#include <algorithm>

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

            // for(uint n = 0; n < N ;n++){
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
    }
}
#endif /* UTILITIES_H */
