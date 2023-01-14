![Screenshot](https://user-images.githubusercontent.com/17131686/212317142-6f3a021d-a7af-4114-84c0-c73b2190846a.png)
The author standing before the VL53L5CX, with his right side towards the viewer.

# RemoteViewer
View frames from the multizone ToF sensor VL53L5CX from a 3rd person point of view.
The name is a joke inspired by the movie "The men who stare at goats", where one of the antagonists of the movie is a former "remote viewer" for "new earth army". A remote viewer uses astral projection to see things remotely. When you are using this program, you are the astral projection of the VL53L5CX.

The linear algebra and 3d stuff in this program is based on this tutorial:
https://www.youtube.com/watch?v=M_Hx0g5vFko

## Try it out
Clone the repo and navigate to it in your shell.
I know that there is an union with the PEP 604 shorhand somewhere (e.g. argument: str | None), so at least Python 10 is required.
Create a virtual environment with python 3.10 or above.
pip install -r requirements.txt
python main.py --replay -i example_logs\log1.json -f 5

## Features
### Camera view
The camera view can be moved around, using WASD and some other keys (instructions in the program). If you get lost, home the camera by pressing R

### Mode: Live view
The program can read and display output from the sensor live, by specifying a serial (COM) port and baudrate. The data received on the serial port must conform to the format the parser in VL53L5CX parses the data. This format is not yet specified in a good way and is subject to change. Feel free to suggest new formats.

#### Record live view to file
A log is automatically saved to a file when the program starts in Live view mode.

### Mode: Replay view
Replay a saved log. The user can pause/start, toggle reverse play, scroll through the log frame by frame.
- Play/Pause
- Next/Previous frame
- Replay direction
