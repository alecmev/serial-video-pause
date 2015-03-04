@ECHO OFF

pip install pyserial
powershell -command "& { iwr 'http://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=generated/vlc.py;hb=HEAD' -OutFile vlc.py }"
echo @python main.py test.mp4 test.hex COM3 2 -dws > test.bat
powershell -command "& { iwr 'http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4' -OutFile test.mp4 }"
echo 414243 > test.hex
