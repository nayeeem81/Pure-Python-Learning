# Quick Start Guide - Floating Text Panel Feature

## How to Use the Feature

### 1. Access the Image Editor
Navigate to `/editimage` page in your application.

### 2. Open the Floating Panel
**Option A:** Press the **T** key anywhere on the page
**Option B:** The panel will be visible on the right side if previously shown

### 3. Add Text
1. Enter a **Title** (max 200 characters) in the title input field
2. Enter a **Short Brief** (max 500 characters) in the textarea
3. Click the **💾 Add/Update** button

### 4. View the Overlay
- The entered text will immediately appear over the image canvas
- Title appears at top-left in gold (#f5c451)
- Brief appears below in white
- Both have drop shadows for readability over any image

### 5. Download the Image
Click the **Download PNG** button to save the image with text composited into it.

### 6. Clear Text
Click the **🗑️ Clear** button to remove all saved text. You'll be asked to confirm.

### 7. Hide the Panel
- Click the **×** button in the panel header
- Or press **T** key again

## Keyboard Shortcuts
| Key | Action |
|-----|--------|
| **T** | Toggle floating panel visibility (press anywhere, not in inputs) |

## Features Explained

### Real-time Preview
As you type in the title or brief fields, the text appears on the canvas in real-time. This lets you see exactly how it will look before downloading.

### Automatic Persistence
When you click "Add/Update", the text is saved to the database. When you reload the page, your text will automatically reappear.

### Presentation-Style Layout
The text is automatically positioned and sized based on your image dimensions:
- Larger images get larger fonts
- Smaller images get smaller fonts
- Text is always positioned in safe margins
- Drop shadows ensure readability on any background

### Composite Download
The downloaded PNG contains both:
1. The modified image (with your channel adjustments)
2. The text overlay (title + brief)
All in a single flat image file.

## Troubleshooting

### Panel Not Appearing
1. Refresh the page
2. Check browser console (F12) for errors
3. Ensure you're not typing in another input field when pressing T

### Text Not Saving
1. Check browser network tab (F12) for failed requests
2. Verify the "Add/Update" button was clicked (not just Enter key)
3. Check if the database is connected
4. Look for any error alerts in the UI

### Text Not Showing on Download
1. Ensure text was added/saved (it should show on canvas first)
2. Try refreshing and adding text again
3. Check that the title and brief fields have content
4. Verify you're saving before downloading

### Text Too Large/Small
This is normal and adjusts based on your image size. The algorithm automatically sizes fonts based on image dimensions.

## Technical Details

### API Endpoints Used
- `POST /api/metadata/save` - Save/update text
- `GET /api/metadata/current` - Load saved text on page load
- `POST /api/metadata/clear` - Clear saved text

### Data Stored
- **Title:** Up to 200 characters
- **Short Brief:** Up to 500 characters
- **Metadata:** Version, creation date, modification date, user info

### Supported Fonts
The system will use the best available system font:
- Windows: Arial
- macOS: Arial
- Linux: DejaVuSans
- Fallback: Pillow default font

## Tips for Best Results

1. **Keep text concise:** Long text will wrap but may look cramped on small images
2. **Use simple titles:** Avoid special characters if possible
3. **Test download:** Always download once to see final result
4. **Image size matters:** Larger images accommodate more text
5. **Check contrast:** Light text works best on dark backgrounds, vice versa

## Common Use Cases

### Presentation Slides
Use the title for the main topic and brief for supporting details. Download the image to use in presentations.

### Social Media Posts
Add attention-grabbing titles and descriptions to images before sharing online.

### Documentation
Add captions to images for better clarity in technical documentation.

### Watermarking
Add your name or project name as a watermark to protect images.

## Support & Feedback

If you encounter issues:
1. Check the browser console (F12) for errors
2. Try clearing browser cache
3. Refresh the page and try again
4. Report any bugs with error messages

---

**Version:** 1.0
**Last Updated:** 2024
**Status:** Production Ready
