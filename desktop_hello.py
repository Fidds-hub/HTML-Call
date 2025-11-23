from pathlib import Path

def create_hello_file():
    desktop = Path.home() / "Desktop"
    file_path = desktop / "hello-world.txt"
    file_path.write_text("Github Python Test Success.")
    print(f"File Created At {file_path}")
    
create_hello_file()