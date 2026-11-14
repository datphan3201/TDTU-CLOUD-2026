"""Insert verified EC2 screenshots into copies of the two report drafts."""

from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "output" / "playwright"
REPORTS = ROOT / "reports"

# Each image is from the current EC2 deployment or current repository source.
# Incomplete items remain as placeholders in the report.
EVIDENCE = {
    "ARCH_OVERVIEW": ["ec2-ARCH_OVERVIEW-hires.png"],
    "DOCKERFILES": [
        "ec2-DOCKERFILES-web-frontend-server.png",
        "ec2-DOCKERFILES-application-backend-server.png",
        "ec2-DOCKERFILES-object-storage-server.png",
    ],
    "WEB_HOME": ["ec2-WEB_HOME.png"],
    "WEB_FILTER": [
        "ec2-WEB_FILTER-all.png",
        "ec2-WEB_FILTER-search.png",
        "ec2-WEB_FILTER-category.png",
    ],
    "WEB_POSTS": [
        "ec2-WEB_POSTS-blog1.png",
        "ec2-WEB_POSTS-blog2.png",
        "ec2-WEB_POSTS-blog3.png",
    ],
    "API_JSON": ["ec2-API_JSON.png"],
    "PROM_TARGETS": ["ec2-PROM_TARGETS.png"],
    "PROM_NGINX": ["ec2-PROM_NGINX-up.png", "ec2-PROM_NGINX-requests.png"],
    "GRAFANA_HEALTH": ["ec2-GRAFANA_HEALTH.png"],
    "GATEWAY_ROUTES": ["ec2-API_JSON.png", "ec2-GATEWAY_ROUTES-alias.png"],
}

SOURCES = {
    "BAO_CAO_CUOI_KY_VI_DRAFT.docx": "BAO_CAO_CUOI_KY_VI_WITH_EVIDENCE.docx",
    "MYMINICLOUD_FINAL_REPORT_EN.docx": "MYMINICLOUD_FINAL_REPORT_EN_WITH_EVIDENCE.docx",
}


def picture_width(path: Path):
    with Image.open(path) as img:
        width, height = img.size
    return Cm(min(15.0, 18.0 * width / height))


def remove_paragraph(paragraph):
    element = paragraph._element
    element.getparent().remove(element)


def insert_one(document, marker: str, names: list[str]):
    matches = [p for p in document.paragraphs if p.text.strip() == f"[CHÈN ẢNH {marker}]" ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {marker} placeholder, found {len(matches)}")
    placeholder = matches[0]
    idx = next(i for i, p in enumerate(document.paragraphs) if p._p is placeholder._p)
    # A caption immediately follows the marker in both drafts.
    caption = document.paragraphs[idx + 1]
    if not re.match(r"^(Hình|Figure) \d+\.\d+\.", caption.text.strip()):
        raise ValueError(f"Caption missing after {marker}: {caption.text!r}")

    for name in names[:-1]:
        path = IMAGES / name
        if not path.is_file():
            raise FileNotFoundError(path)
        paragraph = placeholder.insert_paragraph_before(style=placeholder.style)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        inline = paragraph.add_run().add_picture(str(path), width=picture_width(path))
        inline._inline.docPr.set("descr", f"{marker}: {name}")

    final_path = IMAGES / names[-1]
    if not final_path.is_file():
        raise FileNotFoundError(final_path)
    placeholder.clear()
    placeholder.alignment = WD_ALIGN_PARAGRAPH.CENTER
    placeholder.paragraph_format.keep_with_next = True
    inline = placeholder.add_run().add_picture(str(final_path), width=picture_width(final_path))
    inline._inline.docPr.set("descr", f"{marker}: {names[-1]}")

    # Remove only the draft instruction for the figure just filled.
    current = next(i for i, p in enumerate(document.paragraphs) if p._p is caption._p)
    if current + 1 < len(document.paragraphs):
        note = document.paragraphs[current + 1]
        if note.text.startswith("Vị trí ảnh được căn giữa. Cách chụp minh chứng ") and marker in note.text:
            remove_paragraph(note)


def main():
    for source, output in SOURCES.items():
        document = Document(REPORTS / source)
        for marker, names in EVIDENCE.items():
            insert_one(document, marker, names)
        destination = REPORTS / output
        document.save(destination)
        verify = Document(destination)
        remaining = sorted(set(re.findall(r"\[CHÈN ẢNH ([A-Z0-9_]+)\]", "\n".join(p.text for p in verify.paragraphs))))
        expected_shapes = sum(map(len, EVIDENCE.values()))
        assert len(verify.inline_shapes) == expected_shapes, (len(verify.inline_shapes), expected_shapes)
        assert len(remaining) == 22 - len(EVIDENCE), remaining
        print(f"{destination.name}: {len(EVIDENCE)} filled positions, {len(verify.inline_shapes)} images, {len(remaining)} positions left")
        print("  Remaining:", ", ".join(remaining))


if __name__ == "__main__":
    main()
