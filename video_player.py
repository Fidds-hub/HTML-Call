import vlc
import sys
import time
import platform
import tkinter as tk
from tkinter import filedialog, ttk

class MinimalVideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimal VLC Player")
        self.root.geometry("800x600")
        
        # --- VLC Instance Setup ---
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.is_playing = False

        # --- UI Layout ---
        self._setup_ui()
        
        # --- Events ---
        # Handle closing the window properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ui(self):
        """Builds the GUI elements."""
        
        # 1. Video Display Area (The "Screen")
        # We use a black Canvas to act as the video container
        self.video_frame = tk.Canvas(self.root, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # 2. Controls Container
        controls_frame = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        controls_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 3. Progress Slider
        self.time_var = tk.DoubleVar()
        self.progress_slider = tk.Scale(
            controls_frame, 
            variable=self.time_var, 
            command=self.on_seek,
            orient="horizontal",
            showvalue=0,  # Hide the number above the slider
            bg="#f0f0f0",
            troughcolor="#d0d0d0",
            sliderlength=15
        )
        self.progress_slider.pack(fill=tk.X, padx=10, pady=5)

        # 4. Buttons & Volume
        btn_frame = tk.Frame(controls_frame, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, padx=10)

        self.btn_load = tk.Button(btn_frame, text="Load", command=self.load_video, width=10)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.btn_play = tk.Button(btn_frame, text="Play", command=self.toggle_play, width=10)
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(btn_frame, text="Stop", command=self.stop, width=10)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # Volume Label and Slider
        tk.Label(btn_frame, text="Vol:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(20, 5))
        self.vol_slider = tk.Scale(
            btn_frame, 
            from_=0, to=100, 
            orient="horizontal", 
            command=self.set_volume,
            bg="#f0f0f0",
            length=100,
            showvalue=0
        )
        self.vol_slider.set(50) # Default volume
        self.vol_slider.pack(side=tk.LEFT)

        # Time Label (00:00 / 00:00)
        self.lbl_time = tk.Label(btn_frame, text="00:00 / 00:00", bg="#f0f0f0")
        self.lbl_time.pack(side=tk.RIGHT, padx=10)

    def load_video(self):
        """Opens file dialog and loads media."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Video", "*.mp4 *.avi *.mkv *.mov"), ("All", "*.*")]
        )
        if not filepath:
            return

        # Create media
        media = self.instance.media_new(filepath)
        self.player.set_media(media)

        # EMBEDDING LOGIC:
        # We must tell VLC to draw inside our Tkinter Canvas using the OS-specific Window ID.
        window_id = self.video_frame.winfo_id()
        
        system_platform = platform.system()
        if system_platform == "Windows":
            self.player.set_hwnd(window_id)
        elif system_platform == "Linux":
            self.player.set_xwindow(window_id)
        elif system_platform == "Darwin": # macOS
            # Note: macOS embedding with Tkinter can be tricky depending on the VLC version.
            try:
                # This requires an integer ID.
                self.player.set_nsobject(int(window_id))
            except Exception:
                print("MacOS embedding warning: Might open in separate window.")

        self.play()

    def play(self):
        """Starts playback and the UI update loop."""
        self.player.play()
        self.btn_play.config(text="Pause")
        self.is_playing = True
        self.root.after(100, self.update_progress)

    def toggle_play(self):
        """Toggles between Play and Pause."""
        if self.player.get_media() is None:
            return # Do nothing if no video loaded

        if self.player.is_playing():
            self.player.pause()
            self.btn_play.config(text="Play")
            self.is_playing = False
        else:
            self.player.play()
            self.btn_play.config(text="Pause")
            self.is_playing = True
            self.root.after(100, self.update_progress)

    def stop(self):
        """Stops playback and resets UI."""
        self.player.stop()
        self.btn_play.config(text="Play")
        self.time_var.set(0)
        self.lbl_time.config(text="00:00 / 00:00")
        self.is_playing = False

    def set_volume(self, val):
        """Sets the volume (0-100)."""
        volume = int(val)
        self.player.audio_set_volume(volume)

    def on_seek(self, val):
        """Handles slider drag to seek video."""
        # Note: 'val' comes in as a string from the Scale widget
        if self.player.get_media() is None:
            return
            
        # Only seek if the difference is significant to avoid jitter during auto-update
        # (This is a simplified approach; usually you'd check if user is clicking the mouse)
        target_time = int(float(val))
        current_time = self.player.get_time()
        
        # If the seek request is far from current time, perform seek
        if abs(target_time - current_time) > 1000: 
            self.player.set_time(target_time)

    def update_progress(self):
        """
        Periodically updates the slider and time label.
        Refreshes every 500ms.
        """
        if not self.is_playing:
            return

        # Get total duration (length) and current time
        length = self.player.get_length() # in ms
        current_time = self.player.get_time() # in ms

        # Update slider range and value
        # We only update range if it changed (optimization)
        if length > 0:
            if self.progress_slider.cget("to") != length:
                self.progress_slider.config(to=length)
            
            # Update the slider position to match video
            self.time_var.set(current_time)

            # Update Label Text
            self.lbl_time.config(text=f"{self._format_time(current_time)} / {self._format_time(length)}")

        # Schedule next update
        self.root.after(500, self.update_progress)

    def _format_time(self, ms):
        """Helper to convert milliseconds to MM:SS format."""
        if ms < 0: return "00:00"
        seconds = int(ms / 1000)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def on_close(self):
        """Cleanup logic."""
        self.player.stop()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinimalVideoPlayer(root)
    root.mainloop()
