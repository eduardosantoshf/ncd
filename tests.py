from main import Main
import matplotlib.pyplot as plt
import os
from compressor import Compressor

if __name__ == "__main__":
    
    cs = {}
    samples = [x for x in os.listdir("examples/") if x.endswith(".wav")]
    for c in ["gzip", "bzip2", "lzma"]:
        comp_instance = Compressor(c)
        compressor = comp_instance.select_compressor()
        for t in range(1, 20, 2):
            hits = 0
            for sample in samples:
                m = Main("examples/"+sample, t*0.01, 0, compressor, 0)
                m.trim_sample()
                selected = m.calculate_ndc()
                hits += 1 if selected == sample else 0
                
            cs.setdefault(c, [])
            cs[c].append(hits / len(samples))
        
    for k,v in cs.items():
        
        plt.plot(range(1, 20, 2), v, label=k)

    plt.xlabel("Threshold")
    plt.ylabel("Precision")        
    plt.legend()
    plt.show()
    