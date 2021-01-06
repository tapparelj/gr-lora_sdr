#ifndef INCLUDED_LORA_SDR_WHITENING_H
#define INCLUDED_LORA_SDR_WHITENING_H

#include <gnuradio/sync_block.h>
#include <lora_sdr/api.h>

namespace gr {
namespace lora_sdr {

/*!
 * \brief Whiten the input data
 * For more information about the implementation visit whitening_impl
 * \ingroup lora_sdr
 *
 */
class LORA_SDR_API whitening : virtual public gr::sync_block {
public:
  typedef boost::shared_ptr<whitening> sptr;

  /*!
   * \brief Return a shared_ptr to a new instance of lora_sdr::whitening.
   *
   * To avoid accidental use of raw pointers, lora_sdr::whitening's
   * constructor is in a private implementation
   * class. lora_sdr::whitening::make is the public interface for
   * creating new instances.
   */
  static sptr make();
};

} // namespace lora_sdr
} // namespace gr

#endif /* INCLUDED_LORA_SDR_WHITENING_H */
