# mocapMath
Motion capture is expensive and complex, but what if it wasn't?

### :boom: New Blender Add-on :boom:
There is now an add-on for Blender 2.8x which dramatically simplifies the import/export process the project uses.

### :construction: Work in Progress  :construction:
Enough things work that if *everything* is done perfectly you will get proper results, otherwise `mocapSolver.py` will get very upset, so upset in fact it won't even tell you what's wrong.

## Abstract
Motion capture isn't a new technology but rather it is well established.  Unfortunatly the tools used by the VFX industry on major motion pictures are expensive.  Specialized suits and/or capture studios aren't easy to come by.

At it's core motion capture is just geometric math, taking 2D images and comparing them to create 3D points.  The idea here is to use the free and open source Blender application's camera tracker to track and align multiple cameras in order to reconstruct 3D positional data of an actor's joints.

## Instructions
0. Install the Blender Add-on to the `addons` folder of your Blender 2.8x install.  The mocapMath Utility panel will appear in the _Misc_ tab alongside the tool settings sidebar.
1. In two seperate `.blend` files use the Blender Motion Tracking workspace to track and solve each camera based on pre-synced footage.  Use Blender's camera solver's _floor_, _origin_, _x-axis_, and _set scale_ tools to align each camera based on the same tracks in their respective files.
2. Within each Blender file select the camera created out of the solve and select `Export Camera` from the _mocapMath Utility_ panel.
    - Blender will export `*_CAMERAexport.txt` files in the same directory as the `.blend` files.
3. In two additional seperate `.blend` files use the Blender Motion Tracking workspace to track the motion capture joints.
    - Tracks don't need to last the entire frame range, they can cut in and out, but they should be tracked for every possible frame.
    - Tracks of the same point **_must_** have the same _Track Name_.
        - Use naming scheme `joint.##`
4. Within each Blender file select `Export Trackers` from the _mocapMath Utility_ panel.
    - Blender will export `*_TRACKexport.txt` files in the same directory as the `.blend` files.
5. Run `mocapSolver.py` in your IDE of choice.
    - **Dependencies:** numPy, [mathutils](https://github.com/majimboo/py-mathutils)
6. When prompted select the previously exported `*.txt` files.
    - **Note:** the order in which the files are opened matters, first both camera and track from one scene followed by camera and track from the other.
7. Select a directoy to export the generated solve data but __*DO NOT*__ change the prefilled filename `mocapSolved.txt`.
8. Open a new `.blend` file and save it in the same directory as your `mocapSolved.txt`.
9. Select `Import Solve` from the _mocapMath Utility_ panel.  Blender will create and animate cubes at every point in 3D space where the same tracker was tracked from both cameras.
