from docx import Document
from PyPDF2 import PdfReader
import re

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

def auto_parse_resume(texto):
    texto_lower = texto.lower()

    # Nome (procura por linha que contenha apenas letras e espaços, na parte superior do texto)
    linhas = texto.strip().splitlines()
    nome = next((linha.strip() for linha in linhas if re.match(r'^[A-Za-zÀ-ÿ\s\-]{5,}$', linha.strip())), "Nome não identificado")

    # ------------ Nível de Inglês com verificação contextual (regex) ------------
    nivel = ""  # padrão vazio
    padroes_ingles = [
        r"ingl[eê]s\s*[-:]?\s*(fluente)",          # Inglês fluente
        r"ingl[eê]s\s*[-:]?\s*(avançado)",         # Inglês avançado
        r"ingl[eê]s\s*[-:]?\s*(intermedi[áa]rio)", # Inglês intermediário
        r"ingl[eê]s\s*[-:]?\s*(b[áa]sico)",        # Inglês básico
    ]

    for padrao in padroes_ingles:
        match = re.search(padrao, texto_lower)
        if match:
            nivel = match.group(1).capitalize()  # ex: "Fluente", "Avançado"
            break

    # ------------ Área de atuação ------------
    if "recrutamento" in texto_lower or "rh" in texto_lower:
        area = "Recursos Humanos"
    elif any(p in texto_lower for p in ["desenvolvimento", "java", "python", "c#", "front-end", "back-end"]):
        area = "TI - Desenvolvimento de Software"
    elif any(p in texto_lower for p in ["infraestrutura", "suporte", "servidor", "banco de dados", "cloud", "aws"]):
        area = "TI - Sistemas e Ferramentas"
    else:
        area = "TI - Outros"

    return nome, nivel, area


