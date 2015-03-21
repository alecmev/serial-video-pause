# serial-video-pause

A yet another utility for an Ekselcom product related to video playback with
ambient lighting. Sends a predefined set of bytes to a serial device, plays a
video in fullscreen right after that, then waits N seconds, and goes back to
step 1. Prerequisites:

* Python 3
* VLC 2

Run `setup.bat` to get the remaining dependencies. Should work on any OS
supported by both Python and VLC. Use `com0com` if you have no actual hardware.
