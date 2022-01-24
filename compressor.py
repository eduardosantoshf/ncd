class Compressor:

    def __init__(self, type):
        self.type = type

    def select_compressor(self):
        if self.type == "gzip":
            import gzip as compressor
        elif self.type == "bzip2":
            import bz2 as compressor
        elif self.type == "lzma":
            import lzma as compressor
        else:
            print("Compression type not supported! \n\nAvailable compressors: \n\tgzip, bzip2, lzma")
            exit()

        return compressor