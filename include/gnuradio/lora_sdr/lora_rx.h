#ifndef LORA_RX_HPP
#define LORA_RX_HPP
/********************
GNU Radio C++ Flow Graph Header File

Title: lora_rx
GNU Radio version: v3.11.0.0git-645-g506e68df
********************/

/********************
** Create includes
********************/
#include <gnuradio/top_block.h>
#include <gnuradio/analog/sig_source.h>
#include <gnuradio/blocks/multiply.h>


#include <boost/program_options.hpp>

namespace gr {
  namespace lora_sdr {
  
  class LORA_SDR_API lora_sdr_rx : public gr::heir_block2 {
  

typedef std::shared_ptr<mult> mult_sptr;
mult_sptr make_mult();

class mult : public hier_block2 {

private:
    blocks::multiply_cc::sptr blocks_multiply_xx_0;
    analog::sig_source_c::sptr analog_const_source_x_0;

// Parameters:
    gr_complex mult_amount = {0, 0};


public:
    mult(gr_complex mult_amount);
    ~mult();

    gr_complex get_mult_amount () const;
    void set_mult_amount(gr_complex mult_amount);

};

mult::mult (gr_complex mult_amount) : hier_block2("mult_block",
                gr::io_signature::make(1, 1, sizeof(gr_complex)*1),
                gr::io_signature::make(1, 1, sizeof(gr_complex)*1)
        ) {


// Blocks:
    {
        this->blocks_multiply_xx_0 = blocks::multiply_cc::make(1);
    }
    {
        this->analog_const_source_x_0 = analog::sig_source_c::make(0, analog::GR_CONST_WAVE, 0, 0, mult_amount);
    }

// Connections:
    hier_block2::connect(this->analog_const_source_x_0, 0, this->blocks_multiply_xx_0, 1);
    hier_block2::connect(this->blocks_multiply_xx_0, 0, self(), 0);
    hier_block2::connect(self(), 0, this->blocks_multiply_xx_0, 0);
}

mult::~mult () {}

// Callbacks:
gr_complex mult::get_mult_amount () const {
    return this->mult_amount;
}

void mult::set_mult_amount (gr_complex mult_amount) {
    this->mult_amount = mult_amount;
    this->analog_const_source_x_0->set_offset(this->mult_amount);
}

mult_sptr
make_mult()
{
    return gnuradio::get_initial_sptr(new mult(gr_complex(2, 0)));
}
#endif

