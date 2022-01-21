from ast import arg
import sys

import sox
import argparse
import os
import gzip
import time

class Main:
    
    def __init__(self, sample_file, threshold):
        self.sample_file = sample_file
        self.threshold = threshold
        self.tfm = sox.Transformer()
        self.ndc = dict()
        self.cbn = sox.Combiner()


    def trim_sample(self):
        # trim audio
        self.tfm.trim(0.0, 10.0)

        # apply compression
        self.tfm.compand()

        # output
        self.tfm.build_file(self.sample_file, 'test_trim.wav')

        self.tfm = sox.Transformer()

        self.sample_file = 'test_trim.wav'


   # function to trim audio and save the trimmed version
    def trim_samples(self, start, end):#
        filenames = [file for file in os.listdir("examples/")]#
        for file in filenames:
            with open("examples/" + file, "r") as f:#
                # trim audio
                self.tfm.trim(start, end)#
                # apply compression
                self.tfm.compand()#
                # output file
                self.tfm.build_file("examples/{}".format(file), 'trimmed/{}_trimmed.wav'.format(file.split('.')[0]))#
                self.tfm = sox.Transformer()


    def calculate_ndc(self):

        filenames = [file for file in os.listdir("examples/")]

        for file in filenames:
            if file != '.DS_Store':
                with open("examples/" + file, "rb") as f:

                    # concatenate the 2 samples
                    #self.cbn.build(
                    #    [self.sample_file, 'examples/' + file], 
                    #    'join.wav',
                    #    'concatenate'
                    #)

                    #self.cbn = sox.Combiner()

                    ###################################
                    #            DB File              #
                    ###################################

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w test.freqs examples/{}".format(file))

                    test_file = open("test.freqs", "rb")
                    test_size_read = test_file.read()
                    test_size = len(gzip.compress(test_size_read))

                    os.system("rm test.freqs")

                    ###################################
                    #           Sample File           #
                    ###################################

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w test.freqs " + self.sample_file)

                    sample_file = open("test.freqs", "rb")
                    sample_file_read = sample_file.read()
                    sample_size = len(gzip.compress(sample_file_read))

                    os.system("rm test.freqs")
                    
                    ###################################
                    #       Concatenated file         #
                    ###################################

                    # turn audio into frequencies
                    #os.system("./GetMaxFreqs/src/GetMaxFreqs -w test.freqs join.wav")

                    #join_file = open("test.freqs", "rb")
                    #join_file_read = join_file.read()
                    file_size = len(gzip.compress(test_size_read + sample_file_read))

                    #os.system("rm test.freqs")

                    # calculate NDC
                    self.ndc[file] = (file_size - min(test_size, sample_size)) / max(test_size, sample_size)
                    #print(file + " --- " + str(file_size) + " --- " + str(test_size) + " --- " + str(sample_size))

                    # remove temporary concatenated file
                    #os.remove('join.wav')

        print(self.ndc)
        music = min(self.ndc, key = self.ndc.get)

        return music


if __name__== "__main__":
    
    parser = argparse.ArgumentParser(description='Recognize music.')
    parser.add_argument("--sample", metavar="file", type=str, default="sample01.wav", help='Sample file')
    parser.add_argument('--start_trim', type=float, default=5, help='Seconds to start trim')
    parser.add_argument('--end_trim', type=float, default=10, help='Seconds to stop trim')
    parser.add_argument('--threshold', type=int, default=10, help='Percentage of the song to test')

    args = vars(parser.parse_args())
    
    filename = args["sample"]

    threshold_sample = args["threshold"]

    #if not os.path.exists(filename):
    #    raise Exception("Sample file dies not exist!")

    start_trim = args["start_trim"]
    end_trim = args["end_trim"]

    main = Main(filename, threshold_sample)
    #main.trim_sample()
    #main.trim_samples(0.0, 10.0)

    print(main.calculate_ndc())
    
