import pygame
import numpy as np
from scipy.io.wavfile import write

# Create alarm sound file
def create_alarm_sound():
    # Set parameters
    sample_rate = 44100  # Sample rate in Hz
    duration = 2  # Duration in seconds
    frequency = 440  # Frequency in Hz (A4 note)
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave
    note = np.sin(2 * np.pi * frequency * t)
    
    # Add higher frequency for alarm effect
    alarm = note + 0.5 * np.sin(2 * np.pi * frequency * 2 * t)
    
    # Normalize to prevent clipping
    alarm = alarm / np.max(np.abs(alarm))
    
    # Convert to 16-bit PCM
    alarm = (alarm * 32767).astype(np.int16)
    
    # Save as WAV file
    write("alarm.mp3", sample_rate, alarm)
    print("Alarm sound created as 'alarm.mp3'")

# Create notification sound file
def create_notification_sound():
    # Set parameters
    sample_rate = 44100  # Sample rate in Hz
    duration = 1  # Duration in seconds
    frequency = 523.25  # Frequency in Hz (C5 note)
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave with fade-out
    note = np.sin(2 * np.pi * frequency * t)
    fade = np.linspace(1, 0, int(sample_rate * duration))**2
    notification = note * fade
    
    # Normalize to prevent clipping
    notification = notification / np.max(np.abs(notification))
    
    # Convert to 16-bit PCM
    notification = (notification * 32767).astype(np.int16)
    
    # Save as WAV file
    write("notification.mp3", sample_rate, notification)
    print("Notification sound created as 'notification.mp3'")

if __name__ == "__main__":
    create_alarm_sound()
    create_notification_sound()
    print("Sound files created successfully!")