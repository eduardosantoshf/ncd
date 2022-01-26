import matplotlib.pyplot as plt
import argparse

class Plot:

    def __init__(self, x, y, x_label, y_label, title):
        self.x = x
        self.y = y
        self.x_label = x_label
        self.y_label = y_label
        self.title = title

    def show_plot(self, grid):

        plt.plot(self.x, self.y)
        plt.xticks(self.x)
        #plt.yticks(self.y)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)

        if grid:
            plt.grid()

        plt.show()




