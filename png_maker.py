import os
import sys
import math
import gc
import re
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class PSDCreatorApp:
    def __init__(self, parent):
        self.parent = parent
        
        # Constants for document dimensions
        self.WIDTH_PX = 5669   # 1200cm at 120dpi
        self.HEIGHT_PX = 11335  # 2400cm at 120dpi
        
        # Margins and spacing (in cm)
        self.LEFT_MARGIN_CM = 1
        self.TOP_MARGIN_CM = 1
        self.RIGHT_MARGIN_CM = 1
        self.BOTTOM_MARGIN_CM = 1
        self.HORIZONTAL_SPACING_CM = 3
        self.STROKE_HORIZONTAL_SPACING_CM = 3
        self.VERTICAL_SPACING_CM = 2.5
        self.DPI = 120
        
        # Create the main frame
        main_frame = ttk.Frame(self.parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the top action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Action buttons
        ttk.Button(action_frame, text="Start Processing", command=self.start_processing).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Reset Fields", command=self.reset_fields).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for folder/file selection
        selection_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input folder selection
        ttk.Label(selection_frame, text="Input Folder (PNG Images):").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.input_folder_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.input_folder_var, width=50).grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(selection_frame, text="Browse...", command=self.browse_input_folder).grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)
        
        # Output folder selection
        ttk.Label(selection_frame, text="Output Folder:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.output_folder_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.output_folder_var, width=50).grid(column=0, row=3, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(selection_frame, text="Browse...", command=self.browse_output_folder).grid(column=1, row=3, sticky=tk.W, padx=5, pady=5)
        
        # Target width input
        ttk.Label(selection_frame, text="Target Image Width (cm):").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.target_width_var = tk.StringVar(value="10")
        ttk.Entry(selection_frame, textvariable=self.target_width_var, width=10).grid(column=0, row=5, sticky=tk.W, pady=5)
        
        # Stroke target width input
        ttk.Label(selection_frame, text="Stroke Target Image Width (cm):").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.stroke_target_width_var = tk.StringVar(value="10")
        ttk.Entry(selection_frame, textvariable=self.stroke_target_width_var, width=10).grid(column=0, row=7, sticky=tk.W, pady=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Advanced Settings", padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Horizontal spacing
        ttk.Label(settings_frame, text="Horizontal Spacing (cm):").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.h_spacing_var = tk.StringVar(value=str(self.HORIZONTAL_SPACING_CM))
        ttk.Entry(settings_frame, textvariable=self.h_spacing_var, width=10).grid(column=1, row=0, sticky=tk.W, pady=5, padx=5)
        
        # Stroke Horizontal spacing
        ttk.Label(settings_frame, text="Stroke Horizontal Spacing (cm):").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.stroke_h_spacing_var = tk.StringVar(value=str(self.HORIZONTAL_SPACING_CM))
        ttk.Entry(settings_frame, textvariable=self.stroke_h_spacing_var, width=10).grid(column=1, row=1, sticky=tk.W, pady=5, padx=5)
        
        # Vertical spacing
        ttk.Label(settings_frame, text="Vertical Spacing (cm):").grid(column=2, row=0, sticky=tk.W, pady=5, padx=(20, 0))
        self.v_spacing_var = tk.StringVar(value=str(self.VERTICAL_SPACING_CM))
        ttk.Entry(settings_frame, textvariable=self.v_spacing_var, width=10).grid(column=3, row=0, sticky=tk.W, pady=5, padx=5)
        
        # Margin settings
        ttk.Label(settings_frame, text="Left Margin (cm):").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.left_margin_var = tk.StringVar(value=str(self.LEFT_MARGIN_CM))
        ttk.Entry(settings_frame, textvariable=self.left_margin_var, width=10).grid(column=1, row=2, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(settings_frame, text="Right Margin (cm):").grid(column=2, row=1, sticky=tk.W, pady=5, padx=(20, 0))
        self.right_margin_var = tk.StringVar(value=str(self.RIGHT_MARGIN_CM))
        ttk.Entry(settings_frame, textvariable=self.right_margin_var, width=10).grid(column=3, row=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(settings_frame, text="Top Margin (cm):").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.top_margin_var = tk.StringVar(value=str(self.TOP_MARGIN_CM))
        ttk.Entry(settings_frame, textvariable=self.top_margin_var, width=10).grid(column=1, row=3, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(settings_frame, text="Bottom Margin (cm):").grid(column=2, row=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.bottom_margin_var = tk.StringVar(value=str(self.BOTTOM_MARGIN_CM))
        ttk.Entry(settings_frame, textvariable=self.bottom_margin_var, width=10).grid(column=3, row=2, sticky=tk.W, pady=5, padx=5)
        
        # Output format options
        ttk.Label(settings_frame, text="Output Format:").grid(column=0, row=4, sticky=tk.W, pady=10)
        self.format_var = tk.StringVar(value="PNG")
        ttk.Radiobutton(settings_frame, text="PNG", variable=self.format_var, value="PNG").grid(column=1, row=4, sticky=tk.W)
        ttk.Radiobutton(settings_frame, text="JPG", variable=self.format_var, value="JPG").grid(column=2, row=4, sticky=tk.W, padx=(10, 0))
        
        # Background option
        ttk.Label(settings_frame, text="Background:").grid(column=0, row=5, sticky=tk.W, pady=10)
        self.background_var = tk.StringVar(value="transparent")
        ttk.Radiobutton(settings_frame, text="Transparent", variable=self.background_var, value="transparent").grid(column=1, row=5, sticky=tk.W)
        ttk.Radiobutton(settings_frame, text="White", variable=self.background_var, value="white").grid(column=2, row=5, sticky=tk.W, padx=(10, 0))
        
        # Image repetition frame
        repeat_frame = ttk.LabelFrame(main_frame, text="Image Repetition", padding="10")
        repeat_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Repetition pattern information
        ttk.Label(repeat_frame, text="Images with pattern 'QT_xxx_filename.png' will be repeated xxx times.").grid(
            column=0, row=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Example
        ttk.Label(repeat_frame, text="Example: QT_3_mickey.png will be repeated 3 times").grid(
            column=0, row=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame, padding="10")
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Progress bar
        ttk.Label(status_frame, text="Progress:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5, columnspan=2)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).grid(column=0, row=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        selection_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
    
    def browse_input_folder(self):
        """Open file dialog to select input folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder_var.set(folder)
    
    def browse_output_folder(self):
        """Open file dialog to select output folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder_var.set(folder)
    
    def reset_fields(self):
        """Reset all input fields to default values."""
        self.input_folder_var.set("")
        self.output_folder_var.set("")
        self.target_width_var.set("10")
        self.stroke_target_width_var.set("10")
        self.h_spacing_var.set(str(self.HORIZONTAL_SPACING_CM))
        self.stroke_h_spacing_var.set(str(self.HORIZONTAL_SPACING_CM))
        self.v_spacing_var.set(str(self.VERTICAL_SPACING_CM))
        self.left_margin_var.set(str(self.LEFT_MARGIN_CM))
        self.right_margin_var.set(str(self.RIGHT_MARGIN_CM))
        self.top_margin_var.set(str(self.TOP_MARGIN_CM))
        self.bottom_margin_var.set(str(self.BOTTOM_MARGIN_CM))
        self.format_var.set("PNG")
        self.background_var.set("transparent")
        self.progress_var.set(0)
        self.status_var.set("Ready")
    
    def cm_to_pixels(self, cm):
        """Convert centimeters to pixels based on DPI."""
        return int(cm * self.DPI / 2.54)
    
    def add_stroke(self, image, stroke_width=1):
        """Add a black stroke around the image that follows the contour."""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get the alpha channel and create a mask for the visible parts
        alpha = image.getchannel('A')
        
        # Create a slightly larger image for the result
        new_size = (image.width + 2*stroke_width, image.height + 2*stroke_width)
        stroke_img = Image.new('RGBA', new_size, (0, 0, 0, 0))
        
        # For each direction (up, down, left, right and diagonals)
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        # Create a new alpha channel for the stroke
        stroke_alpha = Image.new('L', new_size, 0)
        
        # For each direction, shift the alpha channel and merge it
        for dx, dy in directions:
            shifted_alpha = Image.new('L', new_size, 0)
            shifted_alpha.paste(alpha, (stroke_width + dx, stroke_width + dy))
            stroke_data = list(stroke_alpha.getdata())
            shifted_data = list(shifted_alpha.getdata())
            merged_data = [max(a, b) for a, b in zip(stroke_data, shifted_data)]
            stroke_alpha.putdata(merged_data)
            shifted_alpha = None
        
        # Create black stroke image with the stroke alpha
        stroke_layer = Image.new('RGBA', new_size, (0, 0, 0, 255))
        stroke_layer.putalpha(stroke_alpha)
        
        # Position the original image in the center of the stroke image
        result = Image.new('RGBA', new_size, (0, 0, 0, 0))
        result.paste(image, (stroke_width, stroke_width), image)
        
        # Create a mask to prevent the stroke from covering the original image
        original_position_mask = Image.new('L', new_size, 0)
        original_position_mask.paste(alpha, (stroke_width, stroke_width))
        
        # Invert the mask
        inverted_mask_data = [255 - p for p in list(original_position_mask.getdata())]
        inverted_mask = Image.new('L', new_size, 0)
        inverted_mask.putdata(inverted_mask_data)
        
        # Apply the inverted mask to the stroke layer
        stroke_rgba = list(stroke_layer.convert('RGBA').getdata())
        inverted_mask_data = list(inverted_mask.getdata())
        
        new_stroke_data = []
        for i, (r, g, b, a) in enumerate(stroke_rgba):
            mask_value = inverted_mask_data[i]
            new_alpha = min(a, mask_value)
            new_stroke_data.append((r, g, b, new_alpha))
        
        stroke_layer.putdata(new_stroke_data)
        
        # Combine the stroke and the original image
        result = Image.alpha_composite(stroke_layer, result)
        
        # Clean up
        stroke_alpha = None
        stroke_layer = None
        original_position_mask = None
        inverted_mask = None
        
        return result
    
    def validate_inputs(self):
        """Validate user inputs before processing."""
        input_folder = self.input_folder_var.get()
        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror("Error", "Please select a valid input folder.")
            return False
        
        png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
        if not png_files:
            messagebox.showerror("Error", "Input folder does not contain any PNG files.")
            return False
        
        output_folder = self.output_folder_var.get()
        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Please select a valid output folder.")
            return False
        
        try:
            width_cm = float(self.target_width_var.get())
            if width_cm <= 0:
                raise ValueError("Width must be positive")
            stroke_width_cm = float(self.stroke_target_width_var.get())
            if stroke_width_cm <= 0:
                raise ValueError("Stroke width must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive numbers for the image widths.")
            return False
        
        try:
            h_spacing = float(self.h_spacing_var.get())
            stroke_h_spacing = float(self.stroke_h_spacing_var.get())
            v_spacing = float(self.v_spacing_var.get())
            left_margin = float(self.left_margin_var.get())
            right_margin = float(self.right_margin_var.get())
            top_margin = float(self.top_margin_var.get())
            bottom_margin = float(self.bottom_margin_var.get())
            
            if any(val < 0 for val in [h_spacing, stroke_h_spacing, v_spacing, left_margin, right_margin, top_margin, bottom_margin]):
                raise ValueError("Spacing and margin values must be non-negative")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for spacing and margin values.")
            return False
        
        if self.format_var.get() == "JPG" and self.background_var.get() == "transparent":
            messagebox.showwarning("Warning", "JPG format does not support transparency. Using white background instead.")
            self.background_var.set("white")
        
        return True
    
    def start_processing(self):
        """Start the image processing with auto width adjustment for ZKT_xxx_ prefixed files."""
        if not self.validate_inputs():
            return
        
        self.parent.config(cursor="wait")
        gc.collect()
        
        try:
            self.progress_var.set(0)
            self.status_var.set("Initializing processing...")
            self.parent.update_idletasks()
            
            # Get input parameters
            input_folder = self.input_folder_var.get()
            output_folder = self.output_folder_var.get()
            target_width_cm = float(self.target_width_var.get())
            stroke_target_width_cm = float(self.stroke_target_width_var.get())
            output_format = self.format_var.get()
            background_type = self.background_var.get()
            
            # Get spacing and margin values
            self.HORIZONTAL_SPACING_CM = float(self.h_spacing_var.get())
            self.STROKE_HORIZONTAL_SPACING_CM = float(self.stroke_h_spacing_var.get())
            self.VERTICAL_SPACING_CM = float(self.v_spacing_var.get())
            self.LEFT_MARGIN_CM = float(self.left_margin_var.get())
            self.RIGHT_MARGIN_CM = float(self.right_margin_var.get())
            self.TOP_MARGIN_CM = float(self.top_margin_var.get())
            self.BOTTOM_MARGIN_CM = float(self.bottom_margin_var.get())
            
            # Convert to pixels
            left_margin_px = self.cm_to_pixels(self.LEFT_MARGIN_CM)
            top_margin_px = self.cm_to_pixels(self.TOP_MARGIN_CM)
            right_margin_px = self.cm_to_pixels(self.RIGHT_MARGIN_CM)
            bottom_margin_px = self.cm_to_pixels(self.BOTTOM_MARGIN_CM)
            h_spacing_px = self.cm_to_pixels(self.HORIZONTAL_SPACING_CM)
            stroke_h_spacing_px = self.cm_to_pixels(self.STROKE_HORIZONTAL_SPACING_CM)
            v_spacing_px = self.cm_to_pixels(self.VERTICAL_SPACING_CM)
            
            # Get all PNG files
            png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
            
            # Calculate total images to process (including repeats)
            total_images = 0
            for file_name in png_files:
                match = re.match(r'^QT_(\d+)_', file_name)
                if match:
                    repeat_count = int(match.group(1))
                    total_images += max(1, repeat_count)  # Ensure at least 1
                else:
                    total_images += 1
            
            self.progress_var.set(5)
            self.status_var.set(f"Found {len(png_files)} PNG files to process ({total_images} total images)")
            self.parent.update_idletasks()
            
            # Create a blank canvas
            if background_type == "transparent" and output_format == "PNG":
                canvas = Image.new('RGBA', (self.WIDTH_PX, self.HEIGHT_PX), color=(0, 0, 0, 0))
            else:
                canvas = Image.new('RGB', (self.WIDTH_PX, self.HEIGHT_PX), color=(255, 255, 255))
            
            # Current position
            x = left_margin_px
            y = top_margin_px
            
            # Counters
            processed = 0
            canvas_count = 1
            
            # Progress increment per image
            image_progress_increment = 85 / total_images if total_images > 0 else 0
            current_progress = 5
            
            # Process each PNG
            for i, file_name in enumerate(png_files):
                try:
                    # Check for QT_xx_ prefix
                    match = re.match(r'^QT_(\d+)_', file_name)
                    repeat_count = int(match.group(1)) if match else 1
                    repeat_count = max(1, repeat_count)  # Ensure at least 1
                    
                    for repeat in range(repeat_count):
                        file_start_progress = current_progress
                        current_progress = file_start_progress + (image_progress_increment * 0.25)
                        self.progress_var.set(current_progress)
                        self.status_var.set(f"Loading {file_name} ({processed+1}/{total_images})")
                        self.parent.update_idletasks()
                        
                        # Load image
                        img_path = os.path.join(input_folder, file_name)
                        img = Image.open(img_path)
                        
                        current_progress = file_start_progress + (image_progress_increment * 0.5)
                        self.progress_var.set(current_progress)
                        self.status_var.set(f"Processing {file_name} ({processed+1}/{total_images})")
                        self.parent.update_idletasks()
                        
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        # Check if stroke image
                        is_stroke_image = file_name.lower().startswith("stroke_")
                        
                        # Trim transparent areas
                        alpha = img.getchannel('A')
                        bbox = alpha.getbbox()
                        if bbox:
                            img = img.crop(bbox)
                        
                        # Apply stroke if needed
                        if is_stroke_image:
                            self.status_var.set(f"Adding stroke to {file_name}")
                            self.parent.update_idletasks()
                            img = self.add_stroke(img, stroke_width=1)
                        
                        # Calculate aspect ratio
                        aspect_ratio = img.width / img.height
                        
                        current_progress = file_start_progress + (image_progress_increment * 0.75)
                        self.progress_var.set(current_progress)
                        self.parent.update_idletasks()
                        
                        # Check for ZKT_xxx_ prefix to auto-adjust width
                        zkt_match = re.match(r'^ZKT_(\d+)_', file_name)
                        if zkt_match:
                            # Extract width from ZKT_xxx_ prefix (in cm)
                            auto_width_cm = float(zkt_match.group(1))
                            if auto_width_cm <= 0:
                                raise ValueError(f"Invalid width {auto_width_cm}cm in filename {file_name}")
                            target_width_px = self.cm_to_pixels(auto_width_cm)
                            self.status_var.set(f"Auto-setting width to {auto_width_cm}cm for {file_name}")
                            self.parent.update_idletasks()
                        else:
                            # Use default width based on image type
                            target_width_px = self.cm_to_pixels(stroke_target_width_cm if is_stroke_image else target_width_cm)
                        
                        # Resize image
                        target_height = int(target_width_px / aspect_ratio)
                        img = img.resize((target_width_px, target_height), Image.LANCZOS)
                        
                        # Rotate 90 degrees clockwise
                        img = img.rotate(-90, expand=True)
                        
                        alpha = None
                        gc.collect()
                        
                        # Check for new row
                        if (x + img.width) > (self.WIDTH_PX - right_margin_px):
                            x = left_margin_px
                            current_width_px = target_width_px
                            y += current_width_px + v_spacing_px
                        
                        # Check for new canvas
                        if (y + img.height) > (self.HEIGHT_PX - bottom_margin_px):
                            current_progress = file_start_progress + (image_progress_increment * 0.85)
                            self.progress_var.set(current_progress)
                            self.status_var.set(f"Saving canvas {canvas_count}")
                            self.parent.update_idletasks()
                            
                            # Save current canvas
                            if output_format == "PNG":
                                canvas_path = os.path.join(output_folder, f"catalog_{canvas_count}.png")
                                if background_type == "transparent":
                                    canvas.save(canvas_path, format="PNG")
                                else:
                                    canvas.convert('RGB').save(canvas_path, format="PNG")
                            else:
                                canvas_path = os.path.join(output_folder, f"catalog_{canvas_count}.jpg")
                                canvas.convert('RGB').save(canvas_path, quality=95)
                            
                            self.status_var.set(f"Saved canvas {canvas_count} to {canvas_path}")
                            self.parent.update_idletasks()
                            
                            # Create new canvas
                            if background_type == "transparent" and output_format == "PNG":
                                canvas = Image.new('RGBA', (self.WIDTH_PX, self.HEIGHT_PX), color=(0, 0, 0, 0))
                            else:
                                canvas = Image.new('RGB', (self.WIDTH_PX, self.HEIGHT_PX), color=(255, 255, 255))
                            
                            canvas_count += 1
                            x = left_margin_px
                            y = top_margin_px
                        
                        # Paste the image
                        canvas.paste(img, (x, y), img if img.mode == 'RGBA' else None)
                        
                        # Update position
                        if is_stroke_image:
                            x += img.width + stroke_h_spacing_px
                        else:
                            x += img.width + h_spacing_px
                        processed += 1
                        
                        img = None
                        gc.collect()
                        
                        current_progress = file_start_progress + image_progress_increment
                        self.progress_var.set(current_progress)
                        self.parent.update_idletasks()
                        
                except Exception as e:
                    self.status_var.set(f"Error processing {file_name}: {e}")
                    self.parent.update_idletasks()
            
            # Save the last canvas
            if processed > 0:
                self.progress_var.set(95)
                self.status_var.set(f"Saving final canvas...")
                self.parent.update_idletasks()
                
                if output_format == "PNG":
                    canvas_path = os.path.join(output_folder, f"catalog_{canvas_count}.png")
                    if background_type == "transparent":
                        canvas.save(canvas_path, format="PNG", optimize=True)
                    else:
                        canvas.convert('RGB').save(canvas_path, format="PNG", optimize=True)
                else:
                    canvas_path = os.path.join(output_folder, f"catalog_{canvas_count}.jpg")
                    canvas.convert('RGB').save(canvas_path, quality=95, optimize=True)
                
                canvas = None
                gc.collect()
                
                self.status_var.set(f"Saved final canvas to {canvas_path}")
            
            self.progress_var.set(100)
            self.status_var.set(f"Completed! Created {canvas_count} image files.")
            self.parent.update_idletasks()
            
            messagebox.showinfo("Success", f"Processing complete! Created {canvas_count} image files.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
        
        finally:
            self.parent.config(cursor="")
