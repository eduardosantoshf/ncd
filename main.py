import sys
import sox
import argparse
import os
import gzip

class Main:
    
    def __init__(self, sample_file):
        self.sample_file = sample_file
        self.tfm = sox.Transformer()
        self.ndc = dict()
        self.cbn = sox.Combiner()

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
        

        self.tfm.trim(start, end)
        self.tfm.build_file("examples/sample01.wav", 'test_trim.wav')

        print("Done")

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

                    f_out_test = gzip.open('compressed/' + file + '.gz', 'wb')
                    f_out_test.writelines(f)
                    test_size = os.path.getsize('compressed/' + file + '.gz')

                    f_out_test.close()

                    f_out_sample = gzip.open(self.sample_file + '.gz', 'wb')
                    f_in_sample = open(self.sample_file, "rb")
                    f_out_sample.writelines(f_in_sample)
                    sample_size = os.path.getsize(self.sample_file + '.gz')

                    f_out_sample.close()

                    f_out = gzip.open('join.wav.gz', 'wb')
                    f_in = open('join.wav', "rb")
                    f_out.writelines(f_in)                   
                    file_size = os.path.getsize('join.wav.gz')

                    f_out.close()

                    print(file)
                    print(file_size)
                    print(test_size)
                    print(sample_size)
                    print("----------")
                    

                    # calculate NDC
                    self.ndc[file] = (file_size - min(test_size, sample_size)) / max(test_size, sample_size)

                    os.remove('join.wav')
                    os.remove('join.wav.gz')

        print(self.ndc)
        music = min(self.ndc, key = self.ndc.get)

        return music


if __name__== "__main__":
    
    parser = argparse.ArgumentParser(description='Recognize music.')
    parser.add_argument("--sample", metavar="file", type=str, default="test_trim.wav", help='Sample file')
    parser.add_argument('--start_trim', type=float, default=5, help='Seconds to start trim')
    parser.add_argument('--end_trim', type=float, default=10, help='Seconds to stop trim')

    args = vars(parser.parse_args())
    
    filename = args["sample"]

    #if not os.path.exists(filename):
    #    raise Exception("Sample file dies not exist!")

    start_trim = args["start_trim"]
    end_trim = args["end_trim"]

    main = Main(filename)
    main.trim_samples(0.0, 10.0)

    print(main.calculate_ndc())
    
