# mocapMath
Motion capture is expensive and complex, but what if it wasn't?

## Abstract
Motion capture isn't a new technology but rather it is well established.  Unfortunatly the tools used by the VFX industry on major motion pictures are expensive.  Specialized suits and/or capture studios aren't easy to come by.

At it's core all motion capture is geometric math, taking 2D images and comparing them to create 3D points.  The idea here is to use the free and open source Blender application's camera tracker to track and align multiple cameras in order to reconstruct 3D positional data of an actor's joints.

## Instructions
1. In two seperate `.blend` files use the Blender Motion Tracking workspace to track and solve each camera based on pre-synced footage.  Use Blender's camera solver's _floor_, _origin_, _x-axis_, and _set scale_ tools to align each camera based on the same tracks in their respective files.
2. Within each Blender file select the camera created out of the solve and run `blenderCameraExport.py`.
    - Blender will export `*_CAMERAexport.txt` files in the same directory as the `.blend` files.
3. In two additional seperate `.blend` files use the Blender Motion Tracking workspace to track the motion capture joints.
    - Tracks don't need to last the entire frame range, they can cut in and out.
    - Tracks of the same point **_must_** have the same _Track Name_.
        - Use naming scheme `joint_##`
4. Within each Blender file run `blenderTrackExport.py`.
    - Blender will export `*_TRACKexport.txt` files in the same directory as the `.blend` files.
5. Run `mocapSolver.py` in your IDE of choice.
    - **Dependencies:** numPy
6. When prompted select the previously exported `*.txt` files.
    - **Note:** the order in which the files are opened matters, first both camera and track from one scene followed by camera and track from the other.
7. Select a directoy to export the generated solve data but __*DO NOT*__ change the prefilled filename `mocapSolved.txt`.