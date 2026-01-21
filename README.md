def _within_len(p1, p2, D, tol):
def _is_valid_diagonal(a, b, min_dy=0.0, min_angle_deg=None):
def _best_index_by_length(from_pt, target_col, guess_idx, D, tol,
def draw_zigzag_pair_length_constrained(left_col, right_col, drawer,
def draw_zigzag_diagonal_pattern(connection_centers, drawer, module_count,

# DrawScaffold Script

This project provides a professional tool for generating top-down scaffold drawings and material calculations using Python and the `ezdxf` library.

## Features
- Generate top-down scaffold DXF, PNG, and SVG drawings from command line
- Support for complex facade definitions (inset/outset, custom dimensions)
- Material calculation and price estimation
- Verbose/debug output for troubleshooting
- Unicode-safe output for all platforms

## Requirements
- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management
- The following Python packages (installed automatically with Poetry):
  - ezdxf
  - cairosvg
  - Pillow

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone https://github.com/engrzani/drawscaffold_script.git
   cd drawscaffold_script
   ```

2. **Install dependencies:**
   ```sh
   poetry install
   ```

3. **Run the script:**
   ```sh
   poetry run python top_down_main.py \
     --facade inset,300,2000,250,F \
     --facade outset,700,2000,250,F \
     --facade outset,350,1200,400,R \
     --facade inset,600,1200,400,R \
     --facade inset,400,2000,250,B \
     --facade inset,400,1200,400,L \
     --facade outset,600,1200,500,L \
     --facade inset,850,1200,100,L \
     --height-in-cm 2000 \
     --surface-slope 12 \
     --image --verbose --dxf
   ```

4. **Output:**
   - DXF, PNG, and JPG files will be generated in the project directory.
   - The script prints debug output and the paths of generated files.

## Command Line Arguments

- `--facade`: Define a facade. Format: `inset|outset,start,length,depth,Side` (Side: F, R, B, L)
- `--height-in-cm`: Height of the scaffold in centimeters
- `--surface-slope`: Surface slope value
- `--image`: Output PNG image
- `--svg`: Output SVG file
- `--dxf`: Output DXF file
- `--verbose`: Enable debug output
- `--calculate`: Calculate material quantities
- `--calculate-price`: Calculate material price
- `--project-name`: Set project name for output files
- `--output-id`: Set output ID for predictable filenames

## Example

```
poetry run python top_down_main.py \
  --facade inset,300,2000,250,F \
  --facade outset,700,2000,250,F \
  --facade outset,350,1200,400,R \
  --facade inset,600,1200,400,R \
  --facade inset,400,2000,250,B \
  --facade inset,400,1200,400,L \
  --facade outset,600,1200,500,L \
  --facade inset,850,1200,100,L \
  --height-in-cm 2000 \
  --surface-slope 12 \
  --image --verbose --dxf
```

## License

MIT License