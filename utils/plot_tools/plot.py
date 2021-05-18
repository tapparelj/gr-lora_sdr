# Simple test file to plot complex data stream

import argparse

# import actual plot scripts
from src.plot_data import plot_data
from src.plot_fft_base import plot_fft_base
from src.plot_psd_base import plot_psd_base
from src.plot_iq import plot_iq
from src.plot_lora import plot_lora

def main():
    description = "gr-lora_sdr complex data stream plotter"
    parser = argparse.ArgumentParser(conflict_handler="resolve", description=description)
    parser.add_argument("-d", "--data-type", default="complex64",
                        choices=("complex64", "float32", "uint32", "int32", "uint16",
                                 "int16", "uint8", "int8"),
                        help="Specify the data type [default=%(default)r]")
    parser.add_argument("-B", "--block", type=int, default=1000,
                        help="Specify the block size [default=%(default)r]")
    parser.add_argument("-s", "--start", type=int, default=0,
                        help="Specify where to start in the file [default=%(default)r]")
    parser.add_argument("-R", "--sample-rate", type=float, default=1.0,
                        help="Set the sampler rate of the data [default=%(default)r]")
    parser.add_argument("--psd-size", type=int, default=1024,
                        help="Set the size of the PSD FFT [default=%(default)r]")
    parser.add_argument("--spec-size", type=int, default=256,
                        help="Set the size of the spectrogram FFT [default=%(default)r]")
    parser.add_argument("-S", "--enable-spec", action="store_true",
                        help="Turn on plotting the spectrogram [default=%(default)r]")
    parser.add_argument("-sf", "--spreading-factor", type=int, default=7,
                        help="Spreading factor used [default=%(default)r]")
    parser.add_argument("file", metavar="FILE", nargs='+',
                        help="Input file with samples")
    parser.add_argument("-m", "--mode", type=str, default="plot_data",
                        choices=("data", "fft", "psd", "iq", "lora"),
                        help="Specify the plot to make")
    # parser = plot_data.setup_options()
    args = parser.parse_args()
    if args.mode == "data":
        plot_data(None, args.file, args)
    if args.mode == "fft":
        plot_fft_base(None, args.file[0], args)
    if args.mode == "psd":
        plot_psd_base(None, args.file[0], args)
    if args.mode == "iq":
        plot_iq(args.file[0], args)
    if args.mode == "lora":
        plot_lora(None, args.file[0], args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
