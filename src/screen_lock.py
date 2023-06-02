import ctypes
import time

# Define constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


# Prevent screen lock
def prevent_screen_lock():
    # Set the thread execution state to prevent screen lock
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


# Release screen lock prevention
def release_screen_lock():
    # Release the thread execution state
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


# Prevent screen lock indefinitely
def run_prevent_screen_lock():
    while True:
        prevent_screen_lock()
        time.sleep(30)  # Adjust the delay as needed
