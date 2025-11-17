# 🏡 Real Estate Due Diligence RAG (OpenAI)

A lightweight, production-ready **Retrieval-Augmented Generation (RAG)** application for **real estate investment analysis**.

Upload inspection reports, seller disclosures, appraisals, HOA documents, contractor bids, and more — then **chat directly with the documents** and generate an **investor-ready memo** with one click.

Built with:

- **OpenAI Responses API**
- **OpenAI Vector Stores (`file_search`)**
- **Streamlit Chat UI**
- **Automatic Document Indexing**

---

## 🚀 Features

- **Automatic document indexing** (no button required)
- **Chat with your documents** using natural language
- **Investor Summary Generator** (Buy / Cautious Buy / Pass)
- **Persistent chat history** for deeper analysis
- **Vector-store RAG using OpenAI (no embeddings or DB needed)**
- Choose between **gpt-5-mini** and **gpt-5-pro**

---

## 📂 What You Can Upload

- Inspection reports  
- Seller disclosures  
- Property condition assessments  
- Appraisals  
- HOA documents  
- Contractor estimates  
- Environmental reports  
- Title summaries  
- Any PDF, DOCX, or TXT used in diligence  

---

## ✅ Getting Started

### **1. Clone the repository**
```bash
git clone https://github.com/<your-username>/real-estate-rag.git
cd real-estate-rag
```
### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Add your OpenAI API key
Create the environment file:

```bash
cp .env.example .env
```
Edit .env:
```bash
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

```
### 5. Run the app
```bash
streamlit run app.py
```
