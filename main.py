import streamlit as st
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import random
import tempfile
import os

# Streamlit UI
st.title("Puzzle Game with Hand Tracking")
st.write("Upload an image to create a puzzle.")

# Upload Image
uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Save the uploaded image temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(uploaded_file.read())
    image_path = temp_file.name
    
    # Load and resize image
    img = cv2.imread(image_path)
    resized_img = cv2.resize(img, (225, 225))
    
    # Display the resized image
    st.image(resized_img, channels="BGR", caption="Resized Image (225x225)")
    
    # Initialize hand detector
    detector = HandDetector(detectionCon=0.8)
    
    # Split image into puzzle pieces
    def split_image_into_pieces(img, rows, cols):
        h, w = img.shape[:2]
        piece_height = h // rows
        piece_width = w // cols
        pieces = []
        for r in range(rows):
            for c in range(cols):
                piece = img[r * piece_height:(r + 1) * piece_height, c * piece_width:(c + 1) * piece_width]
                pieces.append(piece)
        return pieces, (h, w)

    # Class to handle draggable puzzle pieces
    class PuzzlePiece():
        def __init__(self, img, posOrigin):
            self.img = img
            self.posOrigin = posOrigin
            self.size = img.shape[:2]  # Get height and width of the piece
            self.is_snapped = False  # Track if the piece is snapped to a sub-box
            self.is_dragging = False

        def update(self, cursor, is_clicking):
            ox, oy = self.posOrigin
            h, w = self.size
            if cursor is not None and ox < cursor[0] < ox + w and oy < cursor[1] < oy + h and is_clicking:
                self.posOrigin = cursor[0] - w // 2, cursor[1] - h // 2
                self.is_snapped = False  # Reset snapping state when dragging
                self.is_dragging = True
            else:
                self.is_dragging = False

    # Puzzle setup
    rows, cols = 2, 2
    pieces, original_size = split_image_into_pieces(resized_img, rows, cols)
    
    # Create draggable puzzle pieces with non-overlapping random positions
    listPieces = []
    occupied_positions = set()
    for i, piece in enumerate(pieces):
        while True:
            x = random.randint(50, 1000)
            y = random.randint(50, 500)
            piece_rect = (x, y, piece.shape[1], piece.shape[0])
            overlap = False
            for ox, oy, ow, oh in occupied_positions:
                if not (x + piece_rect[2] < ox or x > ox + ow or y + piece_rect[3] < oy or y > oy + oh):
                    overlap = True
                    break
            if not overlap:
                occupied_positions.add(piece_rect)
                listPieces.append(PuzzlePiece(piece, [x, y]))
                break

    # Create the outline box for the completed puzzle
    outline_x, outline_y = 800, 100
    outline_h, outline_w = original_size

    # Create sub-boxes inside the outline box
    sub_boxes = []
    piece_height = outline_h // rows
    piece_width = outline_w // cols
    for r in range(rows):
        for c in range(cols):
            sub_box_x = outline_x + c * piece_width
            sub_box_y = outline_y + r * piece_height
            sub_boxes.append((sub_box_x, sub_box_y, piece_width, piece_height))
    
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    while cap.isOpened():
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        cursor = None
        is_clicking = False
        if hands:
            lmList = hands[0]['lmList']
            p1 = lmList[8][0:2]
            p2 = lmList[12][0:2]
            length, _, img = detector.findDistance(p1, p2, img)
            cursor = lmList[8][0:2]
            is_clicking = length < 60

        # Update and draw all puzzle pieces
        for piece in listPieces:
            piece.update(cursor, is_clicking)
            h, w = piece.size
            ox, oy = piece.posOrigin

            # Snap to the nearest sub-box only when released
            if not piece.is_dragging and not piece.is_snapped:
                min_distance = float('inf')
                nearest_sub_box = None
                for sub_box in sub_boxes:
                    sub_box_x, sub_box_y, sub_box_w, sub_box_h = sub_box
                    sub_box_center_x = sub_box_x + sub_box_w // 2
                    sub_box_center_y = sub_box_y + sub_box_h // 2
                    distance = np.sqrt((ox + w // 2 - sub_box_center_x)**2 + (oy + h // 2 - sub_box_center_y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_sub_box = sub_box

                tolerance = 50
                if min_distance < tolerance:
                    sub_box_x, sub_box_y, _, _ = nearest_sub_box
                    piece.posOrigin = [sub_box_x, sub_box_y]
                    piece.is_snapped = True

            img[oy:oy + h, ox:ox + w] = piece.img

        # Draw the outline box for the completed puzzle
        cv2.rectangle(img, (outline_x, outline_y), (outline_x + outline_w, outline_y + outline_h), (0, 255, 0), 2)
        
        # Draw sub-boxes inside the outline box
        for sub_box in sub_boxes:
            sub_box_x, sub_box_y, sub_box_w, sub_box_h = sub_box
            cv2.rectangle(img, (sub_box_x, sub_box_y), (sub_box_x + sub_box_w, sub_box_y + sub_box_h), (255, 0, 0), 2)

        # Display "Puzzle Completed!" if all pieces are in place
        if all(piece.is_snapped for piece in listPieces):
            cv2.putText(img, "Puzzle Completed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the final image
        cv2.imshow("Puzzle Game", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
