from ast import arg
import sys

import sox
import argparse
import os

from compressor import Compressor
from plots import Plot

class Main:
    
    def __init__(self, sample_file, threshold, start_trim, compressor, noise):
        self.sample_file = sample_file
        self.threshold = threshold
        self.start_trim = start_trim
        self.compressor = compressor
        self.noise = noise
        self.tfm = sox.Transformer()
        self.ndc = dict()

    def trim_sample(self):

        # sample duration
        audio_trim = sox.file_info.duration(self.sample_file) * self.threshold

        try:
            # check if start time is smaller than audio duration
            if self.start_trim > sox.file_info.duration(self.sample_file):
                raise ValueError("Start time must be smaller than song duration!")

            # trim audio
            self.tfm.trim(self.start_trim, audio_trim + self.start_trim)

        # if trim fails
        except(ValueError) as E:
            print("Start time of the trim must be smaller than the end time!")
            exit()

        # remove previous sample file if there
        if os.path.exists("sample/sample.wav"):
            os.remove("sample/sample.wav")
        
        # save trimmed file
        self.tfm.build_file(self.sample_file, 'sample/sample.wav')

        self.sample_file = 'sample/sample.wav'


    def calculate_ndc(self):

        ###################################
        #           Sample File           #
        ###################################
        if self.noise > 1 or self.noise < 0:
            raise ValueError("Noise must be between 0 and 1!")
        
        if self.noise > 0:
            cmd = f"sox sample/sample.wav -p synth whitenoise vol {self.noise} | sox -m sample/sample.wav - sample/sample_noise.wav"
            os.system(cmd)
            self.sample_file = 'sample/sample_noise.wav'


        # turn audio into frequencies
        os.system("./GetMaxFreqs/src/GetMaxFreqs -w sample/sample.freqs {}".format(self.sample_file))

        sample_file = open("sample/sample.freqs", "rb")
        sample_file_read = sample_file.read()
        sample_size = len(self.compressor.compress(sample_file_read))


        # db files
        filenames = [file for file in os.listdir("examples/")]

        for file in filenames:
            if file != '.DS_Store':
                with open("examples/" + file, "rb") as f:

                    output_file = file.split(".")[0]

                    ###################################
                    #            DB File              #
                    ###################################

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w freqs/{}.freqs examples/{}".format(output_file, file))

                    test_file = open("freqs/{}.freqs".format(output_file), "rb")
                    test_size_read = test_file.read()
                    test_size = len(self.compressor.compress(test_size_read))
                    
                    ###################################
                    #       Concatenated file         #
                    ###################################

                    # join file size
                    file_size = len(self.compressor.compress(test_size_read + sample_file_read))

                    # calculate NDC
                    self.ndc[file] = (file_size - min(test_size, sample_size)) / max(test_size, sample_size)

        music = min(self.ndc, key = self.ndc.get)

        return music

    def get_values_plot(self, song, type, values):

        y_values = []

        if type == 'n':
            for noise in values:
                cmd = f"sox sample/sample.wav -p synth whitenoise vol {noise} | sox -m sample/sample.wav - plots/sample_noise.wav"
                os.system(cmd)
                self.sample_file = 'plots/sample_noise.wav'

                # turn audio into frequencies
                os.system("./GetMaxFreqs/src/GetMaxFreqs -w plots/sample.freqs {}".format(self.sample_file))

                sample_file = open("plots/sample.freqs", "rb")
                sample_file_read = sample_file.read()
                sample_size = len(self.compressor.compress(sample_file_read))

                output_file = song.split(".")[0]

                ###################################
                #            DB File              #
                ###################################

                # turn audio into frequencies
                os.system("./GetMaxFreqs/src/GetMaxFreqs -w plots/{}.freqs examples/{}".format(output_file, song))

                test_file = open("plots/{}.freqs".format(output_file), "rb")
                test_size_read = test_file.read()
                test_size = len(self.compressor.compress(test_size_read))
                
                ###################################
                #       Concatenated file         #
                ###################################

                # join file size
                file_size = len(self.compressor.compress(test_size_read + sample_file_read))

                # calculate NDC
                y_values.append((file_size - min(test_size, sample_size)) / max(test_size, sample_size))
        
        elif type == 'st':
            for s_time in values:

                # sample duration
                audio_trim = sox.file_info.duration("examples/" + song) * s_time

                # trim audio
                self.tfm.trim(0, audio_trim)
                
                # save trimmed file
                self.tfm.build_file("examples/" + song, 'plots/sample.wav')

                # turn audio into frequencies
                os.system("./GetMaxFreqs/src/GetMaxFreqs -w plots/sample.freqs plots/sample.wav")

                sample_file = open("plots/sample.freqs", "rb")
                sample_file_read = sample_file.read()
                sample_size = len(self.compressor.compress(sample_file_read))

                output_file = song.split(".")[0]

                ###################################
                #            DB File              #
                ###################################

                # turn audio into frequencies
                os.system("./GetMaxFreqs/src/GetMaxFreqs -w plots/{}.freqs examples/{}".format(output_file, song))

                test_file = open("plots/{}.freqs".format(output_file), "rb")
                test_size_read = test_file.read()
                test_size = len(self.compressor.compress(test_size_read))
                
                ###################################
                #       Concatenated file         #
                ###################################

                # join file size
                file_size = len(self.compressor.compress(test_size_read + sample_file_read))

                y_values.append((file_size - min(test_size, sample_size)) / max(test_size, sample_size))

                self.tfm = sox.Transformer()
                os.remove("plots/sample.wav")


        return y_values



if __name__== "__main__":
    
    parser = argparse.ArgumentParser(description='Recognize music.')
    parser.add_argument("--sample", metavar="file", type=str, default="examples/sample01.wav", help='Sample file')
    parser.add_argument('--start_trim', type=float, default=0, help='Seconds to start trim')
    parser.add_argument('--threshold', type=int, default=50, help='Percentage of the song to test')
    parser.add_argument('--compressor', type=str, default="gzip", help='Compression type (gzip, bzip2, lzma).')
    parser.add_argument('--noise', type=float, default=0, help="Noise value. Default is no noise")
    parser.add_argument("--st", action='store_true', help="Plot graphic with variation of sample size.")
    parser.add_argument("--n", action='store_true', help="Plot graphic with variation of noise.")

    args = vars(parser.parse_args())
    
    # Sample file handling
    filename = args["sample"]

    try:
        f = open(filename, 'r')
    except(IOError) as E:
        print("Sample file dies not exist!")
        exit()

    # threshold precentage
    threshold_sample = args["threshold"] * 0.01

    # start trim time
    start_trim = args["start_trim"]

    # compressor
    comp_instance = Compressor(args["compressor"])
    compressor = comp_instance.select_compressor()

    # noise
    noise = args["noise"]

    # create main object
    main = Main(filename, threshold_sample, start_trim, compressor, noise)

    # trim sample file
    main.trim_sample()

    # predict song
    selected_song = main.calculate_ndc()
    print("A sample pertence ao ficheiro: " + str(selected_song))

    # plots
    if args['n']:

        x = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        y = main.get_values_plot(selected_song, 'n', x)

        plt = Plot(x, y, "Noise", "NDC", "Noise variation")
        plt.show_plot(True)

    elif args['st']:

        x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        y = main.get_values_plot(selected_song, 'st', x)

        plt = Plot(x, y, "Sample Time", "NDC", "Sample time variation (compared to full song)")
        plt.show_plot(True)



    
