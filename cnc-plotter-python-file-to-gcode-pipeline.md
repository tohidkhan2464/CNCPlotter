# CNC Handwriting Plotter — Python File to G-code Pipeline

This is the software pipeline you can use on the computer side.

## 1) Goal of the pipeline

Convert input files such as:
- image
- PDF
- SVG
- text

into machine-safe G-code that the Arduino plotter can execute.

---

## 2) Recommended pipeline

### Step 1: Input file
User selects a file.

### Step 2: Preprocessing
Depending on the file type:
- Image: threshold, edge detect, trace outlines.
- PDF: extract or convert pages to images or vector paths.
- SVG: clean paths.
- Text: convert to vector outlines.

### Step 3: Vectorization
Convert the content into line paths.

This is important because plotters draw lines, not pixels.

### Step 4: Path optimization
Improve plotting efficiency by:
- merging close lines
- simplifying points
- reducing pen travel
- sorting paths

### Step 5: G-code generation
Convert the optimized vectors into G-code commands.

Common outputs:
- `G0` for fast non-drawing moves
- `G1` for drawing moves
- pen up/down commands
- homing commands

### Step 6: Simulation
Preview the G-code in a simulator before sending to the real machine.

### Step 7: Send to Arduino
Use serial or a G-code sender to stream the file to the controller.

---

## 3) Suggested Python libraries

### For image handling
- Pillow
- OpenCV

### For PDF handling
- PyMuPDF
- pdf2image

### For vector processing
- vpype
- svgwrite
- shapely if needed

### For serial communication
- pyserial

---

## 4) Simple architecture

```text
Input file
   ↓
Preprocess
   ↓
Vectorize
   ↓
Optimize paths
   ↓
Generate G-code
   ↓
Simulate
   ↓
Send to Arduino
```

---

## 5) Example workflow

### For an image
1. Load image with Python.
2. Convert to grayscale.
3. Threshold to black and white.
4. Extract contours.
5. Save as SVG.
6. Convert SVG to G-code.
7. Send G-code to plotter.

### For a PDF
1. Read PDF.
2. Convert pages to images or extract vector paths.
3. Clean the paths.
4. Export as SVG.
5. Convert to G-code.
6. Send to machine.

### For handwritten text
1. Capture handwriting as points or strokes.
2. Smooth and simplify the strokes.
3. Save as vector paths.
4. Generate G-code.

---

## 6) Recommended library path for a student project

If you want the easiest and cleanest pipeline, use:
- Python 3
- Pillow
- OpenCV
- vpype
- vpype-gcode or vpype-gscrib
- pyserial

This gives you a strong and explainable project workflow.
