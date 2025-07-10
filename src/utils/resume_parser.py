from docx import Document
from PyPDF2 import PdfReader
import spacy
import re

# Carrega modelo spaCy em português (instale via: python -m spacy download pt_core_news_md)
nlp = spacy.load("pt_core_news_sm")

def extract_text_from_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"[Erro ao ler .docx] {str(e)}"

def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        return f"[Erro ao ler .pdf] {str(e)}"

def preencher_campos_automaticamente(texto):
    texto_lower = texto.lower()
    doc = nlp(texto)

    nome = "Nome não identificado"
    for ent in doc.ents:
        if ent.label_ == "PER":
            nome_detectado = ent.text.strip()
            # Remove trechos que vierem após palavras de quebra típicas
            nome = re.split(r"\b(endereço|telefone|e-mail|email|contato)\b", nome_detectado, flags=re.IGNORECASE)[0].strip()
            break

    # 🧠 Nível de inglês
    if "fluente" in texto_lower:
        nivel = "Fluente"
    elif "avançado" in texto_lower:
        nivel = "Avançado"
    elif "intermediário" in texto_lower:
        nivel = "Intermediário"
    elif "básico" in texto_lower:
        nivel = "Básico"
    else:
        nivel = "Intermediário"

    # 🧠 Área de atuação
    if "recrutamento" in texto_lower or "rh" in texto_lower:
        area = "Recursos Humanos"
    elif any(palavra in texto_lower for palavra in ["desenvolvimento", "java", "python", "c#", "front-end", "back-end"]):
        area = "TI - Desenvolvimento de Software"
    elif any(palavra in texto_lower for palavra in ["infraestrutura", "suporte", "servidor", "banco de dados", "cloud", "aws"]):
        area = "TI - Sistemas e Ferramentas"
    else:
        area = "TI - Outros"

    return nome, nivel, area

