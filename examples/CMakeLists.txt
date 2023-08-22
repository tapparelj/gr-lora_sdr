# This file is a part of gr-lora_sdr
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

install(
    FILES lora_RX.grc
          lora_TX.grc
          tx_rx_functionality_check.grc
          tx_rx_hier_functionality_check.grc
          tx_rx_simulation.grc
          tx_rx_usrp.grc
    DESTINATION ${GR_PKG_DATA_DIR}/examples)
