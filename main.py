import os
import sys
import cv2
import pygame
import json
from dotenv import load_dotenv
import speech_recognition as sr
import threading
from openai import OpenAI
import mediapipe as mp

load_dotenv("settings.env")
if os.getenv("OPENAI_API_KEY") == "YOUR_API_KEY":
    print("Please input your real api key into the `settings.env`")
client = OpenAI()

width, height = int(os.getenv("WIDTH")), int(os.getenv("HEIGHT"))
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
data = []


def play_sound(sound_file):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


def number_in_between(x, y):
    if x > y:
        x, y = y, x

    middle_number = (x + y) / 2

    return middle_number


def rectangle_center(x1, y1, x2, y2):
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    return x, y


def map_range(number, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    new_range = new_max - new_min

    scaled_value = (number - old_min) / old_range
    mapped_value = new_min + (scaled_value * new_range)

    return mapped_value


# Speech recognition setup
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Constants
PUPIL_RADIUS = 90
IRIS_RADIUS = 40
BG_COLOR = (224,172,105)

def speech_recognition_thread():
    global running
    print("Waiting for audio...")
    while running:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            recognized_text = recognizer.recognize_google(audio)
            print(recognized_text)
            if recognized_text.lower() == 'stop':
                running = False
                sys.exit(0)
            print("Waiting for ChatGPT output.")
            completion = client.chat.completions.create(
            model=os.getenv("GPT_CHAT_MODEL"),
            messages=[
                {"role": "system", "content": "You are a human assistant."},
                {"role": "user", "content": str(recognized_text)}
            ]
            )
            output = completion.choices[0].message.content
            print(output)
            print("Waiting for text to speech.")
            screen.fill(BG_COLOR)
            with client.audio.speech.with_streaming_response.create(model=os.getenv("GPT_AUDIO_MODEL"), voice=os.getenv("GPT_AUDIO_VOICE"), input=output) as response:
                response.stream_to_file("speech.mp3")
            play_sound("speech.mp3")
            os.remove("speech.mp3")
        except sr.UnknownValueError:
            pass

def face_recognition_thread():
    global running
    global data
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(2)
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        while running:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (width, height))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = face_detection.process(frame_rgb)
            if results.detections:
                faces = []
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                                int(bboxC.width * iw), int(bboxC.height * ih)
                    faces.append([x, y, w, h])
                    
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            data = faces

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
        

# Start the speech recognition and the face recognition thread
speech_thread = threading.Thread(target=speech_recognition_thread)
speech_thread.start()

face_thread = threading.Thread(target=face_recognition_thread)
face_thread.start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            print(pos)

    screen.fill(BG_COLOR)
    try:
        x1, y1, w, h = data[0]
        x2 = x1 + w
        y2 = y1 + h
        center = rectangle_center(x1, y1, x2, y2)
        pupil_color = (255, 255, 255)
        iris_color = (0, 0, 0)
        eye1x = (213, 76)
        eye2x = (475, 338)
        eye1y = (130, 265)
        pupil1 = (number_in_between(*eye1x))
        pupil2 = (number_in_between(*eye2x))
        iris1x = map_range(center[0], 0, width, *eye1x)
        iris2x = map_range(center[0], 0, width, *eye2x)
        iris1y = map_range(center[1], 0, height, *eye1y)
        iris2y = iris1y
        pygame.draw.circle(screen, pupil_color, (pupil1, 200), PUPIL_RADIUS, 0)
        pygame.draw.circle(screen, pupil_color, (pupil2, 200), PUPIL_RADIUS, 0)
        pygame.draw.circle(screen, iris_color, (iris1x, iris1y), IRIS_RADIUS, 0)
        pygame.draw.circle(screen, iris_color, (iris2x, iris2y), IRIS_RADIUS, 0)
    except (IndexError, json.decoder.JSONDecodeError):
        pass

    pygame.display.flip()

    clock.tick(60)

# Wait for the speech recognition thread to finish before quitting
speech_thread.join()
face_thread.join()
pygame.quit()
