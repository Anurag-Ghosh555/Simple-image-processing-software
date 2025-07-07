import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import io
import time

class ImageProcessor:
    def __init__(self):
        # App setup and configuration
        st.set_page_config(
            page_title="Advanced Image Processor",
            page_icon="🖼️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state for storing image data
        if 'img' not in st.session_state:
            st.session_state.img = None
        if 'processed_img' not in st.session_state:
            st.session_state.processed_img = None
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False
            
        # Setup the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI structure"""
        # Apply custom styling
        self.apply_custom_css()
        
        # App header
        st.title("🖼️ Advanced Image Processor")
        
        # Theme toggle in sidebar
        with st.sidebar:
            st.sidebar.title("Controls")
            
            # Theme toggle with improved UI
            theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
            theme_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
            if st.button(f"{theme_icon} {theme_text}", key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
                
            # Image upload
            st.header("Upload Image")
            uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                self.load_image(uploaded_file)
            
            # Only show processing controls if an image is loaded
            if st.session_state.img is not None:
                self.setup_processing_controls()
        
        # Main area for displaying images
        if st.session_state.img is not None:
            self.display_images()
        else:
            # Show welcome message when no image is loaded
            self.display_welcome_message()
    
    def apply_custom_css(self):
        """Apply custom CSS based on selected theme"""
        # Define colors based on theme - improved contrast
        if st.session_state.dark_mode:
            bg_color = "#121212"  # Darker background
            text_color = "#ffffff"  # White text for better contrast
            accent_color = "#4285f4"  # Brighter blue
            card_bg = "#1e1e1e"  # Darker card background
            button_text = "#ffffff"  # White text for buttons
            shadow_color = "rgba(0, 0, 0, 0.3)"
        else:
            bg_color = "#f0f8ff"  # Light blue background
            text_color = "#212121"  # Very dark gray for better contrast
            accent_color = "#1a73e8"  # Google blue
            card_bg = "#ffffff"  # White
            button_text = "#ffffff"  # White text for buttons
            shadow_color = "rgba(0, 0, 0, 0.1)"
            
        # Apply enhanced custom CSS
        st.markdown(f"""
        <style>
            /* Hide deprecation warnings */
            .stDeployButton, .element-container div[data-testid="stDecoration"] {{
                display: none !important;
            }}
            
            .main .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
                background-color: {bg_color};
                border-radius: 10px;
            }}
            
            .stApp {{
                background-color: {bg_color};
            }}
            
            h1, h2, h3, p {{
                color: {text_color} !important;
            }}
            
            .stMarkdown div p {{
                color: {text_color} !important;
            }}
            
            label, .st-eb {{
                color: {text_color} !important;
            }}
            
            .stButton>button {{
                border-radius: 20px;
                padding: 10px 24px;
                background-color: {accent_color};
                color: {button_text};
                font-weight: bold;
                border: none;
                transition: all 0.3s ease;
                width: 100%;
                margin-bottom: 0.5rem;
                box-shadow: 0 2px 5px {shadow_color};
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            
            .stButton>button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px {shadow_color};
                filter: brightness(1.05);
            }}
            
            .welcome-message {{
                background-color: {card_bg};
                border-radius: 15px;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 8px 16px {shadow_color};
                margin-top: 2rem;
                border: 1px solid {bg_color};
            }}
            
            .image-container {{
                background-color: {card_bg};
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 8px 16px {shadow_color};
                text-align: center;
                border: 1px solid {accent_color}20;
            }}
            
            .status-message {{
                padding: 10px;
                border-radius: 10px;
                background-color: {accent_color};
                color: white;
                text-align: center;
                margin: 10px 0;
                font-weight: bold;
                box-shadow: 0 4px 8px {shadow_color};
            }}
            
            .stProgress > div > div {{
                background-color: {accent_color};
            }}
            
            div[data-testid="stFileUploader"] {{
                border-radius: 10px;
                padding: 10px;
                border: 2px dashed {accent_color}60;
            }}
            
            div[data-testid="stSidebar"] {{
                background-color: {card_bg};
                padding: 2rem 1rem;
                border-radius: 0 10px 10px 0;
                box-shadow: 5px 0 15px {shadow_color};
            }}
            
            .stSidebar > div:first-child {{
                background-color: {card_bg} !important;
            }}
            
            div[data-testid="stSidebar"] h1, div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3, div[data-testid="stSidebar"] label {{
                color: {text_color} !important;
            }}
            
            .stImage {{
                border-radius: 10px;
                box-shadow: 0 4px 8px {shadow_color};
            }}
            
            .stDownloadButton>button {{
                border-radius: 20px;
                padding: 10px 24px;
                background-color: #00c853;  /* Green for save button */
                color: white;
                font-weight: bold;
                border: none;
                transition: all 0.3s ease;
                width: 100%;
                margin-top: 0.5rem;
                box-shadow: 0 2px 5px {shadow_color};
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            
            .stDownloadButton>button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px {shadow_color};
                filter: brightness(1.05);
            }}
            
            .section-divider {{
                border-top: 1px solid {accent_color}40;
                margin: 1.5rem 0;
                opacity: 0.5;
            }}
            
            .stAlert {{
                background-color: {card_bg};
                color: {text_color};
                border-radius: 10px;
                border-left-color: {accent_color};
            }}
            
            .filter-button {{
                margin-bottom: 0.5rem;
            }}
            
            .reset-button {{
                background-color: #f44336 !important;
                color: white !important;
                font-weight: bold !important;
                margin-top: 1rem !important;
            }}
            
            .reset-button:hover {{
                background-color: #d32f2f !important;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    def display_welcome_message(self):
        """Enhanced welcome message"""
        st.markdown("""
        <div class="welcome-message">
            <h2>✨ Welcome to the Advanced Image Processor ✨</h2>
            <p>Transform your images with just a few clicks!</p>
            <p>Upload an image using the sidebar to get started.</p>
            <br>
            <p><b>Team Details:</b></p>
            <p>Anurag Ghosh(RA2311003010607)</p>
            <p>Rishabh Katiyar(RA2311003010579)</p>
            <p>Riya Saxena(RA2311003010580)</p>
            <p>Aishani Mishra(RA2311003010546)</p>
        </div>
        """, unsafe_allow_html=True)
    
    def load_image(self, uploaded_file):
        """Load and store the uploaded image"""
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.session_state.img = img
            st.session_state.processed_img = img.copy()  # Initialize processed with a copy of original
            
            st.success("✅ Image loaded successfully!")
        except Exception as e:
            st.error(f"❌ Failed to load image: {str(e)}")
    
    def display_images(self):
        """Display original and processed images side by side"""
        cols = st.columns(2)
        
        # Original image
        with cols[0]:
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.subheader("Original Image")
            st.image(
                st.session_state.img,
                caption="Original Image",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Processed image
        with cols[1]:
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.subheader("Processed Image")
            if st.session_state.processed_img is not None:
                st.image(
                    st.session_state.processed_img,
                    caption="Processed Image",
                    use_container_width=True
                )
                
                # Add download button directly under the processed image for convenience
                buffer = io.BytesIO()
                st.session_state.processed_img.save(buffer, format="PNG")
                st.download_button(
                    label="💾 Download This Image",
                    data=buffer.getvalue(),
                    file_name="processed_image.png",
                    mime="image/png"
                )
            else:
                st.info("Apply a filter to see the processed image here")
            st.markdown('</div>', unsafe_allow_html=True)
    
    def setup_processing_controls(self):
        """Set up buttons for image processing with improved UI"""
        st.sidebar.header("Image Filters")
        
        # Define filter functions in session state for button clicks
        if 'negative_filter' not in st.session_state:
            st.session_state.negative_filter = False
        if 'smoothing_filter' not in st.session_state:
            st.session_state.smoothing_filter = False
        if 'edge_filter' not in st.session_state:
            st.session_state.edge_filter = False
            
        # Direct filter buttons
        if st.sidebar.button("🔄 Negative", key="negative_btn"):
            st.session_state.negative_filter = True
            
        if st.sidebar.button("🌊 Smoothing", key="smoothing_btn"):
            st.session_state.smoothing_filter = True
            
        if st.sidebar.button("✴️ Edge Enhance", key="edge_btn"):
            st.session_state.edge_filter = True
        
        # Process filter selections
        if st.session_state.negative_filter:
            self.process_with_progress(self.apply_negative)
            st.session_state.negative_filter = False
            
        if st.session_state.smoothing_filter:
            self.process_with_progress(self.apply_smoothing)
            st.session_state.smoothing_filter = False
            
        if st.session_state.edge_filter:
            self.process_with_progress(self.apply_edge_enhance)
            st.session_state.edge_filter = False
        
        # Add new adjustment controls
        st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.sidebar.header("Image Adjustments")
        
        # Store slider values in session state
        if 'brightness_value' not in st.session_state:
            st.session_state.brightness_value = 1.0
        if 'contrast_value' not in st.session_state:
            st.session_state.contrast_value = 1.0
        if 'apply_brightness' not in st.session_state:
            st.session_state.apply_brightness = False
        if 'apply_contrast' not in st.session_state:
            st.session_state.apply_contrast = False
            
        # Brightness control
        st.session_state.brightness_value = st.sidebar.slider(
            "✨ Brightness", 
            0.0, 2.0, 
            st.session_state.brightness_value, 
            0.1
        )
        
        if st.sidebar.button("Apply Brightness", key="brightness_btn"):
            st.session_state.apply_brightness = True
            
        # Process brightness adjustment
        if st.session_state.apply_brightness:
            self.process_with_progress(lambda: self.adjust_brightness(st.session_state.brightness_value))
            st.session_state.apply_brightness = False
        
        # Contrast control
        st.session_state.contrast_value = st.sidebar.slider(
            "🔆 Contrast", 
            0.0, 2.0, 
            st.session_state.contrast_value, 
            0.1
        )
        
        if st.sidebar.button("Apply Contrast", key="contrast_btn"):
            st.session_state.apply_contrast = True
            
        # Process contrast adjustment
        if st.session_state.apply_contrast:
            self.process_with_progress(lambda: self.adjust_contrast(st.session_state.contrast_value))
            st.session_state.apply_contrast = False
        
        # Reset Image functionality
        st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.sidebar.header("Reset Image")
        
        if 'reset_image' not in st.session_state:
            st.session_state.reset_image = False
            
        # Prominent reset button with custom styling
        if st.sidebar.button("🔄 Reset to Original", key="reset_btn", help="Reset the image to its original state"):
            st.session_state.reset_image = True
            
        if st.session_state.reset_image:
            if st.session_state.img is not None:
                st.session_state.processed_img = st.session_state.img.copy()
                st.success("✅ Image has been reset to original!")
                st.session_state.reset_image = False
        
        # Save button in sidebar
        st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.sidebar.header("Save Image")
        if st.session_state.processed_img is not None:
            buffer = io.BytesIO()
            st.session_state.processed_img.save(buffer, format="PNG")
            st.sidebar.download_button(
                label="💾 Save Processed Image",
                data=buffer.getvalue(),
                file_name="processed_image.png",
                mime="image/png",
                key="save_sidebar"
            )
    
    def process_with_progress(self, filter_func):
        """Process image with progress bar"""
        if st.session_state.img is not None:
            try:
                # Show progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate processing time for visual feedback
                for percent_complete in range(0, 101, 10):
                    time.sleep(0.05)  # Short delay for animation
                    progress_bar.progress(percent_complete)
                    status_text.markdown(f'<div class="status-message">Processing: {percent_complete}%</div>', unsafe_allow_html=True)
                
                # Apply the actual filter
                st.session_state.processed_img = filter_func()
                
                # Complete progress
                progress_bar.progress(100)
                status_text.markdown('<div class="status-message">✅ Processing complete!</div>', unsafe_allow_html=True)
                time.sleep(0.5)  # Show completion message briefly
                status_text.empty()
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"❌ Filter error: {str(e)}")
    
    def apply_negative(self):
        """Apply negative filter to the image"""
        if st.session_state.processed_img:
            return st.session_state.processed_img.point(lambda p: 255 - p)
        return st.session_state.img.point(lambda p: 255 - p)
    
    def apply_smoothing(self):
        """Apply smoothing filter to the image"""
        if st.session_state.processed_img:
            return st.session_state.processed_img.filter(ImageFilter.GaussianBlur(2))
        return st.session_state.img.filter(ImageFilter.GaussianBlur(2))
    
    def apply_edge_enhance(self):
        """Apply edge enhancement to the image"""
        if st.session_state.processed_img:
            return st.session_state.processed_img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        return st.session_state.img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    
    def adjust_brightness(self, factor):
        """Adjust image brightness"""
        if st.session_state.processed_img:
            enhancer = ImageEnhance.Brightness(st.session_state.processed_img)
            return enhancer.enhance(factor)
        enhancer = ImageEnhance.Brightness(st.session_state.img)
        return enhancer.enhance(factor)
    
    def adjust_contrast(self, factor):
        """Adjust image contrast"""
        if st.session_state.processed_img:
            enhancer = ImageEnhance.Contrast(st.session_state.processed_img)
            return enhancer.enhance(factor)
        enhancer = ImageEnhance.Contrast(st.session_state.img)
        return enhancer.enhance(factor)

# Run the app
if __name__ == "__main__":
    app = ImageProcessor()