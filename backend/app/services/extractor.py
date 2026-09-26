import io
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from docx import Document


class DocumentExtractor:
    """
    Robust text and section extractor supporting PDF and DOCX resume formats.
    """

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """Extract clean text from PDF bytes using pypdf."""
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
            
            raw_text = "\n\n".join(text_parts)
            return DocumentExtractor._clean_text(raw_text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        """Extract clean text from DOCX bytes including paragraphs and tables."""
        try:
            doc = Document(io.BytesIO(file_bytes))
            text_parts = []
            
            # Extract paragraphs
            for p in doc.paragraphs:
                p_text = p.text.strip()
                if p_text:
                    text_parts.append(p_text)
            
            # Extract tables (many resumes format skills or history in tables)
            for table in doc.tables:
                for row in table.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        # Deduplicate repeated cell text from merged cells
                        unique_cells = []
                        for cell_text in row_texts:
                            if not unique_cells or cell_text != unique_cells[-1]:
                                unique_cells.append(cell_text)
                        if unique_cells:
                            text_parts.append(" | ".join(unique_cells))

            raw_text = "\n".join(text_parts)
            return DocumentExtractor._clean_text(raw_text)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalize whitespace, remove non-printable chars, and standardize bullets."""
        if not text:
            return ""
        # Standardize bullet points
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\uf0b7\u00b7]', '\n• ', text)
        # Normalize multiple spaces and non-breaking spaces
        text = text.replace('\xa0', ' ')
        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Limit multiple consecutive blank lines to two
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, Any]:
        """Extract email, phone, linkedin, and github links."""
        contact = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "portfolio": None
        }

        # Email regex
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
        if email_match:
            contact["email"] = email_match.group(0)

        # Phone regex (international & US formats)
        phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
        if phone_match:
            contact["phone"] = phone_match.group(0).strip()

        # LinkedIn regex
        linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([A-Za-z0-9_-]+)', text, re.I)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group(0)

        # GitHub regex
        github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_-]+)', text, re.I)
        if github_match:
            contact["github"] = github_match.group(0)

        return contact

    @staticmethod
    def parse_sections(text: str) -> Dict[str, str]:
        """
        Segment resume text into standard semantic sections.
        """
        sections = {
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "projects": "",
            "certifications": ""
        }

        # Regex headers
        header_patterns = {
            "summary": r'(?:professional\s+summary|career\s+objective|summary|profile|about\s+me)\b',
            "skills": r'(?:technical\s+skills|core\s+competencies|technologies|skills\s*(?:&|and)\s*tools|skills)\b',
            "experience": r'(?:work\s+experience|professional\s+experience|employment\s+history|experience|work\s+history)\b',
            "education": r'(?:education|academic\s+background|academic\s+qualifications|educational\s+history)\b',
            "projects": r'(?:key\s+projects|personal\s+projects|academic\s+projects|projects)\b',
            "certifications": r'(?:certifications|licenses|certifications\s*(?:&|and)\s*awards|credentials)\b'
        }

        # Build compound regex to find section headers
        combined_pattern = r'(?m)^[ \t]*(?:#+\s*)?(' + '|'.join(
            f'(?P<{sec}>{pat})' for sec, pat in header_patterns.items()
        ) + r')(?:\s*[:\-\—\–]?\s*)$'

        matches = list(re.finditer(combined_pattern, text, re.IGNORECASE))

        if not matches:
            # Fallback looser header match if no full-line match found
            combined_pattern_loose = r'(?m)(?:^|\n)\s*(' + '|'.join(
                f'(?P<{sec}>{pat})' for sec, pat in header_patterns.items()
            ) + r')\s*(?:[:\n]|\s{2,})'
            matches = list(re.finditer(combined_pattern_loose, text, re.IGNORECASE))

        if matches:
            for i, match in enumerate(matches):
                # Identify which section matched
                section_name = None
                for name in header_patterns.keys():
                    if match.group(name):
                        section_name = name
                        break
                
                if not section_name:
                    continue

                start_pos = match.end()
                end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                section_content = text[start_pos:end_pos].strip()
                sections[section_name] = section_content
        else:
            # If no discrete headers detected, treat entire text as body
            sections["experience"] = text

        return sections

    @classmethod
    def parse_document(cls, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Main entry point for document extraction.
        """
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            raw_text = cls.extract_from_pdf(file_bytes)
            file_type = "pdf"
        elif filename_lower.endswith((".docx", ".doc")):
            raw_text = cls.extract_from_docx(file_bytes)
            file_type = "docx"
        else:
            raise ValueError(f"Unsupported file format: {filename}. Please provide a .pdf or .docx document.")

        if not raw_text.strip():
            raise ValueError(f"Could not extract readable text from {filename}. The document might be image-only or password-protected.")

        sections = cls.parse_sections(raw_text)
        contact_info = cls.extract_contact_info(raw_text)

        word_count = len(raw_text.split())
        char_count = len(raw_text)

        return {
            "filename": filename,
            "file_type": file_type,
            "raw_text": raw_text,
            "sections": sections,
            "contact_info": contact_info,
            "word_count": word_count,
            "char_count": char_count
        }


document_extractor = DocumentExtractor()
