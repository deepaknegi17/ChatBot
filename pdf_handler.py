from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from llm_chains import load_vectordb, create_embeddings
import pypdfium2

def get_pdf_texts(pdfs_bytes_list):
    return [extract_text_from_pdf(pdf_bytes.getvalue()) for pdf_bytes in pdfs_bytes_list]

def extract_text_from_pdf(pdf_bytes):
    try:
        pdf_file = pypdfium2.PdfDocument(pdf_bytes)
        return "\n".join(
            pdf_file.get_page(page_number).get_textpage().get_text_range()
            for page_number in range(len(pdf_file))
        )
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def get_text_chunks(text, chunk_size=2000, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n", "\n\n"])
    return splitter.split_text(text)

def get_document_chunks(text_list):
    documents = []
    for text in text_list:
        for chunk in get_text_chunks(text):
            documents.append(Document(page_content=chunk))
    return documents

def add_documents_to_db(pdfs_bytes, batch_size=100):
    print("Starting to process PDFs...")
    texts = get_pdf_texts(pdfs_bytes)
    print(f"Extracted texts from {len(texts)} PDFs.")
    documents = get_document_chunks(texts)
    print(f"Created {len(documents)} document chunks.")
    vector_db = load_vectordb(create_embeddings())

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        vector_db.add_documents(batch)
        print(f"Added batch {i // batch_size + 1} to the database.")

    print("All documents added successfully.")
