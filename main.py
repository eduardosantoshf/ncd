import sys
import sox
import argparse
import os
import gzip
import time

class Main:
    
    def __init__(self, sample_file):
        self.sample_file = sample_file
        self.tfm = sox.Transformer()
        self.ndc = dict()
        self.cbn = sox.Combiner()


    def trim_sample(self):
        # trim audio
        self.tfm.trim(0.0, 10.0)

        # apply compression
        self.tfm.compand()

        # output
        self.tfm.build_file("examples/" + self.sample_file, 'test_trim.wav')

        self.tfm = sox.Transformer()

        self.sample_file = 'test_trim.wav'


    # function to trim audio and save the trimmed version
    def trim_samples(self, start, end):

        filenames = [file for file in os.listdir("examples/")]

        for file in filenames:
            with open("examples/" + file, "r") as f:

                # trim audio
                self.tfm.trim(start, end)

                # apply compression
                self.tfm.compand()

                # output file
                self.tfm.build_file("examples/{}".format(file), 'trimmed/{}_trimmed.wav'.format(file.split('.')[0]))

                self.tfm = sox.Transformer()


    def calculate_ndc(self):

        filenames = [file for file in os.listdir("trimmed/")]

        for file in filenames:
            if file != '.DS_Store':
                with open("trimmed/" + file, "rb") as f:

                    # concatenate the 2 samples
                    self.cbn.build(
                        [self.sample_file, 'trimmed/' + file], 
                        'join.wav',
                        'concatenate'
                    )

                    ###################################
                    #            DB File              #
                    ###################################

                    #open compressed file
                    f_out_test = gzip.open('compressed/' + file.split(".")[0] + '.freqs.gz', 'wb')

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w test.freqs trimmed/{}".format(file))

                    # write in compressed file
                    f_in = open("test.freqs", "rb")
                    f_out_test.writelines(f_in)
                    f_in.close()
                    f_out_test.close()
                    os.system("rm test.freqs")

                    # get file size
                    test_size = os.path.getsize('compressed/' + file.split(".")[0] + '.freqs.gz') * 8


                    ###################################
                    #           Sample File           #
                    ###################################

                    #open compressed file
                    f_out_sample = gzip.open(self.sample_file.split(".")[0] + '.freqs.gz', 'wb')

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w test.freqs " + self.sample_file)

                    # write in compressed file
                    with open("test.freqs", "rb") as freqs:
                        f_out_sample.writelines(freqs)
                    f_out_sample.close()
                    os.system("rm test.freqs")

                    # get file size
                    sample_size = os.path.getsize(self.sample_file.split(".")[0] + '.freqs.gz')

                    
                    ###################################
                    #       Concatenated file         #
                    ###################################

                    #open compressed file
                    f_out = gzip.open('join.freqs.gz', 'wb')

                    # turn audio into frequencies
                    os.system("./GetMaxFreqs/src/GetMaxFreqs -w test.freqs join.wav")

                    # write in compressed file
                    with open("test.freqs", "rb") as freqs:
                        f_out.writelines(freqs)
                    f_out.close()
                    os.system("rm test.freqs")

                    # get file size      
                    file_size = os.path.getsize('join.freqs.gz')

                    # calculate NDC
                    self.ndc[file] = (file_size - min(test_size, sample_size)) / max(test_size, sample_size)

                    # remove temporary concatenated file
                    os.remove('join.wav')
                    os.remove('join.freqs.gz')

        print(self.ndc)
        music = min(self.ndc, key = self.ndc.get)

        return music


if __name__== "__main__":
    
    parser = argparse.ArgumentParser(description='Recognize music.')
    parser.add_argument("--sample", metavar="file", type=str, default="sample01.wav", help='Sample file')
    parser.add_argument('--start_trim', type=float, default=5, help='Seconds to start trim')
    parser.add_argument('--end_trim', type=float, default=10, help='Seconds to stop trim')

    args = vars(parser.parse_args())
    
    filename = args["sample"]

    #if not os.path.exists(filename):
    #    raise Exception("Sample file dies not exist!")

    start_trim = args["start_trim"]
    end_trim = args["end_trim"]

    main = Main(filename)
    main.trim_sample()
    main.trim_samples(0.0, 10.0)

    print(main.calculate_ndc())
    
