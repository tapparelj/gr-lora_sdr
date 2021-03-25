# Simple test file to plot complex data stream

import argparse

# import actual plot scripts
from src.plot_data import plot_data
from src.plot_fft_base import plot_fft_base
from src.plot_psd_base import plot_psd_base
from src.plot_iq import plot_iq
from src.plot_lora import plot_lora

# def open_file(filename):
#     data = np.fromfile(open(filename), dtype=np.complex64)
#     return data
#
#
# def plot_fft(data, samp_rate):
#     # Number of samplepoints
#     sp = np.fft.fft(data)
#     freq = np.fft.fftfreq(data.shape[-1])
#     plt.plot(freq, sp.real, freq, sp.imag)
#     plt.show()
#
#
# def plot_spectogram(data, samp_rate):
#     n = data.size
#     NFFT = 1024
#     dt = 1 / samp_rate
#     t_end = 0.005
#     end = int(t_end / dt)
#     data = np.resize(np.abs(data), end)
#     # time vector
#     # t = np.arange(0, t_end, dt)
#     fig, ax = plt.subplots()
#     cmap = plt.get_cmap('viridis')
#     vmin = 20 * np.log10(np.max(data)) - 40  # hide anything below -40 dBc
#     cmap.set_under(color='k', alpha=None)
#     pxx, freq, t, cax = ax.specgram(data, NFFT=NFFT, Fs=2 * int(samp_rate), mode='magnitude', vmin=vmin, cmap=cmap)
#     fig.colorbar(cax)
#     ax.ticklabel_format(axis='both', style='sci')
#     plt.xlabel("Time")
#     plt.ylabel("Frequency")
#     plt.show()
#     print("test")
#
#
# def plot_power_fft_time(data, samp_rate):
#     # number of samples
#     n = data.size
#     # fft version of input data
#     y_real = np.fft.rfft(data.real)
#     y_imag = np.fft.rfft(data.imag)
#     # end time
#     t_end = (1 / samp_rate) * n
#     # test value -> in ms range
#     t_end = 0.05
#     # time vector
#     t = np.arange(0, t_end, 1 / samp_rate)
#     # frequencies vector
#     f = np.arange(0, n) * (samp_rate * n)
#     power_real = np.power(np.abs(y_real), 2) / n
#     power_real = np.resize(power_real, t.size)
#     f = np.resize(f, t.size)
#
#     power_freq = power_real / f
#     print("test")
#
#     #
#
#     #
#     # # power_imag = np.power(np.abs(y_imag), 2) / n
#     # # plt.plot(abs(power_real),label="real")
#     # # plt.plot(abs(power_imag),label="imag")
#     # a = np.diag(range(15))
#     # # test = f[:,0]
#     # # test = np.ndarray.tolist(t)
#     # # ftes = np.ndarray.tolist(f)
#     # # a = np.mat()
#     # a = np.concatenate([t,f])
#     # plt.matshow(a)
#     # plt.xlabel("Time")
#     # plt.ylabel("Freqency")
#     # plt.show()
#
#
# def plot_power_fft_bin(data, samp_rate):
#     # number of samples
#     n = data.size
#     # fft version of input data
#     y_real = np.fft.rfft(data.real)
#     y_imag = np.fft.rfft(data.imag)
#     #
#
#     power_real = np.power(np.abs(y_real), 2) / n
#     power_imag = np.power(np.abs(y_imag), 2) / n
#     plt.plot(abs(power_real), label="real")
#     plt.plot(abs(power_imag), label="imag")
#     plt.xlabel("FFT bin")
#     plt.ylabel("Power")
#     plt.show()


# def main():
#     description = "gr-lora_sdr complex data stream plotter"
#     parser = argparse.ArgumentParser(conflict_handler="resolve", description=description)
#     # parser.add_argument("-B", "--block", type=int, default=1000,
#     #                     help="Specify the block size [default=%(default)r]")
#     # parser.add_argument("-s", "--start", type=int, default=0,
#     #                     help="Specify where to start in the file [default=%(default)r]")
#     parser.add_argument("-s", "--samp_rate", type=float, default=250e3,
#                         help="Set the sampler rate of the data default=%(default)r")
#     parser.add_argument("filename", metavar="FILE",
#                         help="Input file with complex samples")
#     args = parser.parse_args()
#
#     print("Welcome to gr-lora_sdr test plotter")
#     # filename = sys.argv[1]
#     data = open_file(args.filename)
#     # plot_fft(data,args.samp_rate)
#     # plot_power_fft_bin(data, args.samp_rate)
#     plot_spectogram(data, args.samp_rate)

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
