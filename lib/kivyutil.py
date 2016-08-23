import os

CMD = r"""
set KIVY_PORTABLE_ROOT=C:\Users\Jonas\Desktop\temp_gk\Kivy-1.9.0-py3.4-win32-x86
set PY_VER=34
set PYTHON_DIR=Python%PY_VER%
set KIVY_DIR=kivy%PY_VER%
set GST_REGISTRY=%KIVY_PORTABLE_ROOT%gstreamer\registry.bin
set KIVY_SDL2_PATH=%KIVY_PORTABLE_ROOT%SDL2\lib;%KIVY_PORTABLE_ROOT%SDL2\include\SDL2;%KIVY_PORTABLE_ROOT%SDL2\bin
set USE_SDL2=1
set GST_PLUGIN_PATH=%KIVY_PORTABLE_ROOT%gstreamer\lib\gstreamer-1.0
set PATH=%KIVY_PORTABLE_ROOT%;%KIVY_PORTABLE_ROOT%%PYTHON_DIR%;%KIVY_PORTABLE_ROOT%tools;%KIVY_PORTABLE_ROOT%%PYTHON_DIR%\Scripts;%KIVY_PORTABLE_ROOT%gstreamer\bin;%KIVY_PORTABLE_ROOT%MinGW\bin;%KIVY_PORTABLE_ROOT%SDL2\bin;%PATH%
set PKG_CONFIG_PATH=%KIVY_PORTABLE_ROOT%gstreamer\lib\pkgconfig;%PKG_CONFIG_PATH%
set PYTHONPATH=%KIVY_PORTABLE_ROOT%%KIVY_DIR%;%PYTHONPATH%
set kivy_paths_initialized=1
"""

def init_kivy():

    os.system(CMD)
    print("Done")
