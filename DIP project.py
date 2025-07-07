import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.img = None
        self.img_path = None
        self.processed_img = None
        self.dark_mode = False
        # Use maximized window instead of fullscreen
        self.root.state('zoomed')
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize all UI components"""
        self.root.title("Advanced Image Processor")
        
        # Configure styles
        self.style = ttk.Style()
        
        # Improved light theme colors
        self.bg_color = "#e6f2ff"  # Light blue background
        self.button_color = "#1a73e8"  # Google blue
        self.button_active = "#0d5bb9"
        self.text_color = "#202124"  # Dark gray
        
        # Improved dark theme colors
        self.dark_bg = "#202124"  # Dark gray
        self.dark_button = "#1a73e8"  # Same blue but brighter
        self.dark_button_active = "#0d5bb9"
        self.dark_text = "#e8eaed"  # Light gray
        
        # Configure frame styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Dark.TFrame", background=self.dark_bg)
        
        # Configure button styles with rounded corners and hover effects
        self.style.configure("TButton",
            font=('Helvetica', 12, 'bold'),
            padding=10,
            relief="raised",
            borderwidth=0,
            foreground="#0d47a1",  # Dark blue text
            background=self.button_color,
            bordercolor=self.button_color,
            focuscolor=self.button_color,
            lightcolor=self.button_color,
            darkcolor=self.button_color,
            borderradius=25,  # More rounded corners
        )
        
        # Enhanced rounded button style
        self.style.configure("Rounded.TButton",
            borderwidth=0,
            relief="raised",
            padding=10,
            font=('Helvetica', 12, 'bold'),
            foreground="#0d47a1",  # Dark blue text
            background=self.button_color,
            bordercolor=self.button_color,
            focuscolor=self.button_color,
            lightcolor=self.button_color,
            darkcolor=self.button_color,
            borderradius=50,  # Fully pill-shaped
            highlightthickness=0
        )
        
        # Hover effects with pop-up animation
        self.style.map("Rounded.TButton",
            background=[
                ('active', self.button_active),
                ('!active', self.button_color)
            ],
            relief=[
                ('pressed', 'sunken'),
                ('!pressed', 'raised')
            ],
            foreground=[
                ('active', "#1565c0"),  # Brighter blue when active
                ('!active', "#0d47a1")  # Dark blue when inactive
            ],
            padding=[
                ('active', (10, 10, 12, 12)),  # Slightly larger when hovered
                ('!active', (10, 10, 10, 10))
            ]
        )
        
        self.root.configure(bg=self.bg_color)
        
        # Main frames
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.image_frame = ttk.Frame(self.root, padding="10")
        self.image_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(
            self.control_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            style="Rounded.TButton"
        )
        self.theme_btn.pack(pady=10, fill=tk.X)
        
        # Upload button
        self.upload_btn = ttk.Button(
            self.control_frame, 
            text="📁 Upload Image", 
            command=self.upload_image,
            style="Rounded.TButton"
        )
        self.upload_btn.pack(pady=10, fill=tk.X)

    def upload_image(self):
        """Handle image upload"""
        self.img_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if self.img_path:
            try:
                self.img = Image.open(self.img_path)
                self.display_images()
                self.setup_processing_controls()
            except Exception as e:
                self.show_error(f"Failed to load image: {str(e)}")
    
    def display_images(self):
        """Display original and processed images with perfect fitting"""
        if not hasattr(self, 'original_canvas'):
            self.setup_canvases()
            
        # Calculate exact fitting while maintaining aspect ratio
        img_width, img_height = self.img.size
        canvas_width = 500
        canvas_height = 500
        
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # High-quality resizing
        display_img = self.img.copy()
        display_img = display_img.resize((new_width, new_height), Image.LANCZOS)
        self.original_img_tk = ImageTk.PhotoImage(display_img)
        
        # Perfectly center the image
        x_pos = (canvas_width - new_width) // 2
        y_pos = (canvas_height - new_height) // 2
        
        self.original_canvas.delete("all")
        self.original_canvas.create_image(
            x_pos + new_width//2, y_pos + new_height//2,
            anchor=tk.CENTER,
            image=self.original_img_tk
        )

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Set dark theme colors
            self.root.configure(bg=self.dark_bg)
            self.control_frame.configure(style="Dark.TFrame")
            self.image_frame.configure(style="Dark.TFrame")
            self.theme_btn.configure(text="☀️ Light Mode")
            
            # Update button styles
            self.style.configure("Rounded.TButton",
                background=self.dark_button,
                foreground=self.dark_text
            )
            self.style.map("Rounded.TButton",
                background=[('active', self.dark_button_active)]
            )
        else:
            # Set light theme colors
            self.root.configure(bg=self.bg_color)
            self.control_frame.configure(style="TFrame")
            self.image_frame.configure(style="TFrame")
            self.theme_btn.configure(text="🌙 Dark Mode")
            
            # Update button styles
            self.style.configure("Rounded.TButton",
                background=self.button_color,
                foreground="white"
            )
            self.style.map("Rounded.TButton",
                background=[('active', self.button_active)]
            )

    def setup_processing_controls(self):
        """Setup processing buttons with undo/redo functionality"""
        if not hasattr(self, 'processing_frame'):
            self.processing_frame = ttk.Frame(self.control_frame)
            self.processing_frame.pack(pady=20, fill=tk.X)
            
            # History stack for undo/redo
            self.history = []
            self.history_index = -1
            
            ttk.Label(self.processing_frame, text="Image Filters", 
                     font=('Helvetica', 12, 'bold')).pack()
            
            buttons = [
                ("🔲 Negative", self.apply_negative),
                ("🌀 Smoothing", self.apply_smoothing),
                ("🔍 Edge Enhance", self.apply_edge_enhance),
                ("💾 Save Image", self.save_image),
                ("↩️ Undo", self.undo_action),
                ("↪️ Redo", self.redo_action)
            ]
            
            for text, command in buttons:
                btn = ttk.Button(
                    self.processing_frame,
                    text=text,
                    command=command,
                    style="Rounded.TButton"
                )
                btn.pack(pady=5, fill=tk.X)

    def apply_filter(self, filter_func):
        """Common filter application with loading animation"""
        if self.img:
            try:
                self.arrow_progress = 0
                self.loading_arrow.pack(pady=10)
                self.processed_canvas.delete("all")
                self.processed_img = filter_func()
                self.root.after(50, self.animate_loading)
                self.add_to_history()
            except Exception as e:
                self.loading_arrow.pack_forget()
                self.show_error(f"Filter error: {str(e)}")

    def animate_loading(self):
        """Animate loading arrow from left to right with theme colors"""
        arrow_color = "#1565C0" if not self.dark_mode else "#90CAF9"  # Dark blue / light blue
        if self.arrow_progress < 100:
            self.arrow_progress += 5
            self.loading_arrow.delete("all")
            
            # Draw arrow outline
            self.loading_arrow.create_polygon(
                10, 25, 90, 25, 90, 15, 100, 25,
                90, 35, 90, 25, fill="", outline=arrow_color, width=2
            )
            
            # Fill progress
            fill_width = 80 * (self.arrow_progress/100)
            self.loading_arrow.create_rectangle(
                10, 20, 10 + fill_width, 30,
                fill=arrow_color, outline=""
            )
            
            self.root.after(30, self.animate_loading)  # Faster animation
        else:
            self.loading_arrow.pack_forget()
            self.update_processed_display()

    def apply_negative(self):
        """Apply negative filter"""
        self.apply_filter(lambda: self.img.convert('RGB').point(lambda p: 255 - p))

    def apply_smoothing(self):
        """Apply smoothing filter"""
        self.apply_filter(lambda: self.img.filter(ImageFilter.GaussianBlur(2)))

    def apply_edge_enhance(self):
        """Apply edge enhancement"""
        self.apply_filter(lambda: self.img.filter(ImageFilter.EDGE_ENHANCE))

    def save_image(self):
        """Save processed image"""
        if self.processed_img:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
            )
            if save_path:
                try:
                    self.processed_img.save(save_path)
                except Exception as e:
                    self.show_error(f"Failed to save image: {str(e)}")

    def setup_canvases(self):
        """Initialize image display canvases"""
        # Create container frame for both canvases
        canvas_container = ttk.Frame(self.image_frame)
        canvas_container.pack(expand=True, fill=tk.BOTH, pady=20)
        
        # Original image canvas
        original_frame = ttk.Frame(canvas_container)
        original_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=20)
        
        ttk.Label(original_frame, text="Original Image", 
                 font=('Helvetica', 12, 'bold')).pack()
        
        self.original_canvas = tk.Canvas(
            original_frame,
            width=500,
            height=500,
            bg="white",
            highlightthickness=3,
            highlightbackground="#8B4513"  # Brown border
        )
        self.original_canvas.pack(pady=10)
        
        # Processed image canvas
        processed_frame = ttk.Frame(canvas_container)
        processed_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=20)
        
        ttk.Label(processed_frame, text="Processed Image", 
                 font=('Helvetica', 12, 'bold')).pack()
        
        self.processed_canvas = tk.Canvas(
            processed_frame,
            width=500,
            height=500,
            bg="white",
            highlightthickness=3,
            highlightbackground="#8B4513"  # Brown border
        )
        
        # Loading arrow at bottom
        arrow_frame = ttk.Frame(canvas_container)
        arrow_frame.pack(pady=80)
        self.loading_arrow = tk.Canvas(arrow_frame, width=100, height=50,
                                     bg=self.bg_color, highlightthickness=0)
        self.loading_arrow.pack()
        self.arrow_progress = 0
        self.processed_canvas.pack(pady=10)

    def add_to_history(self):
        """Add current state to history stack (max 5 steps)"""
        if self.processed_img:
            # Only keep history up to current index
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.processed_img.copy())
            # Limit history to 5 steps
            if len(self.history) > 5:
                self.history.pop(0)
            self.history_index = len(self.history) - 1

    def undo_action(self):
        """Undo the last action (up to 5 steps)"""
        if self.history_index > 0:
            self.history_index -= 1
            self.processed_img = self.history[self.history_index]
            self.update_processed_display()
            # Show current position in history
            self.show_status(f"Undo: step {len(self.history)-self.history_index} of {len(self.history)}")

    def redo_action(self):
        """Redo the last undone action (up to 5 steps)"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.processed_img = self.history[self.history_index]
            self.update_processed_display()
            # Show current position in history
            self.show_status(f"Redo: step {self.history_index+1} of {len(self.history)}")

    def show_status(self, message):
        """Show status message temporarily"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            self.root.after(2000, lambda: self.status_label.config(text=""))

    def update_processed_display(self):
        """Update the processed image display with proper fitting"""
        if self.processed_img:
            # Calculate aspect-ratio preserving dimensions
            img_width, img_height = self.processed_img.size
            canvas_width = 500
            canvas_height = 500
            
            ratio = min(canvas_width/img_width, canvas_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # Resize image while maintaining aspect ratio
            display_img = self.processed_img.copy()
            display_img = display_img.resize((new_width, new_height), Image.LANCZOS)
            self.processed_img_tk = ImageTk.PhotoImage(display_img)
            
            # Center the image on canvas
            self.processed_canvas.delete("all")
            self.processed_canvas.create_image(
                canvas_width//2, canvas_height//2,
                anchor=tk.CENTER,
                image=self.processed_img_tk
            )

    def show_error(self, message):
        """Display error message"""
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        ttk.Label(
            error_window,
            text=message,
            foreground="red",
            wraplength=300
        ).pack(padx=20, pady=20)
        ttk.Button(
            error_window,
            text="OK",
            command=error_window.destroy
        ).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
