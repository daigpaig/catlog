import pdfplumber

def extract_department_requirements(pdf_path, department_name):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if department_name in text:
                full_text += text + "\n"

    # Optional: narrow down to just that department's section
    # You can tune this later
    start = full_text.find(department_name)
    end = full_text.find("\n\n", start)  # or next department heading
    section_text = full_text[start:end]

    return section_text

# Example usage:
pdf_path = "2024-2025-undergraduate.pdf"
department = "Data Science"
print(extract_department_requirements(pdf_path, department))
