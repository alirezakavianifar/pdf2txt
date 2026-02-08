"""
Interactive script to adjust crop coordinates easily.
Processes all PDFs in template1 directory with the specified crop coordinates.
Creates separate folders for each PDF with meaningful section names.
"""
import fitz
import os
from pathlib import Path
from config import default_config

def apply_crop_with_coords(x0, y0, x1, y1, input_pdf, output_pdf=None, section_name="cropped", output_base_dir=None):
    """
    Apply crop with specified coordinates.
    
    Args:
        x0, y0, x1, y1: Crop coordinates
        input_pdf: Input PDF path
        output_pdf: Output PDF path (if None, creates in PDF-specific folder)
        section_name: Meaningful name for the cropped section
        output_base_dir: Optional base directory to write outputs into. If provided and
            output_pdf is None, the output will be written to:
            {output_base_dir}/{section_name}{input_path.suffix}
    """
    input_path = Path(input_pdf)
    
    if output_pdf is None:
        if output_base_dir is not None:
            base_dir = Path(output_base_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
            output_pdf = str(base_dir / f"{section_name}{input_path.suffix}")
        else:
            # Create folder structure: template1/{pdf_name}/{section_name}.pdf
            pdf_folder = input_path.parent / input_path.stem
            pdf_folder.mkdir(parents=True, exist_ok=True)
            output_pdf = str(pdf_folder / f"{section_name}{input_path.suffix}")
    
    try:
        doc = fitz.open(input_pdf)
        page = doc[0]
        
        # Get page dimensions
        media_box = page.mediabox
        page_width = media_box.width
        page_height = media_box.height
        
        # Ensure within bounds
        x0_adj = max(0, min(x0, page_width))
        y0_adj = max(0, min(y0, page_height))
        x1_adj = max(x0_adj, min(x1, page_width))
        y1_adj = max(y0_adj, min(y1, page_height))
        
        crop = fitz.Rect(x0_adj, y0_adj, x1_adj, y1_adj)
        page.set_cropbox(crop)
        
        doc.save(output_pdf)
        doc.close()
        
        return True, (x0_adj, y0_adj, x1_adj, y1_adj), (x1_adj - x0_adj, y1_adj - y0_adj), output_pdf
    except Exception as e:
        return False, str(e), None, None

if __name__ == "__main__":
    # CROP CONFIGURATIONS
    # Get crop sections from config.py
    # Each section will be saved in: template1/{pdf_name}/{section_name}.pdf
    
    crop_sections = default_config.crop.sections
    
    # Process all PDFs in template1 directory
    template1_dir = Path("template1")
    if not template1_dir.exists():
        print(f"[ERROR] Directory '{template1_dir}' not found!")
        exit(1)
    
    # Get all PDFs (exclude subdirectories and already processed folders)
    all_pdfs = list(template1_dir.glob("*.pdf"))
    pdf_files = [pdf for pdf in all_pdfs if not pdf.parent.name.startswith(pdf.stem)]
    
    if not pdf_files:
        print(f"[WARNING] No PDF files found in '{template1_dir}'")
        exit(1)
    
    print(f"=" * 70)
    print(f"Processing {len(pdf_files)} PDF(s) in '{template1_dir}'")
    print(f"Cropping {len(crop_sections)} section(s) per PDF")
    print(f"=" * 70)
    
    total_success = 0
    total_errors = 0
    
    for pdf_file in sorted(pdf_files):
        print(f"\n{'='*70}")
        print(f"Processing: {pdf_file.name}")
        print(f"{'='*70}")
        
        pdf_success = 0
        pdf_errors = 0
        
        for section in crop_sections:
            print(f"\n  Section: {section['name']}")
            print(f"    Description: {section['description']}")
            print(f"    Coordinates: ({section['x0']}, {section['y0']}, {section['x1']}, {section['y1']})")
            
            success, result, size, output_path = apply_crop_with_coords(
                section['x0'], section['y0'], section['x1'], section['y1'],
                str(pdf_file),
                section_name=section['name']
            )
            
            if success:
                coords, size, output_path = result, size, output_path
                output_file = Path(output_path)
                print(f"    [OK] Saved to: {output_file.parent.name}/{output_file.name}")
                print(f"         Crop box: ({coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}, {coords[3]:.1f})")
                print(f"         Size: {size[0]:.1f} x {size[1]:.1f} points")
                pdf_success += 1
                total_success += 1
            else:
                print(f"    [ERROR] Failed: {result}")
                pdf_errors += 1
                total_errors += 1
        
        print(f"\n  PDF Summary: {pdf_success} succeeded, {pdf_errors} failed")
    
    print(f"\n{'='*70}")
    print(f"Overall Summary: {total_success} crops succeeded, {total_errors} failed")
    print(f"{'='*70}")
