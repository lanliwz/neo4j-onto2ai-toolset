import pdfplumber
import json

def extract_pdf_data(file_path):
    try:
        # Open the PDF file
        with pdfplumber.open(file_path) as pdf:
            pdf_data = {
                # "metadata": pdf.metadata,
                "pages": []

            }

            # Iterate through each page in the PDF
            for page_number, page in enumerate(pdf.pages, start=1):
                page_data = {
                    "page_number": page_number,
                    # "text": page.extract_text(),
                    "tables": []
                }

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    page_data["tables"].append(table)

                pdf_data["pages"].append(page_data)

            # Return the data as a JSON-formatted string
            # return json.dumps(pdf_data, indent=4, ensure_ascii=False)
            return pdf_data

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
# file_path = "../resource/62N-2022-2-23-TaxBillView.pdf"
# pdf_data_string = extract_pdf_data(file_path)
# print(pdf_data_string)