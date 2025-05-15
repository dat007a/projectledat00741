import tkinter as tk
from tkinter import ttk
from png_maker import PSDCreatorApp
from offset_png import OffsetPngApp

class CombinedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Tools")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create frames for each tab
        self.png_maker_frame = ttk.Frame(self.notebook)
        self.offset_png_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.png_maker_frame, text="PNG Maker")
        self.notebook.add(self.offset_png_frame, text="Offset PNG")
        
        # Initialize the PNG Maker app in its tab
        self.png_maker_app = PSDCreatorApp(self.png_maker_frame)
        
        # Initialize the Offset PNG app in its tab
        self.offset_png_app = OffsetPngApp(self.offset_png_frame)
        
        # Center the window
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

def main():
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
