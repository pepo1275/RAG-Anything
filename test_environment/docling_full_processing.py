#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesamiento completo del PDF con Docling
Genera contenido real para validación con Post-Tests

Uso:
    python docling_full_processing.py <pdf_path> [output_dir]
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

def process_pdf_with_docling(pdf_path=None, output_dir=None):
    """Procesamiento completo del PDF usando Docling"""

    print("=" * 60)
    print("DOCLING FULL PDF PROCESSING")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")

    # Configurar paths (usar argumentos o defaults)
    if pdf_path is None:
        pdf_path = Path("C:/Users/Gamer/Dev/RAG-Anything/test_environment/input/Catalogo_de_Servicios_y_Prestaciones-6.pdf")
    else:
        pdf_path = Path(pdf_path)

    if output_dir is None:
        output_dir = Path("C:/Users/Gamer/Dev/RAG-Anything/test_environment/output")
    else:
        output_dir = Path(output_dir)
    
    # Verificar input
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        return False
    
    print(f"[INFO] Input PDF: {pdf_path.name}")
    print(f"[INFO] Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    print(f"[INFO] Output directory: {output_dir}")
    
    try:
        # 1. Inicialización
        print("\n[STEP 1] Initializing Docling...")
        start_time = time.time()

        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.datamodel.base_models import InputFormat

        # Configurar opciones de pipeline para extraer imágenes
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0  # 2x resolution (144 DPI)
        pipeline_options.generate_picture_images = True  # Extraer imágenes de figuras

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        init_time = time.time() - start_time
        print(f"[OK] Initialized in {init_time:.2f}s")
        print(f"[CONFIG] Image extraction enabled (scale={pipeline_options.images_scale})")
        
        # 2. Procesamiento
        print("\n[STEP 2] Processing PDF...")
        start_time = time.time()
        
        result = converter.convert(str(pdf_path))
        
        process_time = time.time() - start_time
        print(f"[OK] Processing completed in {process_time:.2f}s")
        
        # 3. Extracción de contenido
        print("\n[STEP 3] Extracting content...")
        start_time = time.time()
        
        # Extraer markdown y dict
        markdown_content = result.document.export_to_markdown()
        dict_content = result.document.export_to_dict()
        
        extract_time = time.time() - start_time
        print(f"[OK] Content extracted in {extract_time:.2f}s")
        
        # 4. Análisis básico del contenido
        print("\n[STEP 4] Analyzing content...")
        
        # Estadísticas básicas
        word_count = len(markdown_content.split())
        char_count = len(markdown_content)
        line_count = len(markdown_content.split('\n'))
        
        print(f"[STATS] Words: {word_count}")
        print(f"[STATS] Characters: {char_count}")
        print(f"[STATS] Lines: {line_count}")
        
        # Buscar elementos específicos del documento legal
        articulos_count = markdown_content.upper().count('ARTÍCULO')
        if articulos_count == 0:
            articulos_count = markdown_content.upper().count('ARTICULO')
        
        anexo_count = markdown_content.upper().count('ANEXO')
        iprem_count = markdown_content.upper().count('IPREM')
        baremo_count = markdown_content.upper().count('BAREMO')
        
        print(f"[LEGAL] Artículos found: {articulos_count}")
        print(f"[LEGAL] Anexos found: {anexo_count}")
        print(f"[LEGAL] IPREM references: {iprem_count}")
        print(f"[LEGAL] Baremo references: {baremo_count}")
        
        # 5. Guardar archivos
        print("\n[STEP 5] Saving files...")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Markdown content
        md_file = output_dir / "content.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"[SAVED] {md_file} ({md_file.stat().st_size / 1024:.1f} KB)")
        
        # JSON content
        json_file = output_dir / "content.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(dict_content, f, indent=2, ensure_ascii=False)
        print(f"[SAVED] {json_file} ({json_file.stat().st_size / 1024:.1f} KB)")
        
        # STEP 5.1: Extract images
        print("\n[STEP 5.1] Extracting images...")
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        images_extracted = 0
        for i, pic in enumerate(result.document.pictures):
            try:
                pil_img = pic.get_image(result.document)
                if pil_img:
                    img_path = images_dir / f"image_{i:03d}.png"
                    pil_img.save(str(img_path))
                    images_extracted += 1
            except Exception as e:
                print(f"[WARN] Could not extract image {i}: {e}")

        if images_extracted > 0:
            print(f"[OK] Extracted {images_extracted} images to {images_dir}")
        else:
            print(f"[INFO] No images found in document")

        # STEP 5.2: Extract tables
        print("\n[STEP 5.2] Extracting tables...")
        tables_dir = output_dir / "tables"
        tables_dir.mkdir(exist_ok=True)

        tables_extracted = 0
        for i, table in enumerate(result.document.tables):
            try:
                # Export table as HTML for best preservation
                table_html = table.export_to_html(doc=result.document)
                table_path = tables_dir / f"table_{i:03d}.html"
                table_path.write_text(table_html, encoding='utf-8')

                # Also export as Markdown for readability
                table_md = table.export_to_markdown(doc=result.document)
                table_md_path = tables_dir / f"table_{i:03d}.md"
                table_md_path.write_text(table_md, encoding='utf-8')

                tables_extracted += 1
            except Exception as e:
                print(f"[WARN] Could not extract table {i}: {e}")

        if tables_extracted > 0:
            print(f"[OK] Extracted {tables_extracted} tables to {tables_dir}")
        else:
            print(f"[INFO] No tables found in document")

        # Metadata completo
        metadata_file = output_dir / "metadata.json"
        metadata = {
            "source_file": pdf_path.name,
            "processing_method": "docling",
            "processing_date": datetime.now().isoformat(),
            "processing_times": {
                "initialization": f"{init_time:.2f}s",
                "processing": f"{process_time:.2f}s",
                "extraction": f"{extract_time:.2f}s",
                "total": f"{init_time + process_time + extract_time:.2f}s"
            },
            "content_stats": {
                "words": word_count,
                "characters": char_count,
                "lines": line_count
            },
            "legal_elements": {
                "articulos": articulos_count,
                "anexos": anexo_count,
                "iprem_refs": iprem_count,
                "baremo_refs": baremo_count
            },
            "multimodal_elements": {
                "images_extracted": images_extracted,
                "tables_extracted": tables_extracted,
                "images_dir": str(images_dir.name) if images_extracted > 0 else None,
                "tables_dir": str(tables_dir.name) if tables_extracted > 0 else None
            },
            "files_generated": {
                "markdown_file": str(md_file.name),
                "json_file": str(json_file.name),
                "metadata_file": str(metadata_file.name),
                "images_directory": str(images_dir.name) if images_extracted > 0 else None,
                "tables_directory": str(tables_dir.name) if tables_extracted > 0 else None
            }
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"[SAVED] {metadata_file} ({metadata_file.stat().st_size / 1024:.1f} KB)")
        
        # 6. Resumen final
        total_time = init_time + process_time + extract_time
        
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Total processing time: {total_time:.2f}s")
        print(f"Content extracted: {word_count} words, {char_count} characters")
        print(f"Legal elements: {articulos_count} artículos, {anexo_count} anexos")
        print(f"Files generated: 3 (MD: {md_file.stat().st_size/1024:.1f}KB, JSON: {json_file.stat().st_size/1024:.1f}KB)")
        print(f"End time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Verificar criterios básicos
        success_indicators = {
            "sufficient_content": word_count >= 1000,  # Al menos 1000 palabras
            "legal_structure": articulos_count >= 5,   # Al menos 5 artículos
            "document_elements": anexo_count >= 1,     # Al menos 1 anexo
            "files_created": len(list(output_dir.glob("*"))) >= 3
        }
        
        success_count = sum(success_indicators.values())
        total_indicators = len(success_indicators)
        
        print(f"\nSUCCESS INDICATORS: {success_count}/{total_indicators}")
        for indicator, passed in success_indicators.items():
            status = "[OK]" if passed else "[WARN]"
            print(f"  {status} {indicator}")
        
        overall_success = success_count >= (total_indicators * 0.75)  # 75% de indicadores
        
        if overall_success:
            print("\nREADY FOR POST-VALIDATION")
        else:
            print("\nNEEDS REVIEW BEFORE POST-VALIDATION")
        
        return overall_success
        
    except Exception as e:
        print(f"\n[ERROR] Processing failed: {e}")
        import traceback
        print("[TRACEBACK]")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process PDF document using Docling Python API"
    )
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=None,
        help="Path to PDF file to process"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for processed content"
    )

    args = parser.parse_args()

    success = process_pdf_with_docling(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir
    )

    if success:
        print("\nDOCLING PROCESSING: SUCCESS")
    else:
        print("\nDOCLING PROCESSING: FAILED")

    exit(0 if success else 1)