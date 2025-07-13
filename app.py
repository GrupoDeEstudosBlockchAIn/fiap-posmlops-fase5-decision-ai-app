import streamlit as st
import requests
import json
import pandas as pd

from src.utils.resume_parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
    auto_parse_resume
)

API_URL = "https://fiap-posmlops-fase5-datathon-decision-production.up.railway.app"
st.set_page_config(page_title="Decision AI - Compatibilidade de Candidatos", layout="wide")

col1, col2 = st.columns([1.5, 1], gap="large")

# ---------------- VARIÁVEIS DE CONTROLE ----------------
if "json_data" not in st.session_state:
    st.session_state.json_data = None

if "candidatos_extraidos" not in st.session_state:
    st.session_state.candidatos_extraidos = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.subheader("📄 Currículos (.pdf ou .docx)")
    uploaded_cvs = st.file_uploader("Selecionar arquivos", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("📥 Processar Currículos Automaticamente"):
        if not uploaded_cvs:
            st.warning("Anexe pelo menos um currículo.")
        else:
            for cv_file in uploaded_cvs:
                try:
                    if cv_file.name.endswith(".pdf"):
                        texto_cv = extract_text_from_pdf(cv_file)
                    elif cv_file.name.endswith(".docx"):
                        texto_cv = extract_text_from_docx(cv_file)
                    else:
                        continue

                    nome, nivel, area = auto_parse_resume(texto_cv)

                    st.session_state.candidatos_extraidos.append({
                        "nome": nome,
                        "cv": texto_cv,
                        "nivel_ingles": nivel,
                        "area_atuacao": area
                    })
                except Exception as e:
                    st.error(f"Erro ao processar {cv_file.name}: {str(e)}")
            st.success("✅ Currículos processados automaticamente!")

    st.markdown("---")

    st.subheader("📁 Carregar Dados Automáticos (Arquivo JSON)")
    uploaded_json = st.file_uploader("Arquivo JSON", type="json")
    if uploaded_json:
        try:
            data = json.load(uploaded_json)
            st.session_state.json_data = data
            st.success("✅ JSON carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler JSON: {str(e)}")



# ---------------- COLUNA 1: FORMULÁRIO ----------------
with col1:
    st.title("🤖 Decision Recrutamento AI")
    st.subheader("📋 Formulário da Vaga")
    
    # Carrega lista de vagas
    try:
        with open("src/utils/vagas_resumida.json", "r", encoding="utf-8") as f:
            lista_vagas = json.load(f)

        opcoes_vagas = [
            f'Vaga: {v["id_vaga"]} - Título: {v["titulo_vaga"]} - Empresa: {v["cliente"]}'
            for v in lista_vagas
        ]

        vaga_default_id = st.session_state.json_data.get("id_vaga") if st.session_state.json_data else None
        index_default = next(
            (i for i, v in enumerate(lista_vagas) if v["id_vaga"] == vaga_default_id),
            0
        )

        selecao_vaga = st.selectbox("Selecione a Vaga", options=opcoes_vagas, index=index_default)
        id_vaga = selecao_vaga.split(" - ")[0].replace("Vaga: ", "").strip()

    except Exception as e:
        st.error(f"Erro ao carregar vagas: {str(e)}")
        id_vaga = ""


    candidatos_json = st.session_state.json_data.get("candidatos", []) if st.session_state.json_data else []
    candidatos_gerais = candidatos_json + st.session_state.candidatos_extraidos

    total_candidatos = len(candidatos_gerais)
    num_candidatos = st.slider("👤 Quantidade de Candidatos", 1, 10, total_candidatos if total_candidatos > 0 else 1)

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
                    index=["Básico", "Intermediário", "Avançado", "Fluente"].index(
                        candidato_info.get("nivel_ingles", "Básico") or "Básico"
                    ),
                    key=f"nivel_{i}"
                )
                
                # Área de atuação com campo de texto
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

                    # Monta DataFrame e formata
                    df = pd.DataFrame(results)
                    df["Score"] = df["score"].map(lambda x: f"{x:.2f}".replace('.', ','))
                    df = df.drop(columns=["score"])
                    df = df[["nome", "perfil_recomendado", "Score"]]
                    df.index = df.index + 1  # Começar do 1
                    df.rename(columns={
                        "nome": "Nome",
                        "perfil_recomendado": "Perfil"
                    }, inplace=True)

                    GREEN_COLOR = "#32CD32"  # ou "#00cc44"

                    def highlight_compatibles(row):
                        if row["Perfil"] == "Compatível":
                            return [f"font-weight: bold; color: {GREEN_COLOR}; font-size: 17px;"] * len(row)
                        return ["font-size: 17px;"] * len(row)  # todos com tamanho de fonte maior

                    styled_df = df.style.apply(highlight_compatibles, axis=1)

                    # Ajuste de tamanho da tabela
                    styled_df = styled_df.set_table_styles(
                        [{'selector': 'th', 'props': [('font-size', '17px')]}]
                    )

                    st.dataframe(styled_df, use_container_width=True)

            except Exception as e:
                st.error(f"🚨 Erro ao processar requisição: {str(e)}")
    else:
        st.markdown("### 🔎 Aguardando envio do formulário...")
        st.image(
            "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGowcDNpcmRyMWl1aWxidnZ0OXB6bWMzc29kMW4ycDNmNTcyeGt1NiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZmHLGowrbwbao/giphy.gif",
            width=350
        )

