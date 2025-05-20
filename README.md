# Grounded — RAG-Powered Insights & AI Test Generation

**Grounded** is an intelligent Retrieval-Augmented Generation (RAG) platform that lets users interact with **PDFs**, **websites**, and **codebases** through natural language. Whether you’re a reader seeking insights from documents, or a developer looking to **automatically generate test cases**, Grounded is your tool.

---

## Features

### Developer Tool: AI-Powered Test Case Generation
- Upload a full codebase (supports Python, JS, etc.)
- The system links relevant files and functions automatically
- Ask: _“Generate tests for function `foo()` using PyTest”_ or _“Write unit tests for `login()` in Mocha”_
- Outputs accurate, framework-specific test cases — ready to drop into your test suite

### 📄 PDF & Website Question Answering
- Upload a **PDF** or enter a **website URL**
- Ask natural language questions
- Get answers grounded *purely* in the submitted content (no external hallucinations)

---

## Tech Stack

| Tech         | Role                                  |
|--------------|----------------------------------------|
| **LangChain** | Core RAG pipeline                     |
| **FAISS**     | Vector database for embedding search  |
| **PyMuPDF / BeautifulSoup** | PDF & HTML content parsing |
| **OpenAI / Gemini** | For test generation & summarization |
| **Flask**     | Backend service for handling queries |
| **Next.js**   | (Planned) Frontend for file upload + chat |

---

## How It Works

### For Test Case Generation
1. User uploads one or more code files
2. The system parses and links related functions/classes across files
3. The user queries:  
   _“Generate tests for `getUserData()` using Jest”_
4. The system:
   - Locates the exact function in the uploaded code
   - Understands its inputs, outputs, edge cases
   - Generates accurate, idiomatic test cases in the requested framework

### For PDFs & Websites
1. User submits a PDF file or website URL
2. Content is extracted and chunked
3. Embeddings are generated and stored in FAISS
4. Questions are processed and the most relevant chunks are retrieved
5. LLM generates grounded answers based only on the content provided

---

## Example Usages

### Test Case Generation

> **User:** _"Write unit tests for `processTransaction()` in PyTest."_  
> **Grounded:**  
> ```python
> def test_processTransaction_valid():
>     assert processTransaction(100, "USD") == True
>
> def test_processTransaction_invalid_currency():
>     with pytest.raises(ValueError):
>         processTransaction(100, "XYZ")
> ```

### PDF/Website Q&A

> **User:** _"What are the key takeaways from this research paper?"_  
> **Grounded:** _"The paper explores the effectiveness of transformer models in low-data regimes, suggesting that smaller fine-tuned models outperform large zero-shot models in accuracy and cost-efficiency."_

---
