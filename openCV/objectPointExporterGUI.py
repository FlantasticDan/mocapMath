"""
A GUI that is better served by an Excel spreadsheet but this too export marker world space
coordinates for camera calibration.
"""

from tkinter import *
from tkinter import filedialog

master = Tk()

# Global Variables
ROWS = 1
COLORS = []
SHAPES = []
X = []
Y = []
Z = []

def addRow(master, iteration):
    """Adds an inout row to the GUI."""
    row = Label(master, text="{:2}".format(iteration))
    row.grid(row=iteration, column=0)

    color = StringVar(master)
    color.set("")

    c = OptionMenu(master, color, "red", "yellow", "green", "cyan", "blue", "magenta")
    c.grid(row=iteration, column=1)

    shape = StringVar(master)
    shape.set("")

    s = OptionMenu(master, shape, "triangle", "circle", "square", "slash", "line", "y")
    s.grid(row=iteration, column=2)

    x = Entry(master, width=5)
    x.grid(row=iteration, column=3)

    y = Entry(master, width=5)
    y.grid(row=iteration, column=4)

    z = Entry(master, width=5)
    z.grid(row=iteration, column=5)

    global ROWS
    ROWS += 1

    COLORS.append(color)
    SHAPES.append(shape)
    X.append(x)
    Y.append(y)
    Z.append(z)

    return color, shape, x, y, z

def exportConfig():
    """Basically a CSV exporter but less optimized and with no data validation."""
    filepath = filedialog.asksaveasfile(title="Save Config File As...", defaultextension='.txt')
    count = 0
    if filepath is None:
        return
    with filepath as export:
        while count < len(COLORS):
            if COLORS[count].get() == "":
                break
            export.write("{} {} {} {} {}\n".format(COLORS[count].get(),
                                                   SHAPES[count].get(),
                                                   X[count].get(),
                                                   Y[count].get(),
                                                   Z[count].get()))
            count += 1
    export.close()


## Setup Header UI ##
rowAdd = Button(master, text="Add Row", command=lambda: addRow(master, ROWS))
rowAdd.grid(row=0, column=0)

labelColor = Label(master, text="Color", width=12)
labelColor.grid(row=0, column=1)

labelShape = Label(master, text="Shape", width=12)
labelShape.grid(row=0, column=2)

labelX = Label(master, text="x", width=6)
labelX.grid(row=0, column=3)

labelY = Label(master, text="y", width=6)
labelY.grid(row=0, column=4)

labelZ = Label(master, text="z", width=6)
labelZ.grid(row=0, column=5)

exportButton = Button(master, text="Export Configuration", command=exportConfig)
exportButton.grid(row=0, column=6)

# Enter Application Loop #
master.mainloop()
