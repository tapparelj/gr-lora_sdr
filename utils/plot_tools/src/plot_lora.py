import numpy
from gnuradio import gr

try:
    from pylab import Button, connect, draw, figure, figtext, get_current_fig_manager, mlab, show, rcParams, ceil
except ImportError:
    print("Please install Matplotlib to run this script (http://matplotlib.sourceforge.net/)")
    raise SystemExit(1)
import numpy as np

from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.plot_data import datatype_lookup


class plot_lora(object):
    def __init__(self, datatype, filename, options):
        self.hfile = open(filename, "r")
        self.block_length = options.block
        self.start = options.start
        self.sample_rate = options.sample_rate
        self.psdfftsize = options.psd_size
        self.specfftsize = options.spec_size

        self.datatype = datatype
        if self.datatype is None:
            self.datatype = datatype_lookup[options.data_type]
        self.sizeof_data = self.datatype().nbytes  # number of bytes per sample in file

        self.axis_font_size = 16
        self.label_font_size = 18
        self.title_font_size = 20
        self.text_size = 22
        # TODO fix this the right manner
        self.xlim = np.array([10, 20])

        # Setup PLOT
        self.fig = figure(1, figsize=(16, 12), facecolor='w')
        rcParams['xtick.labelsize'] = self.axis_font_size
        rcParams['ytick.labelsize'] = self.axis_font_size

        self.text_file = figtext(0.10, 0.95, ("File: %s" % filename),
                                 weight="heavy", size=self.text_size)
        self.text_file_pos = figtext(0.10, 0.92, "Position: ",
                                     weight="heavy", size=self.text_size)
        self.text_block = figtext(0.35, 0.92, ("Block Size: %d" % self.block_length),
                                  weight="heavy", size=self.text_size)
        self.text_sr = figtext(0.60, 0.915, ("Sample Rate: %.2f" % self.sample_rate),
                               weight="heavy", size=self.text_size)
        self.make_plots()
        # info for buttons etc
        self.button_left_axes = self.fig.add_axes([0.45, 0.01, 0.05, 0.05], frameon=True)
        self.button_left = Button(self.button_left_axes, "<")
        self.button_left_callback = self.button_left.on_clicked(self.button_left_click)

        self.button_right_axes = self.fig.add_axes([0.50, 0.01, 0.05, 0.05], frameon=True)
        self.button_right = Button(self.button_right_axes, ">")
        self.button_right_callback = self.button_right.on_clicked(self.button_right_click)

        self.manager = get_current_fig_manager()
        connect('draw_event', self.zoom)
        connect('key_press_event', self.click)
        show()

    def get_data(self):
        self.position = self.hfile.tell() / self.sizeof_data
        self.text_file_pos.set_text("Position: %d" % self.position)
        try:
            self.iq = numpy.fromfile(self.hfile, dtype=self.datatype, count=self.block_length)
        except MemoryError:
            print("End of File")
            return False
        else:
            # retesting length here as newer version of numpy does not throw a MemoryError, just
            # returns a zero-length array
            if (len(self.iq) > 0):
                tstep = 1.0 / self.sample_rate
                # self.time = numpy.array([tstep*(self.position + i) for i in range(len(self.iq))])
                self.time = numpy.array([tstep * (i) for i in range(len(self.iq))])

                self.iq_psd, self.freq = self.dopsd(self.iq)
                return True
            else:
                print("End of File")
                return False

    def dopsd(self, iq):
        ''' Need to do this here and plot later so we can do the fftshift '''
        overlap = self.psdfftsize / 4
        winfunc = numpy.blackman
        psd, freq = mlab.psd(iq, self.psdfftsize, self.sample_rate,
                             window=lambda d: d * winfunc(self.psdfftsize),
                             noverlap=overlap)
        psd = 10.0 * numpy.log10(abs(psd))
        return (psd, freq)

    def make_plots(self):
        # if specified on the command-line, set file pointer
        self.hfile.seek(self.sizeof_data * self.start, 1)

        # define positions default is fine for now
        iqdims = [0.075, 0.2, 0.4, 0.6]
        psddims = [0.575, 0.2, 0.4, 0.6]
        specdims = [0.575, 0.2, 0.4, 0.6]

        # Subplot for spectrogram plot
        self.sp_spec = self.fig.add_subplot(2, 2, 1)
        self.sp_spec.set_title(("Spectrogram"), fontsize=self.title_font_size, fontweight="bold")
        self.sp_spec.set_xlabel("Time (s)", fontsize=self.label_font_size, fontweight="bold")
        self.sp_spec.set_ylabel("Frequency (Hz)", fontsize=self.label_font_size, fontweight="bold")
        self.draw_spec(self.time, self.iq)

        # Subplot for PSD plot
        self.sp_psd = self.fig.add_subplot(2, 2, 2)
        self.sp_psd.set_title(("PSD"), fontsize=self.title_font_size, fontweight="bold")
        self.sp_psd.set_xlabel("Frequency (Hz)", fontsize=self.label_font_size, fontweight="bold")
        self.sp_psd.set_ylabel("Power Spectrum (dBm)", fontsize=self.label_font_size, fontweight="bold")

        r = self.get_data()

        # self.plot_iq = self.sp_iq.plot([], 'bo-')  # make plot for reals
        # self.plot_iq += self.sp_iq.plot([], 'ro-')  # make plot for imags
        # self.draw_time(self.time, self.iq)         # draw the plot

        self.plot_psd = self.sp_psd.plot([], 'b')  # make plot for PSD
        self.draw_psd(self.freq, self.iq_psd)  # draw the plot



        draw()

    def downchrip(self, t):

    def draw_time(self, t, iq):
        self.sp_spec.set_xlim(t.min(), t.max())

    def draw_psd(self, f, p):
        self.plot_psd[0].set_data([f, p])
        self.sp_psd.set_ylim([p.min() - 10, p.max() + 10])
        self.sp_psd.set_xlim([f.min(), f.max()])

    def draw_spec(self, t, s):
        overlap = self.specfftsize / 4
        winfunc = numpy.blackman
        self.sp_spec.clear()
        self.sp_spec.specgram(s, self.specfftsize, self.sample_rate,
                              window=lambda d: d * winfunc(self.specfftsize),
                              noverlap=overlap, xextent=[t.min(), t.max()])

    def draw_demod(self, t, s):
        # demod = gr.ex
        overlap = self.specfftsize / 4
        winfunc = numpy.blackman
        self.sp_spec.clear()
        self.sp_spec.specgram(np.abs(s), self.specfftsize, self.sample_rate,
                              window=lambda d: d * winfunc(self.specfftsize),
                              noverlap=overlap, xextent=[t.min(), t.max()])

    def update_plots(self):
        self.draw_time(self.time, self.iq)
        self.draw_psd(self.freq, self.iq_psd)
        self.draw_spec(self.time, self.iq)
        self.xlim = numpy.array(self.sp_spec.get_xlim())  # so zoom doesn't get called

        draw()

    def zoom(self, event):
        newxlim = numpy.array(self.sp_spec.get_xlim())
        curxlim = numpy.array(self.xlim)
        if (newxlim[0] != curxlim[0] or newxlim[1] != curxlim[1]):
            # xmin = max(0, int(ceil(self.sample_rate*(newxlim[0] - self.position))))
            # xmax = min(int(ceil(self.sample_rate*(newxlim[1] - self.position))), len(self.iq))
            xmin = max(0, int(ceil(self.sample_rate * (newxlim[0]))))
            xmax = min(int(ceil(self.sample_rate * (newxlim[1]))), len(self.iq))

            iq = numpy.array(self.iq[xmin: xmax])
            time = numpy.array(self.time[xmin: xmax])

            iq_psd, freq = self.dopsd(iq)

            self.draw_psd(freq, iq_psd)
            self.xlim = numpy.array(self.sp_spec.get_xlim())

            draw()

    def click(self, event):
        forward_valid_keys = [" ", "down", "right"]
        backward_valid_keys = ["up", "left"]

        if (find(event.key, forward_valid_keys)):
            self.step_forward()

        elif (find(event.key, backward_valid_keys)):
            self.step_backward()

    def button_left_click(self, event):
        self.step_backward()

    def button_right_click(self, event):
        self.step_forward()

    def step_forward(self):
        r = self.get_data()
        if (r):
            self.update_plots()

    def step_backward(self):
        # Step back in file position
        if (self.hfile.tell() >= 2 * self.sizeof_data * self.block_length):
            self.hfile.seek(-2 * self.sizeof_data * self.block_length, 1)
        else:
            self.hfile.seek(-self.hfile.tell(), 1)
        r = self.get_data()
        if (r):
            self.update_plots()

    @staticmethod
    def setup_options():
        description = "."

        parser = ArgumentParser(conflict_handler="resolve", description=description)
        parser.add_argument("-d", "--data-type", default="complex64",
                            choices=("complex64", "float32", "int32", "uint32", "int16",
                                     "uint16", "int8", "uint8"),
                            help="Specify the data type [default=%(default)r]")
        parser.add_argument("-B", "--block", type=int, default=8192,
                            help="Specify the block size [default=%(default)r]")
        parser.add_argument("-s", "--start", type=int, default=0,
                            help="Specify where to start in the file [default=%(default)r]")
        parser.add_argument("-R", "--sample-rate", type=eng_float, default=1.0,
                            help="Set the sampler rate of the data [default=%(default)r]")
        parser.add_argument("--psd-size", type=int, default=1024,
                            help="Set the size of the PSD FFT [default=%(default)r]")
        parser.add_argument("--spec-size", type=int, default=256,
                            help="Set the size of the spectrogram FFT [default=%(default)r]")
        parser.add_argument("-S", "--enable-spec", action="store_true",
                            help="Turn on plotting the spectrogram [default=%(default)r]")
        parser.add_argument("file", metavar="FILE",
                            help="Input file with samples")

        return parser


def find(item_in, list_search):
    try:
        return list_search.index(item_in) != None
    except ValueError:
        return False


def main():
    parser = plot_lora.setup_options()
    args = parser.parse_args()
    plot_lora(None, args.file, args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
