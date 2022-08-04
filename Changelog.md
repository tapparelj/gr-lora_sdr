# v0.4.0
- Port to GNU Radio 3.10
- Added hierarchical blocks for easy Tx and Rx utilisation
- fixed issue with buffer sizes for spreading factor 12
- move sample flowgraphs from apps to examples

# v0.3.0
- Added soft-decision decoding as an option
- Added choice of different sampling rate and bandwidth for both transmitter and receiver
- Added callback to set coding rate and spreading factor of the transmitter during flowgraph runtime
- Updated documentation of each block
- Cleaned legacy unused blocks

# v0.2.0
 - Update to GNU Radio 3.8.2
 - Supports custom network identifiers/sync words
 - Improved message passing between blocks
 - Fixed bug for negative CFO

# v0.1.0
- Initial transceiver supporting 
    - Spreading factors: 7-12 (without reduce rate mode)
    - Coding rates: 0-4
    - Implicit and explicit header mode
    - Payload length: 1-255 bytes
    - Verification of payload CRC
    - Verification of explicit header checksum

