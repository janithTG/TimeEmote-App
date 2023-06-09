import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
import cv2
from PyQt5.QtWidgets import QApplication
import time
from deepface import DeepFace
import webbrowser
import random
from plyer import notification
from tkinter import messagebox
import tkinter as tk


def write_link_to_file(link):
    with open('music_links.txt', 'a') as f:
        f.write(link + "\n")

class LinkSaver(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeEmote")
        self.resize(400, 200)

        # Create widgets

        self.link_label = QLabel("Enter at least one YouTube Link:")
        self.link_label.setFont(QFont("Helvetica", 14))
        self.link_entry = QLineEdit()
        self.link_entry.setPlaceholderText("Paste YouTube link here...")
        self.link_entry.setFont(QFont("Helvetica", 14))
        self.save_button = QPushButton("Save Link")
        self.save_button.clicked.connect(self.save_link)
        self.save_button.setFont(QFont("Helvetica", 16))
        self.save_button.setStyleSheet(
            "QPushButton {"
            "background-color: #5BC0EB;"
            "border-style: outset;"
            "border-radius: 10px;"
            "border-width: 2px;"
            "border-color: beige;"
            "padding: 6px;"
            "}"
            "QPushButton:hover {"
            "background-color: #6C5B7B;"
            "color: white;"
            "}"
        )


        # Create run code button
        self.run_button = QPushButton("Run Code")
        self.run_button.clicked.connect(self.minimize)
        self.run_button.clicked.connect(self.run_code)
        self.run_button.setFont(QFont("Helvetica", 16))
        self.run_button.setStyleSheet(
            "QPushButton {"
            "background-color: #5BC0EB;"
            "border-style: outset;"
            "border-radius: 10px;"
            "border-width: 2px;"
            "border-color: beige;"
            "padding: 6px;"
            "}"
            "QPushButton:hover {"
            "background-color: #6C5B7B;"
            "color: white;"
            "}"
        )

        # Create close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_window)
        self.close_button.setFont(QFont("Helvetica", 16))
        self.close_button.setStyleSheet(
            "QPushButton {"
            "background-color: #FF0000;"
            "border-style: outset;"
            "border-radius: 10px;"
            "border-width: 2px;"
            "border-color: beige;"
            "padding: 6px;"
            "}"
            "QPushButton:hover {"
            "background-color: #6C5B7B;"
            "color: white;"
            "}"
        )

        # Create layout
        layout = QVBoxLayout()
        layout.addWidget(self.link_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.link_entry, alignment=Qt.AlignCenter)
        layout.addWidget(self.save_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.run_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def minimize(self):
        self.showMinimized()

    def save_link(self):
        link = self.link_entry.text()
        write_link_to_file(link)
        self.link_entry.clear()


    def run_code(self):
        self.run_button.clicked.connect(self.showMinimized)
        song_start_time = 0

        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)

        # Initialize timer and flag
        start_time = 0
        last_detection_time = 0
        person_detected = False
        song_playing = False

        # cap.set(3, 640)  # set Width
        # cap.set(4, 480)  # set Height

        while True:
            # Read frames from webcam
            ret, frame = cap.read()

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Convert to the desired depth
            gray = cv2.convertScaleAbs(gray)

            # Detect faces in the frame using the face cascade classifier
            faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw rectangle around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Loop through each face and detect the emotion using DeepFace
            for (x, y, w, h) in faces:
                face_img = frame[y:y + h, x:x + w]
                try:
                    results = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=True)
                    emotion = results[0]['dominant_emotion']
                    print(emotion)
                except ValueError as ve:
                    print(f"Error: {ve}")
                    continue

                # Draw a rectangle around the face and display the dominant emotion
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

                # Display output
                # cv2.imshow('frame', frame)

                # Play happy song if emotion is sad




                if emotion == "sad" and (time.time() - song_start_time > 0.5 * 60 or song_start_time == 0):
                    if not song_playing:  # check if song is not already playing
                        root = tk.Tk()
                        root.withdraw()
                        response = messagebox.askyesno('TimeEmote | Play a Happy Song', 'Would you like to play a happy song?')

                        if response:
                            song_playing = True
                            song_start_time = time.time()
                            with open('music_links.txt', 'r') as f:
                                links = f.readlines()

                            # Choose a random link
                            random_link = random.choice(links).strip()

                            webbrowser.open(random_link)
                            song_playing = False


            if not song_playing:
                # Display the resulting frame
                cv2.imshow('TimeEmote', frame)

            # Check if a person is detected
            if len(faces) > 0:
                person_detected = True
                last_detection_time = time.time()

                if start_time == 0:
                    # Start timer
                    start_time = time.time()
                    print('start time is :', start_time)
            else:
                person_detected = False

            # Check if 2 minutes have passed man is in or not there
            if not person_detected and time.time() - last_detection_time > 0.2 * 60:
                # Pause timer
                start_time = 0

            # Check if 20 minutes have passed
            if person_detected and time.time() - start_time > 1 * 60:
                # Display message on screen
                cv2.putText(frame, "20 minutes of inactivity. Please move.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 2)

                # print(time.time())
                # print("please move")

                notification.notify(
                    title='TimeEmote | Time Tracker',
                    message='Time for a Break',
                    app_name='Desk Meter',
                    timeout=15
                )

                cv2.imshow('TimeEmote', frame)

                # Reset timer
                start_time = time.time()

                # Press 'q' to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        pass

    def close_window(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("background-color: #E0E0E0;")
    link_saver = LinkSaver()
    link_saver.show()
    sys.exit(app.exec_())