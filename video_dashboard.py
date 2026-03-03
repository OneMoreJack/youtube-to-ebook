"""
YouTube Video to Ebook Dashboard
A beautiful web interface to generate ebooks from YouTube videos.
"""

import streamlit as st
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# Inject local module path for streamlit_image_select
sys.path.insert(0, str(Path(__file__).parent / "vendor"))

from video_to_ebook import extract_video_id, generate_ebook, fetch_all_transcripts, generate_all_articles
from create_ebook import create_epub, DEFAULT_OUTPUT_DIR
from cover_generator import generate_cover_bytes
from streamlit_image_select import image_select


# Paths
PROJECT_DIR = Path(__file__).parent
EBOOKS_DIR = PROJECT_DIR / "ebooks"

# Create ebooks directory if it doesn't exist
EBOOKS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Video to Ebook",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - Editorial Magazine Aesthetic
# (Matching dashboard.py style)
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&family=Sora:wght@300;400;500;600&display=swap');

    :root {
        --bg-primary: #0d0d0d;
        --bg-secondary: #161616;
        --bg-tertiary: #1a1a1a;
        --bg-card: #1e1e1e;
        --accent-gold: #d4a855;
        --accent-gold-dim: #a68542;
        --accent-gold-glow: rgba(212, 168, 85, 0.15);
        --text-primary: #e8e4dd;
        --text-secondary: #9a958c;
        --text-dim: #5c5850;
        --border-subtle: #2a2a2a;
        --success: #5cb85c;
        --error: #c9302c;
    }

    /* Main container */
    .stApp {
        background: var(--bg-primary);
        background-image:
            radial-gradient(ellipse at top right, rgba(212, 168, 85, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at bottom left, rgba(212, 168, 85, 0.02) 0%, transparent 50%);
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-subtle);
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    h1 {
        font-size: 2.75rem !important;
        letter-spacing: -0.02em;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 1rem;
        margin-bottom: 2rem !important;
    }

    h2 {
        font-size: 1.75rem !important;
        color: var(--accent-gold) !important;
        margin-top: 2rem !important;
    }

    h3 {
        font-size: 1.25rem !important;
        font-weight: 400 !important;
        font-style: italic;
    }

    p, li, span, div {
        font-family: 'Sora', sans-serif;
        color: var(--text-primary);
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        font-family: 'Sora', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.03em;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        border: 1px solid var(--border-subtle) !important;
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--accent-gold-dim) !important;
        background: var(--accent-gold-glow) !important;
        color: var(--accent-gold) !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-dim) 100%);
        color: var(--bg-primary);
        border: none;
        font-weight: 600;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(212, 168, 85, 0.25);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stTextInput input,
    .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        caret-color: var(--accent-gold) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-gold-dim) !important;
        box-shadow: 0 0 0 2px var(--accent-gold-glow) !important;
    }

    /* Info boxes */
    .stAlert {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        border-left: 3px solid var(--accent-gold);
    }

    /* File Uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: var(--bg-tertiary) !important;
        border: 1px dashed var(--accent-gold-dim) !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploadDropzone"] * {
        color: var(--text-primary) !important;
    }

    /* Hide image fullscreen button */
    [data-testid="StyledFullScreenButton"] {
        display: none !important;
    }
    
    /* Compact Cover Customization Controls */
    [data-testid="stSlider"], 
    [data-testid="stRadio"] {
        margin-bottom: -1.2rem !important;
    }
    
    /* Hide slider min/max text to prevent overlap */
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"] {
        display: none !important;
    }
    /* Specific selector for the bottom numbers in Streamlit slider */
    div[data-testid="stSlider"] > div:nth-child(2) > div:nth-child(2) {
        display: none !important;
    }

    /* Code blocks */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: var(--bg-tertiary);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: var(--accent-gold);
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid var(--border-subtle);
        margin: 2rem 0;
    }

    /* Success/Error messages */
    .stSuccess {
        background: rgba(92, 184, 92, 0.15) !important;
        border: 1px solid rgba(92, 184, 92, 0.4) !important;
        border-left: 3px solid var(--success) !important;
    }

    .stError {
        background: rgba(201, 48, 44, 0.15) !important;
        border: 1px solid rgba(201, 48, 44, 0.4) !important;
        border-left: 3px solid var(--error) !important;
    }

    .stWarning {
        background: rgba(212, 168, 85, 0.15) !important;
        border: 1px solid rgba(212, 168, 85, 0.4) !important;
        border-left: 3px solid var(--accent-gold) !important;
    }

    /* Logo/Title styling */
    .masthead {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 2px solid var(--accent-gold);
        margin-bottom: 2rem;
    }

    .masthead h1 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .masthead .tagline {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }

    /* Ebook card */
    .ebook-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }

    .ebook-card:hover {
        border-color: var(--accent-gold-dim);
    }

    /* Progress item */
    .progress-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border-subtle);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }

    .progress-success {
        color: var(--success);
    }

    .progress-error {
        color: var(--error);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-subtle);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-dim);
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 700;
                    letter-spacing: 0.1em; color: #d4a855;">VIDEO TO EBOOK</div>
        <div style="font-family: 'Sora', sans-serif; font-size: 0.7rem; letter-spacing: 0.15em;
                    text-transform: uppercase; color: #5c5850; margin-top: 0.25rem;">YouTube → EPUB</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show existing ebooks
    st.markdown("#### 📚 Your Ebooks")
    
    ebook_files = sorted(EBOOKS_DIR.glob("*.epub"), reverse=True)
    
    if ebook_files:
        for ebook_file in ebook_files[:10]:  # Show last 10
            with open(ebook_file, "rb") as f:
                st.download_button(
                    label=ebook_file.name,
                    data=f.read(),
                    file_name=ebook_file.name,
                    mime="application/epub+zip",
                    key=f"dl_{ebook_file.name}",
                    use_container_width=True
                )
    else:
        st.caption("No ebooks yet. Generate your first one!")


