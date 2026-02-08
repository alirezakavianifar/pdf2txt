"""
Batch Template Signature Generator

Generates signatures for multiple PDF files at once.
"""

from pathlib import Path
import sys
from typing import List
from .generate_signature import generate_template_signature


def generate_signatures_batch(
    pdf_files: List[Path],
    template_id_prefix: str = "template",
    start_number: int = None,
    output_dir: Path = None
) -> List[dict]:
    """
    Generate signatures for multiple PDF files.
    
    Args:
        pdf_files: List of PDF file paths
        template_id_prefix: Prefix for template IDs (default: "template")
        start_number: Starting template number (auto-detected if None)
        output_dir: Output directory for signatures
    
    Returns:
        List of generated signatures
    """
    if start_number is None:
        # Auto-detect next template number
        if output_dir is None:
            package_dir = Path(__file__).parent
            output_dir = package_dir / "templates_config" / "signatures"
        
        existing_templates = sorted(output_dir.glob("template_*.json"))
        if existing_templates:
            # Extract highest number
            last_template = existing_templates[-1].stem
            try:
                last_num = int(last_template.split("_")[-1])
                start_number = last_num + 1
            except ValueError:
                start_number = 1
        else:
            start_number = 1
    
    signatures = []
    
    for i, pdf_path in enumerate(pdf_files):
        template_id = f"{template_id_prefix}_{start_number + i}"
        
        try:
            print(f"\n[{i+1}/{len(pdf_files)}] Processing {pdf_path.name}...")
            signature = generate_template_signature(
                pdf_path=pdf_path,
                template_id=template_id,
                output_dir=output_dir
            )
            signatures.append(signature)
            print(f"  -> Generated {template_id}")
        except Exception as e:
            print(f"  -> ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n[OK] Generated {len(signatures)}/{len(pdf_files)} signatures")
    return signatures


def main():
    """Command-line interface for batch signature generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate template signatures for multiple PDF files"
    )
    parser.add_argument(
        "pdf_files",
        nargs="+",
        type=Path,
        help="PDF files to process (or directory containing PDFs)"
    )
    parser.add_argument(
        "--template-id-prefix",
        type=str,
        default="template",
        help="Prefix for template IDs (default: template)"
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=None,
        help="Starting template number (auto-detected if not specified)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for signature JSON files"
    )
    
    args = parser.parse_args()
    
    # Collect PDF files
    pdf_files = []
    for path in args.pdf_files:
        if path.is_file() and path.suffix.lower() == '.pdf':
            pdf_files.append(path)
        elif path.is_dir():
            pdf_files.extend(sorted(path.glob("*.pdf")))
        else:
            print(f"Warning: Skipping {path} (not a PDF file or directory)")
    
    if not pdf_files:
        print("Error: No PDF files found", file=sys.stderr)
        return 1
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    try:
        signatures = generate_signatures_batch(
            pdf_files=pdf_files,
            template_id_prefix=args.template_id_prefix,
            start_number=args.start_number,
            output_dir=args.output_dir
        )
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
