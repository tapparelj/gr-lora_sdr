
#include <gnuradio/io_signature.h>
#include "data_source_impl.h"
#include <gnuradio/block.h>

namespace gr {
  namespace lora_sdr {

    data_source::sptr
    data_source::make(int pay_len,int n_frames)
    {
      return gnuradio::get_initial_sptr
        (new data_source_impl(pay_len, n_frames));
    }

    /*
     * The private constructor
     */
    data_source_impl::data_source_impl(int pay_len,int n_frames)
      : gr::sync_block("data_source",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
        m_n_frames = n_frames;
        m_pay_len = pay_len;
        frame_cnt = -5;// let some time to the Rx to start listening
        message_port_register_in(pmt::mp("trigg"));
        set_msg_handler(pmt::mp("trigg"),boost::bind(&data_source_impl::trigg_handler, this, _1));

        message_port_register_out(pmt::mp("msg"));
    }

    /*
     * Our virtual destructor.
     */
    data_source_impl::~data_source_impl()
    {}
    std::string data_source_impl::random_string(int Nbytes){
        const char* charmap = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        const size_t charmapLength = strlen(charmap);
        auto generator = [&](){ return charmap[rand()%charmapLength]; };
        std::string result;
        result.reserve(Nbytes);
        std::generate_n(std::back_inserter(result), Nbytes, generator);
        return result;
    }
    void data_source_impl::trigg_handler(pmt::pmt_t msg){
        if(frame_cnt<m_n_frames&&frame_cnt>=0){//send a new payload
            std::string str = random_string(m_pay_len);
            message_port_pub(pmt::intern("msg"),pmt::mp(str));

            //print once in every 50 frames information about the number of frames
            std::string msg_info_1 = "INFO:Frame : ";
            std::string msg_info_2 = "/";
            if(!mod(frame_cnt,50))
                std::string msg = msg_info_1 + std::to_string(frame_cnt) + msg_info_2 + std::to_string(m_n_frames);
                GR_LOG_INFO(this->d_logger, msg);
            frame_cnt++;
        }
        else if(frame_cnt<m_n_frames)//wait some time for Rx to start listening
            frame_cnt++;
        else if(frame_cnt==m_n_frames){
            std::string msg_info_1 = "INFO:Done, generated : ";
            std::string msg_info_2 = " frames";
            std::string msg = msg_info_1 + std::to_string(m_n_frames) + msg_info_2;
            GR_LOG_INFO(this->d_logger, msg);
            frame_cnt++;
        }
    }

    int data_source_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      return 0;
    }

  } /* namespace lora_sdr */
} /* namespace gr */
