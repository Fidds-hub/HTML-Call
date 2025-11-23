import cv2
import tkinter as tk
from tkinter import Label, Scale, Button, HORIZONTAL, filedialog
from PIL import Image, ImageTk
from pathlib import Path

class VideoPlayer:
    """Simple video player module"""
    
    def __init__(self, title="Video Player", width=800, height=600):
        self.title = title
        self.width = width
        self.height = height
        
        self.cap = None
        self.total_frames = 0
        self.fps = 30
        self.playing = False
        self.current_frame = 0
        
        # Create window
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry(f"{self.width}x{self.height + 150}")
        
        # Video display label
        self.label = Label(self.root, bg="black")
        self.label.pack(fill="both", expand=True)
        
        # Controls frame
        controls = tk.Frame(self.root)
        controls.pack(fill="x", padx=5, pady=5)
        
        # Browse button
        browse_btn = Button(controls, text="Browse Video", command=self.browse_file, width=15)
        browse_btn.pack(side="left", padx=5)
        
        # File label
        self.file_label = Label(controls, text="No file selected", fg="gray")
        self.file_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Playback controls frame
        playback = tk.Frame(self.root)
        playback.pack(fill="x", padx=5, pady=5)
        
        # Play/Pause button
        self.play_btn = Button(playback, text="Play", command=self.toggle_play, width=10, state="disabled")
        self.play_btn.pack(side="left", padx=5)
        
        # Stop button
        self.stop_btn = Button(playback, text="Stop", command=self.stop, width=10, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Slider
        self.slider = Scale(playback, from_=0, to=100, orient=HORIZONTAL, command=self.seek, state="disabled")
        self.slider.pack(side="left", fill="x", expand=True, padx=5)
        
        # Time label
        self.time_label = Label(playback, text="0 / 0")
        self.time_label.pack(side="right", padx=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
    
    def browse_file(self):
        """Open file browser to select video"""
        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_video(file_path)
    
    def load_video(self, video_path):
        """Load a video file"""
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(str(video_path))
        
        if not self.cap.isOpened():
            self.file_label.config(text="Error: Could not open video", fg="red")
            return
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0
        self.playing = False
        
        # Update UI
        self.file_label.config(text=Path(video_path).name, fg="black")
        self.slider.config(from_=0, to=self.total_frames - 1, state="normal")
        self.slider.set(0)
        self.time_label.config(text=f"0 / {self.total_frames}")
        self.play_btn.config(state="normal", text="Play")
        self.stop_btn.config(state="normal")
        
        self.update_frame()
    
    def update_frame(self):
        """Update video frame"""
        if not self.cap or not self.cap.isOpened():
            self.root.after(100, self.update_frame)
            return
        
        if self.playing:
            ret, frame = self.cap.read()
            
            if ret:
                self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                self.slider.set(self.current_frame)
                self.time_label.config(text=f"{self.current_frame} / {self.total_frames}")
            else:
                self.playing = False
                self.play_btn.config(text="Play")
        
        # Display current frame
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.width, self.height))
                
                img = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(img)
                
                self.label.config(image=photo)
                self.label.image = photo
        
        if self.playing:
            delay = int(1000 / self.fps) if self.fps > 0 else 33
            self.root.after(delay, self.update_frame)
        else:
            self.root.after(100, self.update_frame)
    
    def toggle_play(self):
        """Play/Pause"""
        self.playing = not self.playing
        self.play_btn.config(text="Pause" if self.playing else "Play")
        if self.playing:
            self.update_frame()
    
    def stop(self):
        """Stop playback"""
        self.playing = False
        self.current_frame = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.slider.set(0)
        self.play_btn.config(text="Play")
    
    def seek(self, frame_num):
        """Seek to frame"""
        frame_num = int(float(frame_num))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        self.current_frame = frame_num
        self.time_label.config(text=f"{self.current_frame} / {self.total_frames}")
    
    def quit(self):
        """Close player"""
        self.playing = False
        if self.cap:
            self.cap.release()
        self.root.destroy()
    
    def play(self):
        """Start the player"""
        self.update_frame()
        self.root.mainloop()


# ============ USAGE EXAMPLE ============

if __name__ == "__main__":
    player = VideoPlayer(title="My Video Player", width=800, height=600)
    player.play()