# Puzzle Game with Hand Gesture Control

This is an interactive puzzle game built using OpenCV, Streamlit, and CvZone's HandTrackingModule. The game uses hand gestures for dragging and snapping puzzle pieces into place.

## Features
- Upload an image to split it into puzzle pieces
- Drag and snap puzzle pieces using hand gestures
- Real-time webcam feed for gesture control
- Responsive interface built with Streamlit

## Requirements
Ensure you have the following dependencies installed:
```
streamlit==1.40.1
Pillow==10.4.0
numpy==1.24.3
opencv-python==4.10.0.84
cvzone==1.5.6
```

## Installation
1. Clone the repository:
```
git clone <repository-url>
```
2. Navigate to the project directory:
```
cd puzzle-game
```
3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
1. Run the Streamlit application:
```
streamlit run app.py
```
2. Upload an image through the web interface.
3. Start solving the puzzle using hand gestures!

## How to Play
- Upload an image, which will be resized to 225x225 pixels.
- The image will be split into puzzle pieces.
- Use your hand gestures to drag and drop pieces into the correct positions.
- Once all pieces are in the correct places, the game will display "Puzzle Completed!"

## Acknowledgements
- OpenCV for image processing and webcam integration
- CvZone for hand gesture recognition
- Streamlit for the frontend interface

## License
This project is licensed under the MIT License.

