/**
 * @file frame_detector_impl.cc
 * @author Martyn van Dijke (martijnvdijke600@gmail.com)
 * @brief
 * @version 0.1
 * @date 2021-03-23
 *
 *
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "frame_detector_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace lora_sdr {

frame_detector::sptr frame_detector::make() {
  return gnuradio::get_initial_sptr(new frame_detector_impl());
}

/**
 * @brief Construct a new frame detector impl::frame detector impl object
 *
 */
frame_detector_impl::frame_detector_impl()
    : gr::block("frame_detector",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(1, 1, sizeof(gr_complex))) {}

/**
 * @brief Destroy the frame detector impl::frame detector impl object
 *
 */
frame_detector_impl::~frame_detector_impl() {}

/**
 * @brief
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : required input items (how many items must we
 * have for we can do something)
 */
void frame_detector_impl::forecast(int noutput_items,
                                   gr_vector_int &ninput_items_required) {
  /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
}

/**
 * @brief General work function.
 * Main gnuradio function that does the heavy lifting
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input items
 * @param output_items : output items
 * @return int
 */
int frame_detector_impl::general_work(int noutput_items,
                                      gr_vector_int &ninput_items,
                                      gr_vector_const_void_star &input_items,
                                      gr_vector_void_star &output_items) {
  const gr_complex *in = (const gr_complex *)input_items[0];
  gr_complex *out = (gr_complex *)output_items[0];

  // Do <+signal processing+>
  // Tell runtime system how many input items we consumed on
  // each input stream.
  consume_each(noutput_items);

  // Tell runtime system how many output items we produced.
  return noutput_items;
}

} /* namespace lora_sdr */
} /* namespace gr */
