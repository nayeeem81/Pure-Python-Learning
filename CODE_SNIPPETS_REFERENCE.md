# Code Snippets & Reference Guide

## Quick Reference - All Components

### 1. Database Model
**File:** `WebFastapiGttsProject/data/model.py`

```python
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text

class ImageMetadata(SQLModel, table=True):
	__tablename__ = "image_metadata"

	id: Optional[int] = Field(default=None, primary_key=True)
	title: str = Field(sa_column=Column(Text, nullable=False), default="")
	short_brief: str = Field(sa_column=Column(Text, nullable=False), default="")
	version: int = Field(default=1)
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	modified_by: Optional[str] = Field(default=None, max_length=100)
```

### 2. API Endpoints
**File:** `WebFastapiGttsProject/api/imagetensor.py`

#### Save Endpoint
```python
@router_imagetensor.post("/metadata/save", response_model=ImageMetadataResponse)
async def save_image_metadata(
	request: ImageMetadataRequest,
	session: Session = Depends(get_db)
):
	try:
		statement = select(ImageMetadata)
		result = await session.execute(statement)
		metadata = result.scalars().first()

		if metadata:
			metadata.title = request.title
			metadata.short_brief = request.short_brief
			metadata.version += 1
			metadata.modified_at = datetime.now(timezone.utc)
		else:
			metadata = ImageMetadata(
				title=request.title,
				short_brief=request.short_brief,
				version=1
			)
			session.add(metadata)

		await session.commit()
		await session.refresh(metadata)

		return ImageMetadataResponse(
			id=metadata.id,
			title=metadata.title,
			short_brief=metadata.short_brief,
			version=metadata.version,
			modified_at=metadata.modified_at
		)
	except Exception as exc:
		await session.rollback()
		raise HTTPException(status_code=500, detail=f"Save failed: {str(exc)}")
```

#### Retrieve Endpoint
```python
@router_imagetensor.get("/metadata/current", response_model=ImageMetadataResponse | None)
async def get_image_metadata(session: Session = Depends(get_db)):
	try:
		statement = select(ImageMetadata)
		result = await session.execute(statement)
		metadata = result.scalars().first()
		return metadata if metadata else None
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(exc)}")
```

#### Clear Endpoint
```python
@router_imagetensor.post("/metadata/clear")
async def clear_image_metadata(session: Session = Depends(get_db)):
	try:
		statement = select(ImageMetadata)
		result = await session.execute(statement)
		metadata = result.scalars().first()

		if metadata:
			await session.delete(metadata)
			await session.commit()

		return JSONResponse(
			content={"status": "success", "message": "Metadata cleared."},
			status_code=200
		)
	except Exception as exc:
		await session.rollback()
		raise HTTPException(status_code=500, detail=f"Clear failed: {str(exc)}")
```

### 3. Image Processing Function
**File:** `WebFastapiGttsProject/utilities/image_processing.py`

```python
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def get_system_font(size: int = 40):
	"""Return a system font with fallback to default."""
	font_paths = [
		"/Windows/Fonts/arial.ttf",  # Windows
		"/System/Library/Fonts/Arial.ttf",  # macOS
		"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
	]
	for font_path in font_paths:
		try:
			return ImageFont.truetype(font_path, size)
		except (OSError, IOError):
			continue
	return ImageFont.load_default()

def composite_text_on_image(
	image_array: np.ndarray,
	title: str,
	short_brief: str,
	bg_color=(20, 20, 20),
	text_color=(255, 255, 255),
	accent_color=(245, 196, 81)
) -> np.ndarray:
	"""Composite title and brief text onto an image."""
	result = image_array.copy()
	img = Image.fromarray(result, mode="RGB")
	draw = ImageDraw.Draw(img, "RGBA")

	height, width = result.shape[:2]
	margin_x = max(20, width // 20)
	margin_y = max(20, height // 20)

	title_font_size = max(24, int(height / 12))
	brief_font_size = max(16, int(height / 18))

	title_font = get_system_font(title_font_size)
	brief_font = get_system_font(brief_font_size)

	y_position = margin_y

	# Draw title with background
	if title:
		bbox = draw.textbbox((0, 0), title, font=title_font)
		text_width = bbox[2] - bbox[0]
		text_height = bbox[3] - bbox[1]

		padding = 8
		bg_box = [
			margin_x - padding,
			y_position - padding,
			margin_x + text_width + padding,
			y_position + text_height + padding,
		]
		draw.rectangle(bg_box, fill=(*bg_color, 200), outline=accent_color)
		draw.text((margin_x, y_position), title, fill=text_color, font=title_font)
		y_position += text_height + 20

	# Draw brief with background
	if short_brief:
		lines = short_brief.split('\n')
		brief_text_height = sum(
			(draw.textbbox((0, 0), line, font=brief_font)[3] - 
			 draw.textbbox((0, 0), line, font=brief_font)[1]) + 6 
			for line in lines
		)

		padding = 8
		usable_width = width - (2 * margin_x)
		bg_box = [
			margin_x - padding,
			y_position - padding,
			margin_x + usable_width + padding,
			y_position + brief_text_height + padding,
		]
		draw.rectangle(bg_box, fill=(*bg_color, 180))

		for line in lines:
			draw.text((margin_x, y_position), line, fill=text_color, font=brief_font)
			bbox = draw.textbbox((0, 0), line, font=brief_font)
			y_position += (bbox[3] - bbox[1]) + 6

	return np.asarray(img, dtype=np.uint8)
```