# ============================================
# MAIN CONTENT
# ============================================
st.markdown("""
<div class="masthead">
    <h1>VIDEO TO EBOOK</h1>
    <div class="tagline">Transform YouTube videos into beautiful EPUB ebooks</div>
</div>
""", unsafe_allow_html=True)

import base64

# Two-column layout
col1, col2 = st.columns([1, 2.5], gap="large")

with col1:
    st.markdown("## Configuration")
    
    st.markdown("#### Video IDs")
    st.caption("Enter YouTube video IDs or URLs, one per line")
    
    video_input = st.text_area(
        "Video IDs",
        height=150,
        placeholder="dQw4w9WgXcQ\nhttps://www.youtube.com/watch?v=VIDEO_ID\n...",
        label_visibility="collapsed"
    )
    
    st.markdown("#### Book Details")
    default_title_hint = f"Youtube Collection {datetime.now().strftime('%y.%m.%d')}"
    book_title = st.text_input(
        "Book Title (optional)",
        placeholder=default_title_hint,
        label_visibility="visible"
    )
    
    cover_file = st.file_uploader(
        "Book Cover (optional)",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    generate_clicked = st.button("📚 Generate Ebook", type="primary", use_container_width=True)

with col2:
    st.markdown("## Cover Preview")
    
    display_title = book_title.strip() if book_title.strip() else default_title_hint
    cover_file_bytes = cover_file.getvalue() if cover_file else None
    
    col_preview, col_settings = st.columns([1, 1.4], gap="large")
    
    import glob
    all_covers = sorted(glob.glob("default_covers/*.jpg"))
    if not all_covers:
        all_covers = sorted(glob.glob("default_covers/*.jpeg"))
        
    if "bg_choice" not in st.session_state:
        st.session_state.bg_choice = all_covers[0] if all_covers else None
        
    with col_settings:
        st.markdown(
            "<div style='color: #888; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;'>Background Layout</div>",
            unsafe_allow_html=True
        )
        
        # Determine current index
        current_idx = 0
        if st.session_state.bg_choice in all_covers:
            current_idx = all_covers.index(st.session_state.bg_choice)

        # Grid height matches around 2 rows of square thumbnails
        gallery = st.container(height=230)
        with gallery:
            selected_idx = image_select(
                label="",
                images=all_covers,
                use_container_width=True,
                return_value="index",
                index=current_idx,
                key="bg_gallery"
            )
        
        if all_covers:
            st.session_state.bg_choice = all_covers[selected_idx]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='color: #888; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;'>Typography & Layout</div>",
            unsafe_allow_html=True
        )
        
        # Style Presets
        st.markdown("<div style='font-size: 13px; margin-bottom: 8px; font-weight: 500;'>Quick Presets</div>", unsafe_allow_html=True)
        preset_cols = st.columns(3)
        if preset_cols[0].button("Classic White", use_container_width=True):
            st.session_state.update({"font_size": 72, "text_color": "#ffffff", "text_align": "center", "text_y": 0, "text_x": 0})
            st.rerun()
        if preset_cols[1].button("Light Minimal", use_container_width=True):
            st.session_state.update({"font_size": 60, "text_color": "#222222", "text_align": "center", "text_y": -150, "text_x": 0})
            st.rerun()
        if preset_cols[2].button("Gold Elegant", use_container_width=True):
            st.session_state.update({"font_size": 84, "text_color": "#D4A855", "text_align": "center", "text_y": 100, "text_x": 0})
            st.rerun()
            
        # Initialize defaults in session_state if they don't exist
        defaults = {"font_size": 72, "text_color": "#ffffff", "text_align": "center", "text_x": 0, "text_y": 0}
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

        text_color = st.color_picker("Text Color", key="text_color")
        
        font_size = st.slider("Font Size", 40, 100, key="font_size")
        text_x = st.slider("Horizontal Offset", -400, 400, key="text_x")
        text_y = st.slider("Vertical Offset", -600, 600, key="text_y")
        text_align = st.radio("Text Alignment", ["left", "center", "right"], horizontal=True, key="text_align")

    # Determine base image bytes
    base_img_to_use = cover_file_bytes
    if not base_img_to_use:
        try:
            with open(st.session_state.bg_choice, "rb") as f:
                base_img_to_use = f.read()
        except:
            base_img_to_use = None

    # Generate rendering
    preview_bytes = generate_cover_bytes(
        title=display_title,
        base_img_bytes=base_img_to_use,
        font_size=font_size,
        text_align=text_align,
        text_x_offset=text_x,
        text_y_offset=text_y,
        text_color=text_color
    )
    
    with col_preview:
        st.markdown(
            "<div style='text-align: center; color: #888; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;'>PREVIEW</div>",
            unsafe_allow_html=True
        )
        st.image(preview_bytes, use_container_width=True, caption=display_title)

