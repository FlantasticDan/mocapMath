import tkinter as tk
import os
import csv
import cv2
from markerDetection import markerID, drawMarkerID
from cameraCalibration import importCalibration, exportCalibration, cameraCalibration, importMarkerPlacement, correlatePlacementWithDetection, solveCamera

# File Management
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class debugGUI:
    def __init__(self, master):
        self.master = master
        master.title("mocapMath Debugger")

        # Marker Detection
        self.md = tk.LabelFrame(master, text="Marker Detection Tools", padx='5px', pady='5px')

        self.imgSelect = tk.Button(self.md, text="Select Image", command=self.selectImage)
        self.imgSelect.pack()

        self.imgNameLabel = tk.Label(self.md, text="No Image Selected")
        self.imgNameLabel.pack()

        self.findMarkers = tk.Button(self.md, text="Detect Markers in Image", command=self.detectMarkers)
        self.findMarkers.pack()

        self.markerLabel = tk.Label(self.md, text="No Markers Detected")
        self.markerLabel.pack()

        self.exportAnnotatedMarker = tk.Button(self.md, text='Export Annotated Image', command=self.exportImage)
        self.exportAnnotatedMarker.pack()


        # Camera Calibration
        self.cc = tk.LabelFrame(master, text="Camera Calibration Tools", padx='5px', pady='5px')

        self.calibrationLabel = tk.Label(self.cc, text="Camera Uncalibrated")
        self.calibrationLabel.pack()

        self.importCalButton = tk.Button(self.cc, text="Import Camera Calibration", command=self.importCalibrationUI)
        self.importCalButton.pack()

        self.calibrateButton = tk.Button(self.cc, text="Calibrate Camera", command=self.calibrateCamera)
        self.calibrateButton.pack()

        self.exportCalButton = tk.Button(self.cc, text='Export Camera Calibration', command=self.exportCalibrationUI)
        self.exportCalButton.pack()

        ## Camera Solve
        self.cs = tk.LabelFrame(self.cc, text="Camera Solve", padx='5px', pady='5px')

        self.markerPosLabel = tk.Label(self.cs, text="Marker Placement Missing")
        self.markerPosLabel.pack()

        self.markerImport = tk.Button(self.cs, text='Import Marker Configuration', command=self.importMarkerPosition)
        self.markerImport.pack()

        self.solveButton = tk.Button(self.cs, text='Solve Camera', command=self.solveCam)
        self.solveButton.pack()

        self.cs.pack()

        # Geometry Management
        self.md.grid(row=1, column=1, sticky="N"+"S", padx=5, pady=5)
        self.cc.grid(row=1, column=2, sticky="N"+"S", padx=5, pady=5)

        ### Variables ###
        self.imgPath = None
        self.markersDetected = None
        self.matrix = None
        self.distortion = None
        self.fov = None
        self.SENSORS = []
        self.sensorx = tk.StringVar()
        self.sensory = tk.StringVar()
        self.senW = None
        self.senH = None
        self.patColumns = tk.StringVar()
        self.patRows = tk.StringVar()
        self.markerPlacement = None
        self.camPosition = None
        self.camRotation = None

    def selectImage(self):
        self.imgPath = tk.filedialog.askopenfilename(title="Select an Image...")
        print(os.path.basename(self.imgPath))
        self.imgNameLabel['text'] = os.path.basename(self.imgPath)

    def exportImage(self):
        filepath = tk.filedialog.asksaveasfilename(title='Save Annotated Image As...')
        cv2.imwrite(filepath, drawMarkerID(self.imgPath, self.markersDetected))

    def detectMarkers(self):
        if self.imgPath is None:
            self.markerLabel['text'] = "Select an Image!"
            return
        self.markersDetected = markerID(self.imgPath)
        self.markerLabel['text'] = "Markers Detected"

    def importCalibrationUI(self):
        calPath = tk.filedialog.askopenfilename(title='Select a Calibration File...')
        self.matrix, self.distortion, self.fov = importCalibration(calPath)
        self.calibrationLabel['text'] = "Camera Calibrated"

    def importMarkerPosition(self):
        filepath = tk.filedialog.askopenfilename(title="Select a Marker Configuration File...")
        self.markerPlacement = importMarkerPlacement(filepath)
        self.markerPosLabel['text'] = "Marker Placement Imported"

    def solveCam(self):
        img, obj = correlatePlacementWithDetection(self.markerPlacement, self.markersDetected)
        self.camPosition, self.camRotation = solveCamera(self.matrix, self.distortion, img, obj)

        infoMessage = "POSITION ({}, {}, {})\nROTATION ({}, {}, {})".format(self.camPosition[0],
                                                                            self.camPosition[1],
                                                                            self.camPosition[1],
                                                                            self.camRotation[0],
                                                                            self.camRotation[1],
                                                                            self.camRotation[2])

        tk.messagebox.showinfo(title='Camera Solve Data', message=infoMessage)

    def exportCalibrationUI(self):
        destination = tk.filedialog.asksaveasfilename(title="Save Calibration As...", 
                                                      defaultextension='.npz')
        exportCalibration(destination, self.matrix, self.distortion, self.fov)
        self.calibrationLabel['text'] = "Camera Calibration Exported"

    def getSensor(self, entry):
        return entry[3]

    def getSensorInfo(self, model):
        for sensor in self.SENSORS:
            if sensor[3] == model:
                self.sensorx.set(sensor[1])
                self.sensory.set(sensor[2])

    def calibrateCamera(self):
        calSettings = tk.Toplevel(padx='5px', pady='5px')
        calSettings.title("Camera Calibration Settings")
        calSettings.minsize(width=200, height=10)

        # Sensors
        with open(resource_path("./sensors.csv"), newline='') as database:
            data = csv.reader(database)
            for sensor in data:
                self.SENSORS.append(sensor)
        self.SENSORS.pop(0)

        sensorSelection = tk.StringVar(calSettings)
        sensorSelection.set('Select a Sensor')

        sensorDropDown = tk.OptionMenu(calSettings, sensorSelection,
                                       *map(self.getSensor, self.SENSORS),
                                       command=self.getSensorInfo)
        sensorDropDown.pack()

        sensorPanel = tk.LabelFrame(calSettings, text="Sensor", padx='5px', pady='5px')
        tk.Label(sensorPanel, text="Width").grid(row=2, column=1)
        tk.Label(sensorPanel, text="Height").grid(row=2, column=2)

        self.senW = tk.Entry(sensorPanel, width=7, textvariable=self.sensorx)
        self.senH = tk.Entry(sensorPanel, width=7, textvariable=self.sensory)
        self.senW.grid(row=1, column=1)
        self.senH.grid(row=1, column=2)

        sensorPanel.pack()

        # Patterns
        patternPanel = tk.LabelFrame(calSettings, text='Pattern', padx='5px', pady='5px')

        tk.Label(patternPanel, text="Columns").grid(row=2, column=1)
        tk.Label(patternPanel, text="Rows").grid(row=2, column=2)

        patCol = tk.Entry(patternPanel, width=7, textvariable=self.patColumns)
        patRow = tk.Entry(patternPanel, width=7, textvariable=self.patRows)
        patCol.grid(row=1, column=1)
        patRow.grid(row=1, column=2)

        patternPanel.pack()

        confirmButton = tk.Button(calSettings, text="Run Calibration", command=calSettings.destroy)
        confirmButton.pack()

        calSettings.wait_window()

        imgDir = tk.filedialog.askdirectory(title="Select Directory of Camera Calibration Images")
        self.matrix, self.distortion, self.fov = cameraCalibration(imgDir, self.sensorx.get(),
                                                                   self.sensory.get(),
                                                                   self.patternColumns.get(),
                                                                   self.patternRows.get())

        if self.matrix is not None:
            self.calibrationLabel['text'] = "Camera Calibrated"
        


root = tk.Tk()
gui = debugGUI(root)

root.mainloop()
