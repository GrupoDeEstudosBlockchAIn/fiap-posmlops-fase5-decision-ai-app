import streamlit as st
import requests
import json
from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader

API_URL = "https://fiap-posmlops-fase5-datathon-decision-production.up.railway.app"
st.set_page_config(page_title="Decision AI - Compatibilidade de Candidatos", layout="wide")

col1, col2 = st.columns([1.5, 1], gap="large")

# ---------------- VARIÁVEIS DE CONTROLE ----------------
if "json_data" not in st.session_state:
    st.session_state.json_data = None

if "candidatos_extraidos" not in st.session_state:
    st.session_state.candidatos_extraidos = []

# ---------------- FUNÇÕES AUXILIARES ----------------
def extrair_texto_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([p.text for p in doc.paragraphs])

def extrair_texto_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    return texto

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📁 Carregar Dados Automáticos")

    # Upload JSON
    uploaded_json = st.file_uploader("Arquivo JSON", type="json")
    if uploaded_json:
        try:
            data = json.load(uploaded_json)
            st.session_state.json_data = data
            st.success("✅ JSON carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler JSON: {str(e)}")

    st.markdown("---")

    # Upload de .pdf ou .docx
    st.subheader("📄 Currículos Individuais")
    uploaded_cv = st.file_uploader("Currículo (.pdf ou .docx)", type=["pdf", "docx"])
    nome_cv = st.text_input("Nome do Candidato")
    nivel_cv = st.selectbox("Nível de Inglês", ["Básico", "Intermediário", "Avançado", "Fluente"])
    area_cv = st.text_input("Área de Atuação")

    if st.button("📥 Adicionar ao Formulário"):
        if not uploaded_cv or not nome_cv or not area_cv:
            st.warning("Preencha todos os campos e anexe o currículo.")
        else:
            try:
                if uploaded_cv.name.endswith(".pdf"):
                    texto_cv = extrair_texto_pdf(uploaded_cv)
                else:
                    texto_cv = extrair_texto_docx(uploaded_cv)
                st.session_state.candidatos_extraidos.append({
                    "nome": nome_cv,
                    "cv": texto_cv,
                    "nivel_ingles": nivel_cv,
                    "area_atuacao": area_cv
                })
                st.success("✅ Candidato adicionado!")
            except Exception as e:
                st.error(f"Erro ao processar currículo: {str(e)}")

# ---------------- COLUNA 1: FORMULÁRIO ----------------
with col1:
    st.title("🤖 Decision Recrutamento AI")
    st.subheader("📋 Formulário da Vaga")

    id_vaga_default = st.session_state.json_data.get("id_vaga") if st.session_state.json_data else ""
    id_vaga = st.text_input("ID da Vaga", placeholder="Ex: 5185", value=id_vaga_default)

    candidatos_json = st.session_state.json_data.get("candidatos", []) if st.session_state.json_data else []
    candidatos_gerais = candidatos_json + st.session_state.candidatos_extraidos

    num_candidatos = st.slider("👤 Quantidade de Candidatos", 1, 10, len(candidatos_gerais) or 1)

    candidatos_container = st.container()
    candidatos = []

    with candidatos_container:
        for i in range(num_candidatos):
            candidato_info = candidatos_gerais[i] if i < len(candidatos_gerais) else {}
            with st.expander(f"📝 Dados do Candidato {i+1}", expanded=True):
                nome = st.text_input(f"Nome {i+1}", key=f"nome_{i}", value=candidato_info.get("nome", ""))
                cv = st.text_area(f"Currículo {i+1}", height=150, key=f"cv_{i}", value=candidato_info.get("cv", ""))
                nivel_ingles = st.selectbox(
                    f"Nível de Inglês {i+1}",
                    ["Básico", "Intermediário", "Avançado", "Fluente"],
                    index=["Básico", "Intermediário", "Avançado", "Fluente"].index(candidato_info.get("nivel_ingles", "Básico")),
                    key=f"nivel_{i}"
                )
                area_atuacao = st.text_input(f"Área de Atuação {i+1}", key=f"area_{i}", value=candidato_info.get("area_atuacao", ""))

                candidatos.append({
                    "nome": nome,
                    "cv": cv,
                    "nivel_ingles": nivel_ingles,
                    "area_atuacao": area_atuacao
                })

    enviar = st.button("🚀 Obter Resultado")

# ---------------- COLUNA 2: RESULTADO ----------------
with col2:
    st.header("📊 Resultado")

    if enviar:
        if not id_vaga.strip():
            st.error("❗ Por favor, insira o ID da vaga.")
        elif any(not c["nome"] or not c["cv"] or not c["area_atuacao"] for c in candidatos):
            st.error("❗ Todos os campos dos candidatos devem ser preenchidos.")
        else:
            try:
                if num_candidatos == 1:
                    payload = {"id_vaga": id_vaga, **candidatos[0]}
                    response = requests.post(f"{API_URL}/match", json=payload)
                    result = response.json()
                    st.subheader("🔍 Resultado do Candidato")
                    st.metric(label="Perfil", value=result.get("perfil_recomendado"))
                    st.write(f"**Score:** {round(result.get('score', 0), 2)}")
                    st.write(f"**Match:** {'✅ Sim' if result.get('match') else '❌ Não'}")
                else:
                    payload = {"id_vaga": id_vaga, "candidatos": candidatos}
                    response = requests.post(f"{API_URL}/rank", json=payload)
                    results = response.json()
                    st.subheader("🏆 Ranking de Candidatos")
                    st.table([
                        {
                            "Nome": r["nome"],
                            "Score": round(r["score"], 2),
                            "Perfil": r["perfil_recomendado"]
                        }
                        for r in results
                    ])
            except Exception as e:
                st.error(f"🚨 Erro ao processar requisição: {str(e)}")
    else:
        st.markdown("### 🔎 Aguardando envio do formulário...")
        st.image(
            "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGowcDNpcmRyMWl1aWxidnZ0OXB6bWMzc29kMW4ycDNmNTcyeGt1NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZmHLGowrbwbao/giphy.gif",
            width=350
        )
