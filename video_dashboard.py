"""
YouTube Video to Ebook Dashboard
A beautiful web interface to generate ebooks from YouTube videos.
"""

import streamlit as st
import os
import requests
from pathlib import Path
from datetime import datetime

from video_to_ebook import extract_video_id, generate_ebook, fetch_all_transcripts, generate_all_articles
from create_ebook import create_epub, DEFAULT_OUTPUT_DIR

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
    .stButton > button {
        font-family: 'Sora', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.03em;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        border: 1px solid var(--border-subtle);
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .stButton > button:hover {
        border-color: var(--accent-gold-dim);
        background: var(--accent-gold-glow);
        color: var(--accent-gold);
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
    .stTextArea > div > div > textarea {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        color: var(--text-primary);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-gold-dim);
        box-shadow: 0 0 0 2px var(--accent-gold-glow);
    }

    /* Info boxes */
    .stAlert {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        border-left: 3px solid var(--accent-gold);
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

# Input section
st.markdown("## Video IDs")
st.caption("Enter YouTube video IDs or URLs, one per line")

video_input = st.text_area(
    "Video IDs",
    height=150,
    placeholder="dQw4w9WgXcQ\nhttps://www.youtube.com/watch?v=VIDEO_ID\n...",
    label_visibility="collapsed"
)

# Book title
col1, col2 = st.columns([3, 1])
with col1:
    book_title = st.text_input(
        "Book Title (optional)",
        placeholder="My YouTube Collection",
        label_visibility="visible"
    )

with col2:
    cover_file = st.file_uploader(
        "Book Cover (optional)",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible"
    )

if cover_file:
    st.image(cover_file, caption="Cover Preview", width=150)

st.markdown("<br>", unsafe_allow_html=True)

# Generate button
if st.button("📚 Generate Ebook", type="primary", use_container_width=True):
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
                        
                        # Handle cover image
                        cover_image_bytes = None
                        if cover_file:
                            cover_image_bytes = cover_file.read()
                        elif articles and 'thumbnail' in videos_with_transcripts[0] and videos_with_transcripts[0]['thumbnail']:
                            # Fallback to first video thumbnail
                            try:
                                status_container.text("Phase 3: Fetching video thumbnail for cover...")
                                thumb_url = videos_with_transcripts[0]['thumbnail']
                                response = requests.get(thumb_url, timeout=5)
                                if response.status_code == 200:
                                    cover_image_bytes = response.content
                                    update_progress("3/3", "  ✓ Using video thumbnail as cover")
                            except Exception as e:
                                update_progress("3/3", f"  ⚠ Could not fetch thumbnail: {e}")

                        # Generate ebook
                        title = book_title if book_title else None
                        status_container.text("Phase 3: Creating EPUB...")
                        epub_path = create_epub(articles, output_dir=EBOOKS_DIR, book_title=title, cover_image=cover_image_bytes)
                        
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
