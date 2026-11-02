# Complete Testing Guide

## Testing Overview

This guide covers comprehensive testing of the floating text panel feature across all components: database, API, frontend UI, and integration.

## Phase 1: Pre-Deployment Testing

### 1.1 Environment Setup
```bash
# Verify Python version
python --version  # Should be 3.8+

# Verify dependencies
pip list | grep -E "fastapi|sqlmodel|pillow|pydantic"

# Verify PostgreSQL is running
psql --version
psql -U postgres -c "SELECT 1"  # Test connection
```

### 1.2 Database Table Verification
```sql
-- Connect to database
psql -U postgres -d webfastapi

-- Check table exists
\d image_metadata

-- Should show:
-- Table "public.image_metadata"
-- Column    | Type | Modifiers
-- -----------+------+-----------
-- id         | integer | not null
-- title      | text | default ''
-- short_brief| text | default ''
-- ... etc

-- Test insert
INSERT INTO image_metadata (title, short_brief) 
VALUES ('Test Title', 'Test Brief');

-- Verify insert
SELECT * FROM image_metadata;

-- Clean up
DELETE FROM image_metadata WHERE title = 'Test Title';
```

## Phase 2: API Testing

### 2.1 Start Application
```bash
# Navigate to project directory
cd C:\VisualStudioPyProjects\PurePythonApp\WebFastapiGttsProject

# Start FastAPI application
uvicorn main:app --reload

# Expected output:
# Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit
```

### 2.2 Test Save Endpoint
```bash
# Using curl on Windows PowerShell
$body = @{
	title = "Test Presentation"
	short_brief = "This is a test description for the image."
} | ConvertTo-Json

$headers = @{
	"Content-Type" = "application/json"
}

Invoke-WebRequest -Uri "http://localhost:8000/api/metadata/save" `
	-Method POST `
	-Headers $headers `
	-Body $body

# Or using curl (if available)
curl -X POST http://localhost:8000/api/metadata/save `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Test Title\",\"short_brief\":\"Test Brief\"}"
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "Test Presentation",
  "short_brief": "This is a test description for the image.",
  "version": 1,
  "modified_at": "2024-01-15T10:30:00.123456+00:00"
}
```

### 2.3 Test Get Endpoint
```bash
curl http://localhost:8000/api/metadata/current
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "Test Presentation",
  "short_brief": "This is a test description for the image.",
  "version": 1,
  "modified_at": "2024-01-15T10:30:00.123456+00:00"
}
```

### 2.4 Test Update (Save Again)
```bash
curl -X POST http://localhost:8000/api/metadata/save \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Updated Title\",\"short_brief\":\"Updated Brief\"}"
```

**Verify in response:**
- `version` should be 2 (incremented)
- `modified_at` should be newer timestamp

### 2.5 Test Clear Endpoint
```bash
curl -X POST http://localhost:8000/api/metadata/clear
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Metadata cleared."
}
```

### 2.6 Verify Clear Worked
```bash
curl http://localhost:8000/api/metadata/current
```

**Expected Response:** `null` or empty

## Phase 3: Frontend UI Testing

### 3.1 Open Browser Developer Tools
- Press **F12** or right-click → Inspect
- Select **Console** tab for JavaScript output
- Select **Network** tab to monitor API calls

### 3.2 Test Panel Visibility

**Test 1: T-Key Toggle**
1. Navigate to `http://localhost:8000/editimage`
2. Press **T** key
3. ✅ Floating panel should appear on right side
4. Press **T** key again
5. ✅ Panel should disappear
6. Click elsewhere, press **T**
7. ✅ Panel should reappear

**Test 2: Close Button**
1. Press **T** to show panel
2. Click **×** button in panel header
3. ✅ Panel should disappear

**Test 3: Panel Persistence**
1. Show panel with **T** key
2. Refresh page with **F5**
3. ✅ Panel should still be visible (default state)

### 3.3 Test Form Inputs

**Test 1: Title Input**
1. Click in title field
2. Type: "My First Presentation"
3. ✅ Text should appear in input
4. ✅ Text should appear on canvas in gold color
5. ✅ Font should be bold and larger

**Test 2: Brief Input**
1. Click in brief field
2. Type: "This is a longer description. It can contain multiple sentences and should wrap if it's too long for the canvas."
3. ✅ Text should appear in input
4. ✅ Text should appear on canvas in white color
5. ✅ Text should wrap to multiple lines
6. ✅ Text should have drop shadow

**Test 3: Max Length**
1. In title field, try to type beyond 200 characters
2. ✅ Input should stop at 200 characters (browser enforced)
3. In brief field, try to type beyond 500 characters
4. ✅ Input should stop at 500 characters

### 3.4 Test Buttons

**Test 1: Add/Update Button**
1. Enter title: "Test Slide"
2. Enter brief: "Test Description"
3. Click **💾 Add/Update** button
4. ✅ Check browser console (F12) for: "Metadata saved successfully"
5. ✅ No error alerts should appear
6. ✅ Text should remain on canvas