### 4. HTML Components
**File:** `WebFastapiGttsProject/templates/editimage.html`

#### Keyboard Instruction
```html
<div class="keyboard-instruction">
	<p><strong>💡 Tip:</strong> Press <kbd>T</kbd> to toggle the floating text panel</p>
</div>
```

#### Floating Panel
```html
<div id="floating-panel" class="floating-panel" style="display: none;">
	<div class="floating-panel-header">
		<h3>Presentation Text</h3>
		<button id="close-panel-button" class="close-button" type="button">&times;</button>
	</div>
	<div class="floating-panel-content">
		<div class="form-group">
			<label for="title-input">Title:</label>
			<input id="title-input" type="text" placeholder="Enter slide title" maxlength="200">
		</div>
		<div class="form-group">
			<label for="brief-input">Short Brief:</label>
			<textarea id="brief-input" placeholder="Enter brief description" rows="4" maxlength="500"></textarea>
		</div>
		<div class="floating-panel-actions">
			<button id="save-metadata-button" class="custom-btn">💾 Add/Update</button>
			<button id="clear-metadata-button" class="custom-btn">🗑️ Clear</button>
		</div>
	</div>
</div>
```

#### Text Overlay Canvas
```html
<canvas id="text-overlay-canvas" aria-label="Text overlay canvas" 
		style="position: absolute; top: 0; left: 0; background: transparent;"></canvas>
```

### 5. JavaScript Implementation
**File:** `WebFastapiGttsProject/static/js/edit-image.js`

#### Load Metadata
```javascript
async function loadCurrentMetadata() {
	try {
		const response = await fetch('/api/metadata/current');
		if (response.ok && response.status !== 204) {
			const data = await response.json();
			if (data) {
				currentMetadata = {
					title: data.title || '',
					short_brief: data.short_brief || ''
				};
				titleInput.value = currentMetadata.title;
				briefInput.value = currentMetadata.short_brief;
				renderTextOverlay();
			}
		}
	} catch (error) {
		console.error('Failed to load metadata:', error);
	}
}
```

#### Save Metadata
```javascript
async function saveMetadata() {
	const title = titleInput.value.trim();
	const short_brief = briefInput.value.trim();

	try {
		const response = await fetch('/api/metadata/save', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ title, short_brief })
		});

		if (response.ok) {
			const data = await response.json();
			currentMetadata = {
				title: data.title,
				short_brief: data.short_brief
			};
			renderTextOverlay();
			console.log('Metadata saved successfully');
		} else {
			alert('Failed to save metadata');
		}
	} catch (error) {
		console.error('Metadata save error:', error);
		alert('Error saving metadata: ' + error.message);
	}
}
```

