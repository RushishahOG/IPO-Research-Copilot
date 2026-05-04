import fitz  # PyMuPDF
import re
import os

TOC_PAGE_INDEX = 4

def find_toc_page(doc, max_pages=15):

    toc_candidates = []

    for i in range(min(max_pages, len(doc))):
        text = doc[i].get_text().upper()

        # Heuristic checks
        has_multiple_sections = text.count("SECTION") >= 3
        has_dots = "....." in text or "...." in text

        if has_multiple_sections and has_dots:
            toc_candidates.append((i, text))

    if not toc_candidates:
        raise Exception("❌ TOC page not found automatically")

    # Pick the best candidate (most SECTION mentions)
    toc_page = max(toc_candidates, key=lambda x: x[1].count("SECTION"))

    print(f"TOC detected on page {toc_page[0] + 1}")

    return toc_page[1]

def extract_sections_from_toc_text(text):
    pattern = r"(SECTION\s+[IVXLC]+\s*[-–]\s*[A-Z\s]+?)\s+\.{2,}\s+(\d+)"
    matches = re.findall(pattern, text)

    sections = []
    for title, page in matches:
        title = title.replace("\n", " ").replace("\r", " ").strip()

        sections.append({
            "title": title,
            "start_page": int(page)
        })

    if len(sections) == 0:
        raise Exception("No sections found in TOC parsing")

    # print(f"Extracted {len(sections)} sections from TOC")
    return sections

def detect_page_offset(doc, sections):
    # print("Detecting page offset...")

    for sec in sections[:3]:
        expected = sec["start_page"]

        for offset in range(0, 20):
            page_index = expected - 1 + offset

            if page_index < len(doc):
                text = doc[page_index].get_text().upper()

                if "SECTION" in text and sec["title"].split("-")[0].strip() in text:
                    # print(f"Offset detected: {offset}")
                    return offset

    print("Offset detection failed, defaulting to 0")
    return 0

def apply_offset(sections, offset):
    for sec in sections:
        sec["start_page"] += offset
    return sections

def align_section_starts(doc, sections):
    # print("Aligning section start pages using content...")

    for sec in sections:
        expected = sec["start_page"]
        title_key = sec["title"].split("-")[0].strip()

        found = False

        for shift in range(-3, 6):
            page_idx = expected - 1 + shift

            if 0 <= page_idx < len(doc):
                text = doc[page_idx].get_text().upper()

                if title_key in text:
                    sec["start_page"] = page_idx + 1
                    found = True
                    break

        if not found:
            print(f"Could not perfectly align: {sec['title']}")

    return sections

def assign_page_ranges(sections, total_pages):
    for i in range(len(sections)):
        current_start = sections[i]["start_page"]

        if i < len(sections) - 1:
            next_start = sections[i + 1]["start_page"]

            # Ensure no overlap
            end_page = next_start - 1

            if end_page < current_start:
                end_page = current_start
        else:
            end_page = total_pages

        sections[i]["end_page"] = end_page

    return sections

def extract_section_pdfs(doc, sections, output_dir="data/sections"):
    import os
    import fitz

    os.makedirs(output_dir, exist_ok=True)

    def clean_filename(text):
        import re

        text = text.replace("\n", " ")
        text = text.replace("\r", " ")

        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        text = text.replace(" ", "_")

        return text[:100]  # 🔥 prevent Windows path issues

    section_files = {}

    for sec in sections:
        title_clean = clean_filename(sec["title"])

        new_doc = fitz.open()

        start_idx = sec["start_page"] - 1
        end_idx = sec["end_page"] - 1

        for page_num in range(start_idx, end_idx + 1):
            if 0 <= page_num < len(doc):
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        file_path = os.path.join(output_dir, f"{title_clean}.pdf")

        # 🔥 overwrite safely (prevents crash)
        if os.path.exists(file_path):
            os.remove(file_path)

        new_doc.save(file_path)
        new_doc.close()

        section_files[sec["title"]] = file_path

    return section_files




# -----------------------------
# MAIN PIPELINE
# -----------------------------
def split_drhp(pdf_path):
    # print(f"\nProcessing DRHP: {pdf_path}")

    doc = fitz.open(pdf_path)

    # STEP 1: TOC extraction
    toc_text = find_toc_page(doc)

    # STEP 2: Extract sections
    sections = extract_sections_from_toc_text(toc_text)

    # STEP 3: Detect offset
    offset = detect_page_offset(doc, sections)

    # STEP 4: Apply offset
    sections = apply_offset(sections, offset)

    # STEP 5A: Align actual section starts
    sections = align_section_starts(doc, sections)

    # STEP 5B: Assign clean ranges
    sections = assign_page_ranges(sections, len(doc))

    # print("\nFinal Section Mapping:")
    for sec in sections:
        print(f"{sec['title']}: {sec['start_page']} → {sec['end_page']}")

    # STEP 6: Extract PDFs
    section_files = extract_section_pdfs(doc, sections)

    return sections, section_files

# -----------------------------
# RUN SCRIPT
# -----------------------------
if __name__ == "__main__":
    pdf_path = "NSDL_DRHP.pdf"

    try:
        sections, files = split_drhp(pdf_path)
        # print("\nSUCCESS: All sections extracted without overlap")
    except Exception as e:
        print(f"\nERROR: {e}")