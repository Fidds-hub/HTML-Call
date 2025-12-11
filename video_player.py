import vlc
import time
import sys
import tkinter as tk
from tkinter import filedialog
from threading import Thread

# --- Global Variables ---
player = None
instance = None
root = None

def select_file_and_play():
    """
    Opens the file dialog and starts the VLC player in a separate thread.
    """
    global player, instance, root

    # 1. Open File Dialog
    # Tkinter's askopenfilename provides a native OS file selection window.
    video_path = filedialog.askopenfilename(
        title="Select Video File",
        # You can add common video file extensions here
        filetypes=[
            ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv"), 
            ("All files", "*.*")
        ]
    )

    if not video_path:
        print("No file selected. Aborting playback.")
        return

    print(f"Selected file: {video_path}")
    
    # 2. Stop existing playback if any
    if player and player.is_playing() or player and player.get_state() == vlc.State.Paused:
        print("Stopping current playback...")
        player.stop()
        
    # 3. Start playback in a new thread
    # Running VLC playback in a separate thread prevents the video window
    # from freezing the Tkinter main loop (and vice versa).
    playback_thread = Thread(target=start_vlc_playback, args=(video_path,))
    playback_thread.daemon = True # Allows program to exit even if thread is running
    playback_thread.start()

def start_vlc_playback(video_path):
    """
    Handles the core VLC initialization and playback logic.
    This runs in a separate thread.
    """
    global player, instance

    # 1. Initialize VLC Instance (Only once is ideal, but safe to re-init if needed)
    if instance is None:
        print("Initializing VLC instance...")
        try:
            instance = vlc.Instance(sys.argv)
        except Exception:
            instance = vlc.Instance()
    
    # 2. Create Media Player if it doesn't exist
    if player is None:
        player = instance.media_player_new()
        
    # 3. Create Media Object from File and set it to the player
    media = instance.media_new(video_path)
    player.set_media(media)

    # 4. Start Playback
    print(f"Starting playback for: {video_path}")
    player.play()

    # The Tkinter window manages the exit, but we can print the controls
    print("\n--- Playback Controls ---")
    print("Video is playing in a separate window.")
    print("Close the main 'VLC Player' window or the video window to exit.")
    print("-------------------------\n")
    
def setup_gui():
    """
    Sets up the minimal Tkinter interface.
    """
    global root
    
    # Initialize the main window
    root = tk.Tk()
    root.title("VLC Player")
    
    # Optional: Hide the root window if you only want the file dialog to show initially.
    # root.withdraw()

    # Define the button style and text
    browse_button = tk.Button(
        root, 
        text="Browse and Play Video", 
        command=select_file_and_play,
        font=("Arial", 12),
        padx=20,
        pady=10
    )
    browse_button.pack(pady=50, padx=50)

    # Handle window close event to clean up VLC resources
    def on_closing():
        global player
        if player:
            print("Stopping VLC player and cleaning up resources...")
            player.stop()
            player = None
            # Note: The VLC instance will be destroyed when the script exits
        root.destroy()
        sys.exit() # Ensure the script fully exits the threads

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Run the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    setup_gui()