#### Clear Metadata
```javascript
async function clearMetadata() {
	try {
		const response = await fetch('/api/metadata/clear', { method: 'POST' });

		if (response.ok) {
			currentMetadata = { title: '', short_brief: '' };
			titleInput.value = '';
			briefInput.value = '';
			renderTextOverlay();
			console.log('Metadata cleared');
		} else {
			alert('Failed to clear metadata');
		}
	} catch (error) {
		console.error('Metadata clear error:', error);
		alert('Error clearing metadata: ' + error.message);
	}
}
```

#### Render Text Overlay
```javascript
function renderTextOverlay() {
	if (!tensor) return;

	textOverlayCanvas.width = canvas.width;
	textOverlayCanvas.height = canvas.height;

	if (!currentMetadata.title && !currentMetadata.short_brief) {
		textOverlayContext.clearRect(0, 0, textOverlayCanvas.width, textOverlayCanvas.height);
		return;
	}

	textOverlayContext.clearRect(0, 0, textOverlayCanvas.width, textOverlayCanvas.height);

	const width = textOverlayCanvas.width;
	const height = textOverlayCanvas.height;
	const marginX = Math.max(20, width / 20);
	const marginY = Math.max(20, height / 20);

	const titleFontSize = Math.max(24, Math.floor(height / 12));
	const briefFontSize = Math.max(16, Math.floor(height / 18));

	textOverlayContext.save();

	let yPos = marginY;

	// Draw title with shadow
	if (currentMetadata.title) {
		textOverlayContext.font = `bold ${titleFontSize}px Arial`;
		textOverlayContext.fillStyle = '#f5c451';
		textOverlayContext.shadowColor = 'rgba(0, 0, 0, 0.7)';
		textOverlayContext.shadowBlur = 8;
		textOverlayContext.shadowOffsetX = 2;
		textOverlayContext.shadowOffsetY = 2;
		textOverlayContext.fillText(currentMetadata.title, marginX, yPos);
		yPos += titleFontSize + 20;
		textOverlayContext.shadowColor = 'transparent';
	}

	// Draw brief with shadow
	if (currentMetadata.short_brief) {
		textOverlayContext.font = `${briefFontSize}px Arial`;
		textOverlayContext.fillStyle = '#ffffff';
		textOverlayContext.shadowColor = 'rgba(0, 0, 0, 0.7)';
		textOverlayContext.shadowBlur = 6;
		textOverlayContext.shadowOffsetX = 1;
		textOverlayContext.shadowOffsetY = 1;

		const maxWidth = width - (2 * marginX);
		const lineHeight = briefFontSize + 8;
		const lines = wrapText(currentMetadata.short_brief, maxWidth, briefFontSize);

		lines.forEach((line) => {
			textOverlayContext.fillText(line, marginX, yPos);
			yPos += lineHeight;
		});
	}

	textOverlayContext.restore();
}
```

#### Text Wrapping Helper
```javascript
function wrapText(text, maxWidth, fontSize) {
	const canvas_temp = document.createElement('canvas');
	const ctx_temp = canvas_temp.getContext('2d');
	ctx_temp.font = `${fontSize}px Arial`;

	const words = text.split(' ');
	const lines = [];
	let currentLine = '';

	words.forEach((word) => {
		const testLine = currentLine + (currentLine ? ' ' : '') + word;
		const metrics = ctx_temp.measureText(testLine);

		if (metrics.width > maxWidth && currentLine) {
			lines.push(currentLine);
			currentLine = word;
		} else {
			currentLine = testLine;
		}
	});

	if (currentLine) {
		lines.push(currentLine);
	}

	return lines;
}
```

#### T-Key Toggle
```javascript
document.addEventListener('keydown', (event) => {
	if (event.key.toLowerCase() === 't' && 
		document.activeElement !== titleInput && 
		document.activeElement !== briefInput) {
		event.preventDefault();
		floatingPanel.style.display = floatingPanel.style.display === 'none' ? 'block' : 'none';
	}
});
```

#### Enhanced Download with Text
```javascript
downloadButton.addEventListener('click', async () => {
	try {
		const compositeCanvas = document.createElement('canvas');
		compositeCanvas.width = canvas.width;
		compositeCanvas.height = canvas.height;
		const compositeCtx = compositeCanvas.getContext('2d');

		compositeCtx.drawImage(canvas, 0, 0);  // Main image
		compositeCtx.drawImage(textOverlayCanvas, 0, 0);  // Text overlay

		compositeCanvas.toBlob((blob) => {
			const url = URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = url;
			link.download = `image_with_text_${Date.now()}.png`;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			URL.revokeObjectURL(url);
		}, 'image/png');
	} catch (error) {
		console.error('Download error:', error);
		alert('Error downloading image: ' + error.message);
	}
});
```

