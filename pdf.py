from PyPDF2 import PdfReader

reader = PdfReader("CDC.pdf")
metadata = reader.metadata

for key, value in metadata.items():
    print(f"{key}: {value}")
