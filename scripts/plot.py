# Simple test file to plot complex data stream

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np


def open_file(filename):
    data = np.fromfile(open(filename), dtype=np.complex64)
    return data


def plot_fft(data, samp_rate):
    # Number of samplepoints
    sp = np.fft.fft(data)
    freq = np.fft.fftfreq(data.shape[-1])
    plt.plot(freq, sp.real, freq, sp.imag)
    plt.show()


def plot_power_fft(data, samp_rate):
    n = data.size
    y = np.fft.fft(data)/n
    # f = (n - 1) * samp_rate / n
    # time = np.arange(0, endTime, samplingInterval);
    T = samp_rate*n
    f = np.linspace(0, 1 / T, n)

    period = n/samp_rate
    values = np.arange(int(n/2))
    freqs = values/period
    power = np.power(np.abs(y), 2) / n
    plt.plot(freqs, power)
    plt.xlabel("Frequency")
    plt.ylabel("Power")
    plt.show()


def main():
    description = "Takes a GNU Radio complex binary file and displays the I&Q data versus time and the constellation plot (I vs. Q). You can set the block size to specify how many points to read in at a time and the start position in the file. By default, the system assumes a sample rate of 1, so in time, each sample is plotted versus the sample number. To set a true time axis, set the sample rate (-R or --sample-rate) to the sample rate used when capturing the samples."

    parser = argparse.ArgumentParser(conflict_handler="resolve", description=description)
    # parser.add_argument("-B", "--block", type=int, default=1000,
    #                     help="Specify the block size [default=%(default)r]")
    # parser.add_argument("-s", "--start", type=int, default=0,
    #                     help="Specify where to start in the file [default=%(default)r]")
    parser.add_argument("-s", "--samp_rate", type=float, default=250000,
                        help="Set the sampler rate of the data default=%(default)r")
    parser.add_argument("filename", metavar="FILE",
                        help="Input file with complex samples")
    args = parser.parse_args()

    print("Welcome to gr-lora_sdr test plotter")
    # filename = sys.argv[1]
    data = open_file(args.filename)
    # plot_fft(data,args.samp_rate)
    plot_power_fft(data, args.samp_rate)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