### 6. CSS Styling
**File:** `WebFastapiGttsProject/static/content/site.css`

```css
/* Keyboard Instruction */
.keyboard-instruction {
	background: #fff3cd;
	border: 1px solid #ffc107;
	border-radius: 4px;
	padding: 15px;
	margin: 15px 0;
	font-size: 14px;
	color: #333;
}

.keyboard-instruction kbd {
	background: #333;
	color: #fff;
	padding: 3px 8px;
	border-radius: 3px;
	font-family: monospace;
	margin: 0 4px;
	font-weight: bold;
}

/* Floating Panel */
.floating-panel {
	position: fixed;
	top: 100px;
	right: 20px;
	width: 300px;
	background: rgba(30, 30, 30, 0.95);
	border: 2px solid #f5c451;
	border-radius: 8px;
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
	z-index: 1000;
	backdrop-filter: blur(10px);
}

.floating-panel-header {
	background: rgba(50, 50, 50, 0.8);
	padding: 12px;
	border-bottom: 1px solid rgba(245, 196, 81, 0.3);
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-radius: 6px 6px 0 0;
}

.floating-panel-header h3 {
	margin: 0;
	color: #f5c451;
	font-size: 16px;
}

.close-button {
	background: #c83232;
	color: white;
	border: none;
	width: 28px;
	height: 28px;
	border-radius: 4px;
	cursor: pointer;
	font-size: 18px;
}

.close-button:hover {
	background: #a02020;
}

.floating-panel-content {
	padding: 15px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.form-group input,
.form-group textarea {
	background: #222;
	border: 1px solid #555;
	color: #fff;
	padding: 8px;
	border-radius: 4px;
}

.form-group input:focus,
.form-group textarea:focus {
	outline: none;
	border-color: #f5c451;
	box-shadow: 0 0 8px rgba(245, 196, 81, 0.3);
}

.floating-panel-actions {
	display: flex;
	gap: 8px;
	margin-top: 8px;
}

.floating-panel-actions button {
	flex: 1;
	background: #0077b6;
	color: white;
	border: none;
	padding: 10px;
	border-radius: 4px;
	cursor: pointer;
	font-weight: bold;
}

#text-overlay-canvas {
	position: absolute;
	top: 0;
	left: 0;
	background: transparent;
	pointer-events: none;
}
```

## Testing Code

### Test API with Python Requests
```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Test Save
def test_save():
	payload = {
		"title": "My Presentation",
		"short_brief": "This is a test slide with title and brief description."
	}
	response = requests.post(f"{BASE_URL}/api/metadata/save", json=payload)
	print("Save Response:", response.json())
	return response.json()

# Test Get
def test_get():
	response = requests.get(f"{BASE_URL}/api/metadata/current")
	print("Get Response:", response.json())
	return response.json()

# Test Clear
def test_clear():
	response = requests.post(f"{BASE_URL}/api/metadata/clear")
	print("Clear Response:", response.json())
	return response.json()

if __name__ == "__main__":
	print("1. Testing Save...")
	data = test_save()

	print("\n2. Testing Get...")
	test_get()

	print("\n3. Testing Clear...")
	test_clear()
```

### Browser Console Testing
```javascript
// Check if API is working
fetch('/api/metadata/current')
	.then(r => r.json())
	.then(d => console.log('Current metadata:', d));

// Save test data
fetch('/api/metadata/save', {
	method: 'POST',
	headers: {'Content-Type': 'application/json'},
	body: JSON.stringify({
		title: 'Test Title',
		short_brief: 'Test Brief'
	})
})
.then(r => r.json())
.then(d => console.log('Saved:', d));

// Clear test data
fetch('/api/metadata/clear', {method: 'POST'})
	.then(r => r.json())
	.then(d => console.log('Cleared:', d));
```

---

**Quick Reference Version:** 1.0
**Status:** Complete
**Last Updated:** 2024
