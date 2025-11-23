import tkinter as tk
from tkinter import Text, Button, Frame, filedialog, messagebox
from pathlib import Path

class TextEditor:
    """Simple text editor with open and save functionality"""
    
    def __init__(self, title="Text Editor", width=1000, height=600):
        self.title = title
        self.width = width
        self.height = height
        self.current_file = None
        
        # Create window
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Menu bar
        menu_frame = Frame(self.root)
        menu_frame.pack(fill="x", padx=5, pady=5)
        
        # Open button
        open_btn = Button(menu_frame, text="Open", command=self.open_file, width=10)
        open_btn.pack(side="left", padx=5)
        
        # Save button
        save_btn = Button(menu_frame, text="Save", command=self.save_file, width=10)
        save_btn.pack(side="left", padx=5)
        
        # Save As button
        save_as_btn = Button(menu_frame, text="Save As", command=self.save_as_file, width=10)
        save_as_btn.pack(side="left", padx=5)
        
        # New button
        new_btn = Button(menu_frame, text="New", command=self.new_file, width=10)
        new_btn.pack(side="left", padx=5)
        
        # File label
        self.file_label = tk.Label(menu_frame, text="No file", fg="gray")
        self.file_label.pack(side="left", padx=20, fill="x", expand=True)
        
        # Text area
        self.text_area = Text(self.root, wrap="word", font=("Courier", 11))
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status bar
        status_frame = Frame(self.root)
        status_frame.pack(fill="x", padx=5, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready", fg="green")
        self.status_label.pack(side="left")
        
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
    
    def open_file(self):
        """Open a file"""
        file_path = filedialog.askopenfilename(
            title="Open file",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.current_file = file_path
                self.file_label.config(text=Path(file_path).name, fg="black")
                self.status_label.config(text=f"Opened: {Path(file_path).name}", fg="green")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save current file"""
        if self.current_file is None:
            self.save_as_file()
            return
        
        try:
            content = self.text_area.get("1.0", tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_label.config(text=f"Saved: {Path(self.current_file).name}", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
    
    def save_as_file(self):
        """Save as new file"""
        file_path = filedialog.asksaveasfilename(
            title="Save file as",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.current_file = file_path
                self.file_label.config(text=Path(file_path).name, fg="black")
                self.status_label.config(text=f"Saved: {Path(file_path).name}", fg="green")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def new_file(self):
        """Create new file"""
        if self.text_area.get("1.0", tk.END).strip():
            response = messagebox.askyesnocancel("New File", "Save current file first?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.file_label.config(text="No file", fg="gray")
        self.status_label.config(text="New file", fg="green")
    
    def quit(self):
        """Close editor"""
        if self.text_area.get("1.0", tk.END).strip():
            response = messagebox.askyesnocancel("Quit", "Save before closing?")
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        self.root.destroy()
    
    def run(self):
        """Start the editor"""
        self.root.mainloop()


# ============ USAGE EXAMPLE ============

if __name__ == "__main__":
    editor = TextEditor(title="My Text Editor", width=1000, height=600)
    editor.run()
