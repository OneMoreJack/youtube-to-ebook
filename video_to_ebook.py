"""
YouTube Video to Ebook Generator
Generate EPUB ebooks from YouTube video IDs.

Usage:
    python video_to_ebook.py VIDEO_ID_1 VIDEO_ID_2 ...
    python video_to_ebook.py --title "My Ebook" VIDEO_ID_1 VIDEO_ID_2
"""

import os
import re
import time
import argparse
import yt_dlp
from pathlib import Path
from dotenv import load_dotenv

from get_transcripts import get_transcript
from write_articles import write_article
from create_ebook import create_epub

# Load environment
load_dotenv()

# Paths
PROJECT_DIR = Path(__file__).parent
TRANSCRIPT_DIR = PROJECT_DIR / "transcripts"

# Create transcripts directory
TRANSCRIPT_DIR.mkdir(exist_ok=True)


def extract_video_id(url_or_id):
    """
    Extract video ID from a YouTube URL or return as-is if already an ID.
    """
    text = url_or_id.strip()
    
    # Already a video ID (11 characters, alphanumeric + _ -)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', text):
        return text
    
    # YouTube URL patterns
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


def get_cached_transcript(video_id):
    """
    Get transcript from local cache if available.
    Returns transcript text or None if not cached.
    """
    cache_file = TRANSCRIPT_DIR / f"{video_id}.txt"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_transcript_cache(video_id, transcript):
    """
    Save transcript to local cache.
    """
    cache_file = TRANSCRIPT_DIR / f"{video_id}.txt"
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(transcript)


def get_video_info(video_id):
    """
    Get video metadata using yt-dlp (no API key required).
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                "title": info.get("title", "Unknown Title"),
                "description": info.get("description", ""),
                "channel": info.get("channel", info.get("uploader", "Unknown Channel")),
                "video_id": video_id,
                "url": url
            }
    except Exception as e:
        print(f"  ⚠ Error fetching video info: {e}")
        return None


def fetch_all_transcripts(video_ids, progress_callback=None):
    """
    Phase 1: Fetch all transcripts first (with caching).
    Follows get_transcripts.py pattern with delay between requests.
    
    Returns:
        List of videos with transcripts
    """
    def update_progress(step, message):
        if progress_callback:
            progress_callback(step, message)
        print(message)
    
    videos_with_transcripts = []
    total = len(video_ids)
    
    update_progress("0/0", "\n📝 PHASE 1: Fetching transcripts...\n")
    update_progress("0/0", "=" * 60)
    
    for i, video_input in enumerate(video_ids):
        # Extract video ID
        video_id = extract_video_id(video_input)
        if not video_id:
            update_progress(f"{i+1}/{total}", f"⚠ Invalid video ID/URL: {video_input}")
            continue
        
        update_progress(f"{i+1}/{total}", f"Processing {i+1}/{total}: {video_id}")
        
        # Step 1: Get video info
        video = get_video_info(video_id)
        if not video:
            update_progress(f"{i+1}/{total}", f"  ✗ Could not fetch video info")
            continue
        
        update_progress(f"{i+1}/{total}", f"  → {video['title'][:50]}...")
        
        # Step 2: Check cache first
        transcript = get_cached_transcript(video_id)
        if transcript:
            update_progress(f"{i+1}/{total}", f"  ✓ Loaded from cache ({len(transcript.split())} words)")
            video["transcript"] = transcript
            videos_with_transcripts.append(video)
            continue
        
        # Step 3: Fetch from YouTube
        update_progress(f"{i+1}/{total}", f"  → Fetching transcript from YouTube...")
        transcript = get_transcript(video_id)
        
        if transcript:
            # Save to cache
            save_transcript_cache(video_id, transcript)
            video["transcript"] = transcript
            videos_with_transcripts.append(video)
            update_progress(f"{i+1}/{total}", f"  ✓ Got {len(transcript.split())} words (cached)\n")
        else:
            update_progress(f"{i+1}/{total}", f"  ✗ No transcript available\n")
        
        # Small delay between requests to avoid rate limiting
        if i < len(video_ids) - 1:
            time.sleep(2)
    
    update_progress("0/0", "=" * 60)
    update_progress("0/0", f"Got transcripts for {len(videos_with_transcripts)} of {total} videos\n")
    
    return videos_with_transcripts


def generate_all_articles(videos, progress_callback=None):
    """
    Phase 2: Generate articles for all videos with transcripts.
    
    Returns:
        List of articles ready for ebook generation
    """
    def update_progress(step, message):
        if progress_callback:
            progress_callback(step, message)
        print(message)
    
    articles = []
    total = len(videos)
    
    update_progress("0/0", "\n✍️ PHASE 2: Writing articles with AI...\n")
    update_progress("0/0", "=" * 60)
    
    for i, video in enumerate(videos):
        update_progress(f"{i+1}/{total}", f"Writing article {i+1}/{total}: {video['title'][:40]}...")
        
        article_content = write_article(video)
        
        if article_content:
            articles.append({
                "title": video["title"],
                "channel": video["channel"],
                "url": video["url"],
                "article": article_content
            })
            update_progress(f"{i+1}/{total}", f"  ✓ Generated ({len(article_content)} chars)\n")
        else:
            update_progress(f"{i+1}/{total}", f"  ✗ Failed to generate article\n")
    
    update_progress("0/0", "=" * 60)
    update_progress("0/0", f"Generated {len(articles)} articles\n")
    
    return articles


def generate_ebook(video_ids, book_title=None, output_dir=None, progress_callback=None):
    """
    Main function: Generate an EPUB ebook from video IDs.
    
    Two-phase processing:
    1. Fetch all transcripts first
    2. Then generate all articles
    """
    print("=" * 60)
    print("  VIDEO TO EBOOK GENERATOR")
    print("=" * 60)
    print(f"  Processing {len(video_ids)} video(s)")
    print("=" * 60)
    
    # Phase 1: Fetch all transcripts
    videos_with_transcripts = fetch_all_transcripts(video_ids, progress_callback)
    
    if not videos_with_transcripts:
        print("\n✗ No transcripts available. Check video IDs and try again.")
        return None
    
    # Phase 2: Generate all articles
    articles = generate_all_articles(videos_with_transcripts, progress_callback)
    
    if not articles:
        print("\n✗ No articles generated. Check API configuration.")
        return None
    
    # Phase 3: Create EPUB
    print("\n📚 Creating EPUB ebook...")
    epub_path = create_epub(articles, output_dir=output_dir, book_title=book_title)
    
    print("\n" + "=" * 60)
    print("  DONE!")
    print("=" * 60)
    
    return epub_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate EPUB ebook from YouTube videos"
    )
    parser.add_argument(
        "video_ids",
        nargs="+",
        help="YouTube video IDs or URLs"
    )
    parser.add_argument(
        "--title", "-t",
        help="Custom book title"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    generate_ebook(
        video_ids=args.video_ids,
        book_title=args.title,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
