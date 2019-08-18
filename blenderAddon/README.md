# mocapMath Addon for Blender

## Installing
1. Copy the enitre `mocapMath` folder into your Blender installation's `addons` folder.
2. Copy the built binary of `mocapSolver.exe` into the `mocapMath` folder.
    - Instructions for building `mocapSolver` can be found [here](https://github.com/FlantasticDan/mocapMath)
    - **Note:** This step can be skipped if installing from a [Github Release](https://github.com/FlantasticDan/mocapMath/releases) as the binaries have already been built for you.
3. Enable the Addon in Blender, it will be under the _Import-Export_ category.
4. The _mocapMath Utility_ panel will now appear in the _Misc_ tab alongside the tool settings sidebar.

## Use
1. In two seperate `.blend` files use the Blender Motion Tracking workspace to track and solve each camera based on pre-synced footage.  Use Blender's camera solver's _floor_, _origin_, _x-axis_, and _set scale_ tools to align each camera based on the same tracks in their respective files.
2. Within each Blender file select the camera created out of the solve and select `Export Camera` from the _mocapMath Utility_ panel.
    - Blender will export `*_CAMERAexport.txt` files in the same directory as the `.blend` files.
3. In two additional seperate `.blend` files use the Blender Motion Tracking workspace to track the motion capture joints.
    - Tracks don't need to last the entire frame range, they can cut in and out, but they should be tracked for every possible frame.
    - Tracks of the same point **_must_** have the same _Track Name_.
        - Use naming scheme `joint.##`
4. Within each Blender file select `Export Trackers` from the _mocapMath Utility_ panel.
    - Blender will export `*_TRACKexport.txt` files in the same directory as the `.blend` files.
5. Select `Launch mocapMath Solver` from the _mocapMath Utility_ panel.  This will lauch the mocapSolver binary.
6. When prompted select the previously exported `*.txt` files.
    - **Note:** the order in which the files are opened matters, first both camera and track from one scene followed by camera and track from the other.
7. Select a directoy to export the generated solve data but __*DO NOT*__ change the prefilled filename `mocapSolved.txt`.
8. Open a new `.blend` file and save it in the same directory as your `mocapSolved.txt`.
9. Select `Import Solve` from the _mocapMath Utility_ panel.  Blender will create and animate cubes at every point in 3D space where the same tracker was tracked from both cameras.