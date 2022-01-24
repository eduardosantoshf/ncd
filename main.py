from ast import arg
import sys

import sox
import argparse
import os

from compressor import Compressor

class Main:
    
    def __init__(self, sample_file, threshold, start_trim, compressor):
        self.sample_file = sample_file
        self.threshold = threshold
        self.start_trim = start_trim
        self.compressor = compressor
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
                    #           Sample File           #
                    ###################################

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w sample/sample.freqs {}".format(self.sample_file))

                    sample_file = open("sample/sample.freqs", "rb")
                    sample_file_read = sample_file.read()
                    sample_size = len(self.compressor.compress(sample_file_read))
                    
                    ###################################
                    #       Concatenated file         #
                    ###################################

                    # join file size
                    file_size = len(self.compressor.compress(test_size_read + sample_file_read))

                    # calculate NDC
                    self.ndc[file] = (file_size - min(test_size, sample_size)) / max(test_size, sample_size)

        print(self.ndc)
        music = min(self.ndc, key = self.ndc.get)

        return music


if __name__== "__main__":
    
    parser = argparse.ArgumentParser(description='Recognize music.')
    parser.add_argument("--sample", metavar="file", type=str, default="examples/sample01.wav", help='Sample file')
    parser.add_argument('--start_trim', type=float, default=0, help='Seconds to start trim')
    parser.add_argument('--threshold', type=int, default=50, help='Percentage of the song to test')
    parser.add_argument('--compressor', type=str, default="gzip", help='Compression type (gzip, bzip2, lzma).')

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

    # create main object
    main = Main(filename, threshold_sample, start_trim, compressor)

    # trim sample file
    main.trim_sample()

    # predict song
    print(main.calculate_ndc())
    
