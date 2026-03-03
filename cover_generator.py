import io
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageColor

def generate_cover_bytes(
    title,
    base_img_bytes=None,
    bg_color="#1e1e1e",
    font_size=60,
    text_align="center",
    text_x_offset=0,
    text_y_offset=0,
    text_color="#ffffff"
):
    """
    Generate a 800x1200 cover image with a text box overlay.
    """
    width, height = 800, 1200
    
    # 1. Base Image
    if base_img_bytes:
        try:
            img = Image.open(io.BytesIO(base_img_bytes)).convert("RGBA")
            # Center crop to 800x1200
            aspect = img.width / img.height
            target_aspect = width / height
            if aspect > target_aspect:
                new_w = int(img.height * target_aspect)
                offset = (img.width - new_w) // 2
                img = img.crop((offset, 0, offset + new_w, img.height))
            else:
                new_h = int(img.width / target_aspect)
                offset = (img.height - new_h) // 2
                img = img.crop((0, offset, img.width, offset + new_h))
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        except Exception as e:
            print("Failed to load base image, using solid background:", e)
            img = Image.new("RGBA", (width, height), bg_color)
    else:
        img = Image.new("RGBA", (width, height), bg_color)

    if not title:
        title = "Untitled Ebook"

    # 2. Font Loader (with Chinese support for Mac)
    font = None
    mac_fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf"
    ]
    for fp in mac_fonts:
        try:
            font = ImageFont.truetype(fp, int(font_size))
            break
        except Exception:
            continue
            
    if not font:
        font = ImageFont.load_default()

    # 3. Text Wrapping
    # Heuristic: avg char width is ~50% of font size for English, ~100% for Chinese
    # We will use 70% as a safe bet
    avg_char_width = font_size * 0.7
    max_chars = int((width - 120) / avg_char_width)
    if max_chars < 5: 
        max_chars = 5
    wrapped_lines = textwrap.wrap(title, width=max_chars)

    text = "\n".join(wrapped_lines)
    
    # Calculate Dimensions
    draw = ImageDraw.Draw(img)
    line_spacing = int(font_size * 0.3)
    
    # We use align and spacing for multiline blocks
    try:
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=line_spacing, align=text_align)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.multiline_textsize(text, font=font, spacing=line_spacing)

    # Text bounding limits 
    max_text_w = width - 40
    box_w = min(max_text_w, text_w)
    box_h = text_h

    # Default vertical position: center of the upper 20% of the book
    default_y = int(height * 0.2)
    text_x = (width - box_w) // 2 + text_x_offset
    text_y = default_y + text_y_offset
    
    text_cx = text_x + box_w // 2
    text_cy = text_y + box_h // 2
    
    # 5. Draw Text
    try:
        txt_rgb = ImageColor.getrgb(text_color)
    except Exception:
        txt_rgb = (255, 255, 255)
    txt_fill = (*txt_rgb, 255)
    
    try:
        draw.multiline_text((text_cx, text_cy), text, font=font, fill=txt_fill, spacing=line_spacing, align=text_align, anchor="mm")
    except ValueError:
        # Fallback if "mm" anchor is not supported
        top_left_x = text_cx - text_w // 2
        top_left_y = text_cy - text_h // 2
        draw.multiline_text((top_left_x, top_left_y), text, font=font, fill=txt_fill, spacing=line_spacing, align=text_align)

    # 7. Convert to Bytes
    out_img = img.convert("RGB")
    buf = io.BytesIO()
    out_img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

if __name__ == "__main__":
    # Test
    b = generate_cover_bytes("My YouTube Collection 2026.02.28", bg_color="#123456")
    with open("test_cover.jpg", "wb") as f:
        f.write(b)
    print("Test cover saved.")