st.markdown("<br>", unsafe_allow_html=True)

# Generate logic
if generate_clicked:
    # Parse video IDs
    lines = video_input.strip().split("\n")
    video_ids = [line.strip() for line in lines if line.strip()]
    
    if not video_ids:
        st.error("Please enter at least one video ID or URL")
    else:
        # Validate video IDs
        valid_ids = []
        invalid_ids = []
        
        for vid in video_ids:
            extracted = extract_video_id(vid)
            if extracted:
                valid_ids.append(extracted)
            else:
                invalid_ids.append(vid)
        
        if invalid_ids:
            st.warning(f"Invalid IDs will be skipped: {', '.join(invalid_ids)}")
        
        if valid_ids:
            st.info(f"Processing {len(valid_ids)} video(s)...")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_container = st.empty()
            log_container = st.expander("View Log", expanded=True)
            
            logs = []
            
            def update_progress(step, message):
                logs.append(message)
                with log_container:
                    st.text("\n".join(logs[-20:]))  # Show last 20 log lines
                
                # Update progress bar
                if "/" in step:
                    current, total = step.split("/")
                    if int(total) > 0:  # Prevent division by zero
                        progress = int(current) / int(total)
                        progress_bar.progress(progress)
                        status_container.text(f"Processing video {step}...")
            
            try:
                # Phase 1: Fetch all transcripts
                status_container.text("Phase 1: Fetching transcripts...")
                videos_with_transcripts = fetch_all_transcripts(valid_ids, progress_callback=update_progress)
                
                if not videos_with_transcripts:
                    st.error("No transcripts could be fetched. Check video IDs and try again.")
                else:
                    # Phase 2: Generate all articles
                    status_container.text("Phase 2: Generating articles with AI...")
                    articles = generate_all_articles(videos_with_transcripts, progress_callback=update_progress)
                    
                    if articles:
                        progress_bar.progress(1.0)
                        status_container.text("Creating EPUB...")
                        
                        # Generate ebook
                        status_container.text("Phase 3: Creating EPUB...")
                        epub_path = create_epub(articles, output_dir=EBOOKS_DIR, book_title=display_title, cover_image=preview_bytes)
                        
                        st.success(f"✓ Ebook created with {len(articles)} chapter(s)!")
                        
                        # Download button
                        with open(epub_path, "rb") as f:
                            st.download_button(
                                label="📥 Download EPUB",
                                data=f.read(),
                                file_name=epub_path.name,
                                mime="application/epub+zip",
                                type="primary",
                                use_container_width=True
                            )
                    else:
                        st.error("No articles could be generated. Check API configuration.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                with log_container:
                    st.text("\n".join(logs))

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.caption("YouTube to Ebook Generator • Powered by Claude AI")
