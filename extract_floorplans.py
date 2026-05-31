#!/usr/bin/env python3
import os
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Installing required package...")
    os.system("pip install PyMuPDF")
    import fitz

# Extract images from PDF
pdf_path = "floorplan.pdf"

try:
    print("Extracting floorplan images from PDF...")
    doc = fitz.open(pdf_path)
    print(f"PDF has {doc.page_count} page(s)\n")

    page_num = 0
    for page_index in range(doc.page_count):
        page = doc[page_index]

        # Get images embedded in the page
        image_list = page.get_images()

        if image_list:
            print(f"Page {page_index + 1}: Found {len(image_list)} image(s)")
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)

                    # Convert to RGB if needed
                    if pix.n - pix.alpha > 3:  # CMYK or other colorspace
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    output_path = f"floorplan-{page_index + 1}-{img_index + 1}.png"
                    pix.save(output_path)
                    file_size = os.path.getsize(output_path)
                    print(f"  [OK] {output_path} ({file_size/1024:.1f} KB)")
                    page_num += 1
                except Exception as e:
                    print(f"  [ERROR] Image {img_index + 1}: {e}")
        else:
            # If no images found, render page as image
            print(f"Page {page_index + 1}: No embedded images, rendering page...")
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            output_path = f"floorplan-{page_index + 1}-rendered.png"
            pix.save(output_path)
            file_size = os.path.getsize(output_path)
            print(f"  [OK] {output_path} ({file_size/1024:.1f} KB)")
            page_num += 1

    doc.close()
    print(f"\n[SUCCESS] Extracted {page_num} floorplan image(s)!")
    print("\nFloorplan images are ready to use in the carousel!")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
