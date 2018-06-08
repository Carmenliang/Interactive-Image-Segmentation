import time
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import nibabel as nib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from scipy import ndimage

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

import classical

LARGE_FONT = ('Verdana', 12)
SMALL_FONT = ('Verdana', 10)

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(container, self)

        frame.grid(row=0, column=0, sticky='nsew')

        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.filename = ''
        self.filename_label = None
        self.canvas = None

        # TODO: UCLA logo
        uclapath = 'ucla.png'
        uclaimg = ImageTk.PhotoImage(Image.open(uclapath).resize((100,100)))
        ucla_label = tk.Label(self, image=uclaimg)
        ucla_label.image = uclaimg
        ucla_label.grid(row=0)

        title_label = tk.Label(self, text='Lung Segmentation', font=LARGE_FONT)
        title_label.grid(row=1, column=0)

        # step 1: choose image
        step1_label = tk.Label(self, text='1. Choose image')
        step1_label.grid(row=2, sticky='w')
        file_button = tk.Button(self, text='Add Image', command=self.getfilename)
        file_button.grid(row=3, column=0, sticky='w')

        # Step 2: output directory and filename?
        # TODO: output path, row 3
        step2_label = tk.Label(self, text='2. Choose output directory and filename')
        directory_button = tk.Button(self, text='Choose directory', command=self.getoutputdirectory)
        self.output_filename_label = tk.Label(self, text='filename:')
        self.output_filename_entry = tk.Entry(self)

        step2_label.grid(row=4, sticky='w')
        directory_button.grid(row=5, column=0, sticky='w')
        self.output_filename_label.grid(row=6, column=0, sticky='e')
        self.output_filename_entry.grid(row=6, column=1, sticky='w')

        # Step 3: Parameters (Initial pos, iterations)
        step3_label = tk.Label(self, text='2. Specify Parameters. (Click in image to set initial x, y)', font=LARGE_FONT)
        x_label = tk.Label(self, text='x:', font=SMALL_FONT)
        self.x_entry = tk.Entry(self)
        y_label = tk.Label(self, text='y:', font=SMALL_FONT)
        self.y_entry = tk.Entry(self)
        iter_label = tk.Label(self, text='iterations:', font=SMALL_FONT)
        self.iter_entry = tk.Entry(self)
        self.iter_entry.insert(0, '500')

        step3_label.grid(row=7, sticky='w')
        x_label.grid(row=8, column=0, sticky='e')
        self.x_entry.grid(row=8, column=1, sticky='w')
        y_label.grid(row=9, column=0, sticky='e')
        self.y_entry.grid(row=9, column=1, sticky='w')
        iter_label.grid(row=10, column=0, sticky='e')
        self.iter_entry.grid(row=10, column=1, sticky='w')

        # Step 4: run
        step4_label = tk.Label(self, text='4.')
        run_button = tk.Button(self, text='Run', command=self.run)

        step4_label.grid(row=11, column=0, sticky='w')
        run_button.grid(row=11, column=1, sticky='w')

    def getfilename(self):
        self.filename = filedialog.askopenfilename(initialdir='.', title='select')
        base = os.path.basename(self.filename)
        if not self.output_filename_entry.get():
            self.output_filename_entry.delete(0, tk.END)
            self.output_filename_entry.insert(0, 'output.png')
        print(self.filename)
        if self.filename_label: # already displaying a filename
            # TODO: update displayed filename
            self.filename_label.text=self.filename
            self.filename_label.grid(row=3, column=1)
        else: # no filename label displayed
            # create and grid label
            self.filename_label = tk.Label(self, text=self.filename, font=SMALL_FONT)
            self.filename_label.grid(row=3, column=1)

            # plot figure
            self.image = nib.load(self.filename).get_data().T
            self.figure = Figure(figsize=(5,5), dpi=100)
            self.subplot = self.figure.add_subplot(111)
            self.im = self.subplot.imshow(self.image, cmap=plt.cm.gray)

            self.canvas = FigureCanvasTkAgg(self.figure, self)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=12, column=0)

            self.canvas.mpl_connect('button_press_event', lambda e: self.onclick(e))

    def getoutputdirectory(self):
        self.output_directory = filedialog.askdirectory(initialdir='.', title='select')
        print(self.output_directory)

        output_directory_label = tk.Label(self, text=self.output_directory)
        output_directory_label.grid(row=5, column=1, sticky='w')

    def onclick(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(int(event.xdata)))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(int(event.ydata)))

    def redraw_contour(self, res):
        self.subplot.cla()
        self.subplot.imshow(self.image, cmap=plt.cm.gray)
        self.subplot.contour(res, [0.5], colors='r')
        self.canvas.draw()
        self.parent.update_idletasks()
        self.parent.update()
        self.controller.update_idletasks()
        self.controller.update()

    def run(self):
        if not self.filename:
            print('choose a file first')
            return
        
        output_path = os.path.join(self.output_directory, self.output_filename_entry.get())

        print('run')

        x_img = int(self.y_entry.get())
        y_img = int(self.x_entry.get())
        iterations = int(self.iter_entry.get())
        print('at (%d, %d), %d iterations' % (x_img, y_img, iterations))


        img = classical.run(self.filename, x_img, y_img, iterations, lambda img: self.redraw_contour(img))
        print('classical returned')
        self.figure.savefig(output_path, format='png', dpi=1200)

def main():
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()
