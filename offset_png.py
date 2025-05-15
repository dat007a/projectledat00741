import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import numpy as np
import cv2
import os

class OffsetPngApp:
    def __init__(self, parent):
        self.parent = parent
        
        # Create the main container
        main_frame = ttk.Frame(self.parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and description
        intro = ttk.Label(main_frame, text="Tạo viền offset trắng cho nhiều ảnh PNG nền trong suốt")
        intro.pack(pady=10)
        
        # File selection area
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = ttk.Label(file_frame, text="Chưa chọn file nào")
        self.file_label.pack(pady=5)
        
        choose_btn = ttk.Button(file_frame, text="Chọn nhiều file ảnh", command=self.choose_files)
        choose_btn.pack(pady=5)
        
        # Offset settings
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        offset_frame = ttk.Frame(settings_frame)
        offset_frame.pack(pady=5)
        
        offset_label = ttk.Label(offset_frame, text="Độ rộng offset: ")
        offset_label.pack(side=tk.LEFT)
        
        self.offset_var = tk.IntVar(value=10)
        offset_entry = ttk.Spinbox(offset_frame, from_=1, to=100, textvariable=self.offset_var, width=5)
        offset_entry.pack(side=tk.LEFT)
        
        # Output directory settings
        output_frame = ttk.LabelFrame(main_frame, text="Output Directories", padding="10")
        output_frame.pack(fill=tk.X, pady=10)
        
        # PNG output directory
        png_dir_frame = ttk.Frame(output_frame)
        png_dir_frame.pack(fill=tk.X, pady=5)
        
        png_dir_label = ttk.Label(png_dir_frame, text="PNG Output Directory (optional): ")
        png_dir_label.pack(side=tk.LEFT)
        
        self.png_dir_var = tk.StringVar()
        png_dir_entry = ttk.Entry(png_dir_frame, textvariable=self.png_dir_var, width=30)
        png_dir_entry.pack(side=tk.LEFT, padx=5)
        
        png_dir_btn = ttk.Button(png_dir_frame, text="Browse...", command=self.browse_png_dir)
        png_dir_btn.pack(side=tk.LEFT)
        
        # JPG output directory
        jpg_dir_frame = ttk.Frame(output_frame)
        jpg_dir_frame.pack(fill=tk.X, pady=5)
        
        jpg_dir_label = ttk.Label(jpg_dir_frame, text="JPG Output Directory (optional): ")
        jpg_dir_label.pack(side=tk.LEFT)
        
        self.jpg_dir_var = tk.StringVar()
        jpg_dir_entry = ttk.Entry(jpg_dir_frame, textvariable=self.jpg_dir_var, width=30)
        jpg_dir_entry.pack(side=tk.LEFT, padx=5)
        
        jpg_dir_btn = ttk.Button(jpg_dir_frame, text="Browse...", command=self.browse_jpg_dir)
        jpg_dir_btn.pack(side=tk.LEFT)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=15)
        
        gen_btn = ttk.Button(action_frame, text="Generate", command=self.generate)
        gen_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = ttk.Button(action_frame, text="Reset", command=self.reset_fields)
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Status bar at the bottom
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Store selected files
        self.selected_files = []

    def choose_files(self):
        """Open file dialog to select multiple PNG files."""
        file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
        if file_paths:
            self.selected_files = list(file_paths)
            self.file_label.config(text=f"Đã chọn {len(file_paths)} file")
            self.status_var.set(f"Đã chọn {len(file_paths)} file")
    
    def browse_png_dir(self):
        """Open file dialog to select PNG output directory."""
        folder = filedialog.askdirectory()
        if folder:
            self.png_dir_var.set(folder)
    
    def browse_jpg_dir(self):
        """Open file dialog to select JPG output directory."""
        folder = filedialog.askdirectory()
        if folder:
            self.jpg_dir_var.set(folder)
    
    def reset_fields(self):
        """Reset all fields to default values."""
        self.selected_files = []
        self.file_label.config(text="Chưa chọn file nào")
        self.offset_var.set(10)
        self.png_dir_var.set("")
        self.jpg_dir_var.set("")
        self.status_var.set("Sẵn sàng")
    
    def add_white_offset(self, image_path, offset=10, outdir_png=None, outdir_jpg=None):
        """Add white offset to a transparent PNG image."""
        image = Image.open(image_path).convert("RGBA")
        image_np = np.array(image)
        alpha = image_np[:, :, 3]

        # Tạo mặt nạ nhị phân từ alpha
        _, binary_mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)

        # Làm mịn mask ban đầu
        binary_mask = cv2.GaussianBlur(binary_mask, (3, 3), 0)
        binary_mask = cv2.threshold(binary_mask, 127, 255, cv2.THRESH_BINARY)[1]

        # Dilation để tạo offset mượt (dùng kernel hình ellipse)
        kernel_size = offset * 2 + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        offset_mask = cv2.dilate(binary_mask, kernel, iterations=1)

        # Tạo ảnh border trắng
        h, w = alpha.shape
        white_border = np.zeros((h, w, 4), dtype=np.uint8)
        white_border[:, :, 0:3] = 255
        white_border[:, :, 3] = offset_mask
        border_img = Image.fromarray(white_border)

        # Gộp border vào ảnh gốc
        final_img = Image.alpha_composite(border_img, image)

        # --------------------------
        # LẤP ĐẦY VÙNG TRONG OFFSET
        # --------------------------
        final_np = np.array(final_img)
        filled = np.zeros((h + 2, w + 2), np.uint8)
        mask_for_fill = np.copy(offset_mask)
        cv2.floodFill(mask_for_fill, filled, (0, 0), 255)
        inside_mask = cv2.bitwise_not(mask_for_fill)

        # Làm mịn mask bên trong offset để loại bỏ viền đen
        inside_mask = cv2.GaussianBlur(inside_mask, (5, 5), 0)
        inside_mask = cv2.threshold(inside_mask, 127, 255, cv2.THRESH_BINARY)[1]

        # Tô trắng hoàn toàn vùng bên trong offset (RGB + Alpha)
        for c in range(3):
            final_np[:, :, c] = np.where(inside_mask == 255, 255, final_np[:, :, c])
        final_np[:, :, 3] = np.where(inside_mask == 255, 255, final_np[:, :, 3])

        final_img = Image.fromarray(final_np)

        # Tạo thư mục đầu ra nếu chưa có
        base_dir = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        if outdir_png is None:
            outdir_png = os.path.join(base_dir, "output_png")
        if outdir_jpg is None:
            outdir_jpg = os.path.join(base_dir, "output_jpg")

        os.makedirs(outdir_png, exist_ok=True)
        os.makedirs(outdir_jpg, exist_ok=True)

        # Lưu file PNG trong suốt
        output_path_png = os.path.join(outdir_png, f"{base_name}_offset.png")
        final_img.save(output_path_png)

        # Tạo file JPG với nền xám và ảnh offset thu nhỏ, căn giữa
        background = Image.new("RGB", final_img.size, "#a6a6a6")
        scale_img = final_img.resize((int(w * 0.7), int(h * 0.7)), resample=Image.LANCZOS)
        paste_x = (w - scale_img.size[0]) // 2
        paste_y = (h - scale_img.size[1]) // 2
        final_rgb = scale_img.convert("RGB")
        background.paste(final_rgb, (paste_x, paste_y), scale_img.split()[3])
        output_path_jpg = os.path.join(outdir_jpg, f"{base_name}_offset.jpg")
        background.save(output_path_jpg, quality=95)

        return output_path_png, output_path_jpg
    
    def generate(self):
        """Process all selected files and add white offset to them."""
        if not self.selected_files:
            messagebox.showwarning("Chưa chọn ảnh", "Vui lòng chọn ít nhất một file PNG.")
            return
        
        try:
            # Setup progress window
            progress_window = tk.Toplevel(self.parent)
            progress_window.title("Đang xử lý")
            progress_window.geometry("300x100")
            progress_window.transient(self.parent)
            progress_window.grab_set()
            
            # Center the progress window relative to main window
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (300 // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (100 // 2)
            progress_window.geometry(f"+{x}+{y}")
            
            # Make it non-resizable
            progress_window.resizable(False, False)
            
            # Progress label
            progress_label = tk.Label(progress_window, text="Đang xử lý ảnh...")
            progress_label.pack(pady=(10, 0))
            
            # Progress percentage label
            percentage_label = tk.Label(progress_window, text="0%")
            percentage_label.pack(pady=(0, 5))
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_window, orient="horizontal", mode="determinate", length=250)
            progress_bar.pack(pady=5, padx=20)
            
            total_files = len(self.selected_files)
            offset_value = self.offset_var.get()
            outdir_png = self.png_dir_var.get() if self.png_dir_var.get() else None
            outdir_jpg = self.jpg_dir_var.get() if self.jpg_dir_var.get() else None
            
            # Update function to process files one by one with progress update
            def process_files(index=0):
                if index < total_files:
                    file_path = self.selected_files[index]
                    file_name = os.path.basename(file_path)
                    
                    # Update labels
                    progress_label.config(text=f"Đang xử lý: {file_name}")
                    percentage = int((index / total_files) * 100)
                    percentage_label.config(text=f"{percentage}%")
                    progress_bar["value"] = percentage
                    
                    try:
                        # Process current file
                        self.add_white_offset(file_path, offset=offset_value, outdir_png=outdir_png, outdir_jpg=outdir_jpg)
                        
                        # Schedule next file processing
                        self.parent.after(50, lambda: process_files(index + 1))
                    except Exception as e:
                        progress_window.destroy()
                        messagebox.showerror("Lỗi", f"Lỗi khi xử lý {file_name}: {str(e)}")
                else:
                    # All files processed
                    progress_bar["value"] = 100
                    percentage_label.config(text="100%")
                    progress_label.config(text="Hoàn thành!")
                    
                    # Close progress window after delay
                    self.parent.after(1000, progress_window.destroy)
                    messagebox.showinfo("Thành công", f"Đã xử lý {total_files} ảnh.")
            
            # Start processing
            self.parent.after(100, process_files)
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
