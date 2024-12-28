import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import threading
import os
import platform
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import tkinter as tk
from tkinter import messagebox

# Initialize variables
selected_color = None
lower_bound = None
upper_bound = None
background = None
brightness = 1.0
cloak_enabled = True
reddish_filter = False
guide_displayed = False
volume_level = 1.0  # Current volume level (range 0 to 1)
running = True

# Text-to-speech engine
engine = pyttsx3.init()

def select_color(event, x, y, flags, param):
    global lower_bound, upper_bound, selected_color, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        # Get the selected color
        selected_color = frame[y, x]
        b, g, r = selected_color
        # Define bounds for the selected color
        lower_bound = np.array([max(0, b - 40), max(0, g - 40), max(0, r - 40)])
        upper_bound = np.array([min(255, b + 40), min(255, g + 40), min(255, r + 40)])
        print(f"Selected Color: {selected_color}")
        print(f"Lower Bound: {lower_bound}")
        print(f"Upper Bound: {upper_bound}")

def adjust_brightness(frame, alpha):
    """Adjust brightness."""
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=0)

def reset_spells():
    """Reset all spells to default."""
    global brightness, cloak_enabled, reddish_filter, guide_displayed, volume_level
    brightness = 1.0
    cloak_enabled = True
    reddish_filter = False
    guide_displayed = False
    volume_level = 1.0
    print("Obliviate! All spells reset.")

def adjust_system_brightness(level):
    """Adjust system brightness."""
    if platform.system() == "Windows":
        sbc.set_brightness(level * 100)  # scale level to 0-100
    elif platform.system() == "Linux":
        os.system(f"xrandr --output eDP-1 --brightness {level}")
    elif platform.system() == "Darwin":
        os.system(f"brightness {level}")

def adjust_volume(level):
    """Adjust system volume."""
    try:
        devices = AudioUtilities.GetSpeakers()  # Get the speakers device
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, 1, None)  # Activate the volume interface
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level, None)  # Set the volume to the desired level
    except Exception as e:
        print(f"Error adjusting volume: {e}")

def listen_for_spell():
    """Listen for a spell and execute its corresponding effect."""
    global running, brightness, cloak_enabled, reddish_filter, guide_displayed, volume_level
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for spells... (Say a spell)")
        while running:
            try:
                audio = recognizer.listen(source, timeout=10)  # Increased timeout
                spell = recognizer.recognize_google(audio).lower()
                print(f"You said: {spell}")
                # Handle each spell
                if spell == "lumos":
                    brightness = 2.0
                    adjust_system_brightness(1.0)  # Max brightness
                    print("Lumos! Brightness set to maximum.")
                elif spell == "nox" or spell == "knox":
                    brightness = 0.1
                    adjust_system_brightness(0.1)  # Min brightness
                    print("Nox! Brightness set to minimum.")
                elif spell == "expelliarmus":
                    cloak_enabled = False
                    print("Expelliarmus! Cloak disabled.")
                elif spell == "accio":
                    cloak_enabled = True
                    print("Accio! Cloak enabled.")
                elif spell == "sectumsempra":
                    reddish_filter = True
                    print("Sectumsempra! Adding red filter.")
                elif spell == "obliviate":
                    reset_spells()
                elif (spell == "amplification" or spell == "amplificus"):
                    # Increase volume by 5 points until maximum
                    if volume_level < 1.0:
                        volume_level = min(1.0, volume_level + 0.05)
                        adjust_volume(volume_level)
                        print(f"Amplificus! Volume increased to {volume_level * 100}%.")
                elif (spell == "minimise" or spell == "minimus"):
                    # Decrease volume by 5 points until minimum
                    if volume_level > 0.0:
                        volume_level = max(0.0, volume_level - 0.05)
                        adjust_volume(volume_level)
                        print(f"Minimus! Volume decreased to {volume_level * 100}%.")
                elif spell == "guide":
                    guide_displayed = True
                    show_guide_popup()  # Show pop-up guide
                elif spell == "close guide":
                    guide_displayed = False
                    close_guide_popup()  # Close pop-up guide
                elif spell == "avada kedavra" or spell == "avada keda" :
                    print("Avada Kedavra! Exiting the script.")
                    running = False
            except sr.WaitTimeoutError:
                pass  # Ignore timeout errors
            except sr.UnknownValueError:
                print("Could not understand the spell, try again.")

def show_guide_popup():
    """Show the spell guide in a pop-up window."""
    guide_text = """
    Spell Guide:
    - Lumos: Set brightness to maximum
    - Nox: Set brightness to minimum
    - Expelliarmus: Disable functionality
    - Accio: Enable functionality
    - Amplificus: Increase system volume
    - Minimus: Decrease system volume
    - Obliviate: Reset all spells
    - Guide: Show spell guide
    - Avada Kedavra: Exit the script
    """
    
    # Create pop-up window
    window = tk.Tk()
    window.title("Spell Guide")
    window.geometry("400x300")
    
    label = tk.Label(window, text=guide_text, justify="left", padx=10, pady=10)
    label.pack(padx=10, pady=10)
    
    # Add a button to close the pop-up
    close_button = tk.Button(window, text="Close", command=window.destroy)
    close_button.pack(pady=10)
    
    # Start the window's main loop
    window.mainloop()

def close_guide_popup():
    """Close the spell guide pop-up window."""
    for widget in tk._default_root.winfo_children():
        widget.destroy()

# Initialize the webcam
cap = cv2.VideoCapture(0)

cv2.namedWindow("Select Color")
cv2.setMouseCallback("Select Color", select_color)

selected_color = None
lower_bound = None
upper_bound = None

print("Click on the color of the cloak in the video feed to select it.")

# Capture the static background frame (press 'b' to capture)
background = None
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip the frame horizontally
    cv2.imshow("Select Color", frame)

    key = cv2.waitKey(1)
    if key == ord('b'):  # Capture background
        background = frame
        print("Background captured!")
    if key == 27:  # ESC to exit
        break

cv2.destroyWindow("Select Color")

# Start the spell listening thread
threading.Thread(target=listen_for_spell, daemon=True).start()

if background is not None and lower_bound is not None:
    print("Starting real-time invisibility cloak...")
    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Adjust brightness
        frame = adjust_brightness(frame, brightness)

        # Apply color filtering if cloak is enabled
        if cloak_enabled and lower_bound is not None and upper_bound is not None:
            mask = cv2.inRange(frame, lower_bound, upper_bound)
            # Refine the mask (remove noise)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))

            # Invert the mask
            mask_inv = cv2.bitwise_not(mask)

            # Segment the cloak area
            cloak_area = cv2.bitwise_and(background, background, mask=mask)

            # Segment the non-cloak area
            non_cloak_area = cv2.bitwise_and(frame, frame, mask=mask_inv)

            # Combine the two areas
            final_output = cv2.addWeighted(cloak_area, 1, non_cloak_area, 1, 0)

        # Apply the red filter if Sectumsempra spell is cast
        if reddish_filter:
            final_output = cv2.addWeighted(final_output, 1, np.zeros_like(final_output), 0, 50)

        cv2.imshow("Invisibility Cloak", final_output)

        key = cv2.waitKey(1)
        if key == 27:  # ESC to exit
            break

cap.release()
cv2.destroyAllWindows()
