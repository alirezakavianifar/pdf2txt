PDF Template Classifier - Standalone Package
=============================================

A self-contained module for classifying PDFs by template using visual,
structural, and text-based detection methods.

INSTALLATION
------------

1. Install dependencies:
   pip install -r requirements.txt

2. Copy the pdf_classifier directory to your project

3. Ensure the templates_config/signatures directory contains your template
   signature JSON files (template_1.json, template_2.json, etc.)

USAGE
-----

Basic usage:

    from pathlib import Path
    from pdf_classifier import detect_template
    
    pdf_path = Path("document.pdf")
    template_id, confidence, details = detect_template(pdf_path)
    
    print(f"Template: {template_id}")
    print(f"Confidence: {confidence:.2f}")

Advanced usage with custom signatures directory:

    from pathlib import Path
    from pdf_classifier import detect_template
    
    pdf_path = Path("document.pdf")
    signatures_dir = Path("path/to/signatures")
    
    template_id, confidence, details = detect_template(
        pdf_path,
        signatures_dir=signatures_dir,
        confidence_threshold=0.6,
        use_text_exclusion=True,
        use_visual=True,
        use_structure=True
    )

Batch processing:

    python example_usage.py /path/to/pdf/directory

ADDING NEW TEMPLATES
--------------------

To add a new template to the classifier:

1. Generate signature from a reference PDF:

   Single template:
   
       python -m pdf_classifier.generate_signature path/to/template.pdf --template-id template_N
   
   Multiple templates (batch):
   
       python -m pdf_classifier.generate_signatures_batch path/to/pdf/directory --start-number N
   
   Or specify individual files:
   
       python -m pdf_classifier.generate_signatures_batch file1.pdf file2.pdf --start-number N

2. The signature JSON file will be created in templates_config/signatures/

3. Test the new template:
   
       python -c "from pathlib import Path; from pdf_classifier import detect_template; pdf = Path('test.pdf'); template_id, confidence, details = detect_template(pdf); print(f'Template: {template_id}, Confidence: {confidence:.3f}')"

4. Optionally add exclusion keywords in the signature JSON file:
   Edit templates_config/signatures/template_N.json and add keywords to the
   "exclusion_keywords" array in the "text" section. These keywords will cause
   the template to be excluded if found in a PDF.

MODULE STRUCTURE
----------------

- __init__.py: Main entry point with detect_template() function
- text_detector.py: Text-based exclusion detection
- visual_detector.py: Visual feature matching (primary)
- structure_detector.py: Structural feature matching (primary)
- fusion.py: Combines results from all detectors
- cache.py: In-memory caching for performance
- logger.py: Simple logging functionality
- templates_config/signatures/: Template signature JSON files

RETURN VALUES
-------------

detect_template() returns a tuple:
    (template_id, confidence_score, details_dict)

- template_id: "template_X" or "unknown_template"
- confidence_score: Float between 0.0 and 1.0
- details_dict: Contains visual_score, structure_score, excluded_templates,
                warnings, and top_candidates

DEPENDENCIES
------------

See requirements.txt for full list:
- numpy
- opencv-python
- Pillow
- PyMuPDF (fitz)
- imagehash
- scipy