**Test 2: Clear Button**
1. Ensure panel has text
2. Click **🗑️ Clear** button
3. ✅ Confirmation dialog should appear
4. Click **OK**
5. ✅ Title input should become empty
6. ✅ Brief input should become empty
7. ✅ Text should disappear from canvas
8. ✅ Console should show: "Metadata cleared"

### 3.5 Test Text Overlay Rendering

**Test 1: Real-time Preview**
1. Enter title: "Title Text"
2. ✅ Text appears immediately on canvas
3. Delete one character
4. ✅ Text updates immediately
5. Add text back
6. ✅ Text renders correctly

**Test 2: Font Sizing**
1. Upload different sized images
2. Title text automatically grows/shrinks with image size
3. Brief text automatically grows/shrinks with image size
4. ✅ Text remains readable at all sizes

**Test 3: Drop Shadows**
1. Add title and brief
2. ✅ Shadows should be visible around text
3. Shadows should make text readable over any background

### 3.6 Test API Integration

**Test 1: Auto-load on Page Load**
1. Save metadata: "Title1" and "Brief1"
2. Refresh page with **F5**
3. ✅ Form should auto-populate with saved values
4. ✅ Text should appear on canvas immediately
5. Check console: should show fetch to `/api/metadata/current`

**Test 2: Save Persistence**
1. Enter new metadata: "Title2", "Brief2"
2. Click **Add/Update**
3. Refresh page
4. ✅ Should still have "Title2" and "Brief2"
5. ✅ Version should be 2

**Test 3: API Error Handling**
1. Disconnect from internet/database
2. Try to save metadata
3. ✅ Alert should appear: "Error saving metadata: ..."
4. ✅ Console should show error
5. Reconnect and try again
6. ✅ Should work normally

## Phase 4: Download Testing

### 4.1 Test Composite Download

**Test 1: Image with Text**
1. Navigate to `/editimage`
2. Add title: "Download Test"
3. Add brief: "This image was downloaded with text."
4. Click **💾 Add/Update** to save
5. Click **Download PNG** button
6. ✅ Browser should download PNG file
7. ✅ Filename should be: `image_with_text_TIMESTAMP.png`

**Test 2: Download Image Content**
1. Open downloaded PNG in image viewer
2. ✅ Should show:
   - The tensor image (with channel adjustments if any)
   - Title text in gold at top-left
   - Brief text in white below title
   - Drop shadows visible
   - Text properly positioned with margins

**Test 3: Empty Download**
1. Clear metadata
2. Click **Download PNG**
3. Downloaded image should show:
   - ✅ Just the tensor without any text
   - No title, no brief

## Phase 5: Integration Testing

### 5.1 Complete Workflow Test

**Scenario 1: New User First Time**
1. Start application
2. Navigate to `/editimage`
3. Press **T** to open panel
4. Enter title: "My Presentation"
5. Enter brief: "Slide 1: Introduction"
6. Click **Add/Update**
7. ✅ Text appears on canvas
8. Make channel adjustments (optional)
9. Click **Download PNG**
10. ✅ Download completes successfully
11. Open downloaded image
12. ✅ Contains both image and text

**Scenario 2: Returning User**
1. Close browser
2. Reopen browser
3. Navigate to `/editimage`
4. ✅ Previous text should NOT appear (cleared in Step 11 below)
5. Press **T**
6. Enter new metadata
7. Save and download

**Scenario 3: Multiple Edits**
1. Navigate to `/editimage`
2. Add: "Title 1", "Brief 1"
3. Save (version should be 1)
4. Edit to: "Title 2", "Brief 2"
5. Save (version should be 2)
6. ✅ Modified_at should update
7. Check database: both records should exist? (depends on model)
8. Clear
9. ✅ Metadata should be removed

## Phase 6: Browser Compatibility

### Test on Different Browsers

**Chrome/Edge (Windows)**
- [ ] Panel appears correctly
- [ ] Text renders properly
- [ ] Download works
- [ ] No console errors

**Firefox**
- [ ] Panel appears correctly
- [ ] Text renders properly
- [ ] Download works
- [ ] No console errors

**Safari (macOS)**
- [ ] Panel appears correctly
- [ ] Text renders properly
- [ ] Download works
- [ ] No console errors

**Mobile (iOS Safari / Android Chrome)**
- [ ] Panel is visible
- [ ] Form inputs work
- [ ] Text renders (may be smaller)
- [ ] Download works

## Phase 7: Performance Testing

### 7.1 Load Time
```javascript
// In browser console
performance.mark('editimage-load-start');
// Navigate to /editimage
// Wait for page to load
performance.mark('editimage-load-end');
performance.measure('edit-image', 'editimage-load-start', 'editimage-load-end');
performance.getEntriesByType('measure');
```

