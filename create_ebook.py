"""
Create EPUB Ebook Utility
Standalone module for generating EPUB ebooks from articles.
Extracted from send_email.py for reuse in video-to-ebook workflow.
"""

import os
import markdown
from datetime import datetime
from ebooklib import epub
from pathlib import Path

# Default output directory
PROJECT_DIR = Path(__file__).parent
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "ebooks"


def create_epub(articles, output_dir=None, book_title=None, cover_image=None):
    """
    Create an EPUB ebook from articles.
    
    Args:
        articles: List of dicts with keys: title, channel, url, article
        output_dir: Output directory path (default: ebooks/)
        book_title: Custom book title (default: "YouTube Digest - {date}")
        cover_image: Optional bytes of the cover image
    
    Returns:
        Path to the generated EPUB file
    """
    # Set output directory
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename and title
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    today = datetime.now().strftime("%B %d, %Y")
    
    if book_title:
        display_title = book_title
        filename = f"{book_title.replace(' ', '_')}_{timestamp}.epub"
    else:
        display_title = f"YouTube Digest - {today}"
        filename = f"ebook_{timestamp}.epub"
    
    filepath = output_dir / filename

    # Create the ebook
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(f"youtube-ebook-{timestamp}")
    book.set_title(display_title)
    book.set_language("cn")  # Changed to Chinese for better compatibility with YouTube content often translated to Chinese
    book.add_author("YouTube to Ebook Generator")

    # Set cover if provided
    if cover_image:
        book.set_cover("cover.jpg", cover_image)

    # CSS for nice formatting on ebook readers
    style = """
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        padding: 1em;
    }
    h1 {
        font-size: 1.5em;
        margin-top: 1em;
        border-bottom: 1px solid #ccc;
        padding-bottom: 0.3em;
    }
    h2 {
        font-size: 1.3em;
        margin-top: 1em;
    }
    h3 {
        font-size: 1.1em;
    }
    .intro {
        background: #f5f5f5;
        padding: 1em;
        border-left: 3px solid #666;
        margin-bottom: 1.5em;
        font-size: 0.95em;
    }
    .watch-link {
        margin-top: 1.5em;
        padding: 0.5em;
        background: #f0f0f0;
        display: block;
    }
    blockquote {
        border-left: 3px solid #ccc;
        padding-left: 1em;
        margin-left: 0;
        font-style: italic;
        color: #555;
    }
    """
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)

    chapters = []

    # Create a chapter for each article
    for i, article in enumerate(articles):
        # Convert markdown to HTML
        article_html = markdown.markdown(article['article'])

        chapter_content = f"""
        <html>
        <head>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body>
            <div class="intro">
                <p><em>This article is based on the video "<strong>{article['title']}</strong>" from the YouTube channel <strong>{article['channel']}</strong>.</em></p>
            </div>
            {article_html}
            <p class="watch-link">Watch the original video: {article['url']}</p>
        </body>
        </html>
        """

        chapter = epub.EpubHtml(
            title=article['title'][:50],
            file_name=f"chapter_{i+1}.xhtml",
            lang="en"
        )
        chapter.content = chapter_content
        chapter.add_item(nav_css)

        book.add_item(chapter)
        chapters.append(chapter)

    # Create table of contents
    book.toc = tuple(chapters)

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set the reading order
    book.spine = ["nav"] + chapters

    # Write the EPUB file
    epub.write_epub(str(filepath), book)

    print(f"  ✓ Created EPUB: {filepath}")
    return filepath


if __name__ == "__main__":
    # Test with mock articles
    test_articles = [
        {
            "title": "Test Article 1",
            "channel": "Test Channel",
            "url": "https://youtube.com/watch?v=test1",
            "article": "# Test Headline\n\nThis is a test article with **bold** and *italic* text.\n\n## Section 1\n\nSome content here."
        },
        {
            "title": "Test Article 2",
            "channel": "Another Channel",
            "url": "https://youtube.com/watch?v=test2",
            "article": "# Second Article\n\nMore content here.\n\n> A nice quote"
        }
    ]

    print("Testing EPUB generation...")
    path = create_epub(test_articles, book_title="Test Ebook")
    print(f"Generated: {path}")
