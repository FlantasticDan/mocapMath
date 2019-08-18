# mocapMath
Motion capture is expensive and complex, but what if it wasn't?

### :boom: New Blender Add-on :boom:
There is now an add-on for Blender 2.8x which allows for a complete workflow entirely within Blender.

### :construction: Work in Progress :construction:
Enough things work that if *everything* is done perfectly you will get proper results, otherwise you probably won't.

## Abstract
Motion capture isn't a new technology but rather it is well established.  Unfortunatly the tools used by the VFX industry on major motion pictures are expensive.  Specialized suits and/or capture studios aren't easy to come by.

At it's core motion capture is just geometric math, taking 2D images and comparing them to create 3D points.  The idea is to use existing industry applications to piece together a motion capture workflow.  Up first is Blender, which is **_free_** and **_open source_**!

## Building
This project embeds itself into existing applications and as such is is highly recommended to use pre-built binary packages being distributed via [Github Releases](https://github.com/FlantasticDan/mocapMath/releases).
`mocapSolver` is the root "brain" of the operation.  It processes data exported from supported applications and prepares the solve for import into other supported applications.  Currently it must be be built into a single file executable to be supported by the Blender Addon.
### Dependencies
- numPy
- [mathutils](https://github.com/majimboo/py-mathutils)