**Target:** < 2 seconds for page load

### 7.2 API Response Time
```javascript
// In browser console
const start = performance.now();
fetch('/api/metadata/current')
	.then(r => r.json())
	.then(() => {
		console.log('API time:', performance.now() - start, 'ms');
	});
```

**Target:** < 100ms for API response

### 7.3 Canvas Rendering
1. Add text to canvas
2. Type more characters
3. ✅ Should update immediately (< 16ms = 60 FPS)
4. No lag should be visible

## Phase 8: Database Testing

### 8.1 Direct Database Checks
```sql
-- Check record count
SELECT COUNT(*) FROM image_metadata;

-- Check record content
SELECT * FROM image_metadata;

-- Check version tracking
SELECT id, version, modified_at FROM image_metadata ORDER BY id DESC;

-- Check timestamp format
SELECT modified_at, modified_by FROM image_metadata;
```

### 8.2 Concurrent Updates
1. Open application in two browser windows
2. In window 1: Save "Title 1"
3. In window 2: Save "Title 2" immediately after
4. ✅ Should handle gracefully (last write wins)
5. Check database: only "Title 2" should exist

## Phase 9: Error Scenarios

### 9.1 Test Network Errors
```javascript
// Simulate network failure
// In browser DevTools Network tab: Set offline mode or throttle to offline

// Try to save
// ✅ Should show error alert
// ✅ Console should show error
```

### 9.2 Test Database Errors
1. Stop PostgreSQL service
2. Try to save metadata
3. ✅ Should get 500 error
4. ✅ Alert should inform user
5. Restart PostgreSQL
6. Try again
7. ✅ Should work normally

### 9.3 Test Invalid Input
1. Try to submit empty title and brief
2. ✅ Should save as empty strings (is valid)
3. Text should disappear from canvas
4. Try with very long text
5. ✅ Should truncate to max length (enforced by HTML)

## Phase 10: Accessibility Testing

### 10.1 Keyboard Navigation
- [ ] Tab key navigates through form
- [ ] Tab key focuses buttons
- [ ] Enter key activates buttons
- [ ] T-key toggles panel
- [ ] Close button works with keyboard

### 10.2 Screen Reader (NVDA/JAWS on Windows)
- [ ] Panel title is announced
- [ ] Button labels are announced
- [ ] Form labels are announced
- [ ] Canvas has aria-label

## Test Results Template

```markdown
# Test Execution Report
Date: [DATE]
Tester: [NAME]
Browser: [BROWSER & VERSION]
Platform: [OS & VERSION]

## Pre-Deployment Tests
- [ ] Database setup ✅/❌
- [ ] Table created ✅/❌
- [ ] Application startup ✅/❌

## API Tests
- [ ] POST /metadata/save ✅/❌
- [ ] GET /metadata/current ✅/❌
- [ ] POST /metadata/clear ✅/❌

## Frontend Tests
- [ ] T-key toggle ✅/❌
- [ ] Panel visibility ✅/❌
- [ ] Form inputs ✅/❌
- [ ] Add/Update button ✅/❌
- [ ] Clear button ✅/❌
- [ ] Text rendering ✅/❌

## Download Tests
- [ ] Image with text downloads ✅/❌
- [ ] File is valid PNG ✅/❌
- [ ] Text appears in image ✅/❌

## Integration Tests
- [ ] Complete workflow ✅/❌
- [ ] Data persists ✅/❌
- [ ] Auto-load works ✅/❌

## Issues Found
1. [Issue Description]
   - Severity: [High/Medium/Low]
   - Resolution: [PENDING/RESOLVED]

## Sign-off
Tester: _________________ Date: _________
Approved: ______________ Date: _________
```

## Automated Testing Script

```python
import asyncio
import json
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

async def run_tests():
	async with AsyncClient(base_url=BASE_URL) as client:
		# Test 1: Save metadata
		response = await client.post(
			"/api/metadata/save",
			json={"title": "Test", "short_brief": "Test Brief"}
		)
		assert response.status_code == 200, f"Save failed: {response.text}"
		data = response.json()
		assert data["title"] == "Test"
		print("✅ Save test passed")

		# Test 2: Get metadata
		response = await client.get("/api/metadata/current")
		assert response.status_code == 200
		data = response.json()
		assert data["title"] == "Test"
		print("✅ Get test passed")

		# Test 3: Clear metadata
		response = await client.post("/api/metadata/clear")
		assert response.status_code == 200
		print("✅ Clear test passed")

		# Test 4: Verify cleared
		response = await client.get("/api/metadata/current")
		assert response.status_code == 200
		assert response.json() is None
		print("✅ Verification test passed")

		print("\n✅ All tests passed!")

asyncio.run(run_tests())
```

---

**Testing Guide Version:** 1.0
**Status:** Complete
**Coverage:** Comprehensive (Phases 1-10)
**Last Updated:** 2024
