import sys
import sox
import argparse
import os

class Main:
    
    def __init__(self, sample_file):
        self.sample_file = sample_file
        self.tfm = sox.Transformer()

    # function to trim audio and save the trimmed version
    def trim_sample(self, start, end):
        
        # trim audio
        self.tfm.trim(start, end)

        # apply compression
        self.tfm.compand()

        # output file
        self.tfm.build_file(self.sample_file, 'trimmed/test_trim.wav')

        print("Done")
        


if __name__== "__main__":
    
    parser = argparse.ArgumentParser(description='Recognize music.')
    parser.add_argument("--sample", metavar="file", type=str, default="examples/sample01.wav", help='Sample file')
    parser.add_argument('--start_trim', type=float, default=5, help='Seconds to start trim')
    parser.add_argument('--end_trim', type=float, default=10, help='Seconds to stop trim')

    args = vars(parser.parse_args())
    
    filename = args["sample"]

    if not os.path.exists(filename):
        raise Exception("Sample file dies not exist!")

    start_trim = args["start_trim"]
    end_trim = args["end_trim"]

    main = Main(filename)
    main.trim_sample(start_trim, end_trim)
    
