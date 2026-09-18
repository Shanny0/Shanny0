#!/usr/bin/env python3
"""Rebuild every Lottie animation in this folder.

    python3 build.py

Each illustration has its own scene file (build_canvas.py, build_window.py) built on the
shared toolkit in lottiekit.py. Running a scene file directly rebuilds just that one.
"""

import build_apps
import build_canvas
import build_editor
import build_flow
import build_phone
import build_window

SCENES = (build_canvas, build_window, build_phone, build_editor, build_flow, build_apps)

if __name__ == "__main__":
    for scene in SCENES:
        scene.main()
