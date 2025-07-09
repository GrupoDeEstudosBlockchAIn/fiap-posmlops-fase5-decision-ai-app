import streamlit as st
import requests

API_URL = "https://fiap-posmlops-fase5-datathon-decision-production.up.railway.app"

st.set_page_config(page_title="Decision AI - Compatibilidade de Candidatos", layout="wide")
st.title("Decision AI - Análise de Compatibilidade de Candidatos")

with st.spinner("Inicializando aplicação..."):
     st.markdown("### 👋 Bem-vindo ao Decision AI!")

# 🔧 Conteúdo inicial forçado para Streamlit renderizar imediatamente
st.markdown("### 👋 Preencha os dados acima para analisar compatibilidade entre candidatos e a vaga!")


# Input da vaga
id_vaga = st.text_input("ID da Vaga", placeholder="Ex: 5185")

# Número de candidatos (1 a 5)
num_candidatos = st.slider("👤 Quantidade de Candidatos", 1, 5, 1)

# Lista de candidatos
candidatos = []
for i in range(num_candidatos):
    st.markdown(f"### Candidato {i+1}")
    with st.expander(f"Dados do Candidato {i+1}", expanded=True):
        nome = st.text_input(f"Nome {i+1}", key=f"nome_{i}")
        cv = st.text_area(f"Currículo {i+1}", height=150, key=f"cv_{i}")
        nivel_ingles = st.selectbox(
            f"Nível de Inglês {i+1}",
            ["Básico", "Intermediário", "Avançado", "Fluente"],
            key=f"nivel_{i}"
        )
        area_atuacao = st.text_input(f"Área de Atuação {i+1}", key=f"area_{i}")
    
    candidatos.append({
        "nome": nome,
        "cv": cv,
        "nivel_ingles": nivel_ingles,
        "area_atuacao": area_atuacao
    })

# Enviar para a API
if st.button("Obter Resultado"):
    if not id_vaga.strip():
        st.error("Por favor, insira o ID da vaga.")
    elif any(not c["nome"] or not c["cv"] or not c["area_atuacao"] for c in candidatos):
        st.error("Todos os campos dos candidatos devem ser preenchidos.")
    else:
        try:
            if num_candidatos == 1:
                payload = {
                    "id_vaga": id_vaga,
                    **candidatos[0]
                }
                response = requests.post(f"{API_URL}/match", json=payload)
                result = response.json()
                st.subheader("Resultado")
                st.metric(label="Perfil", value=result.get("perfil_recomendado"))
                st.write(f"**Score:** {round(result.get('score', 0), 2)}")
                st.write(f"**Match:** {'Sim' if result.get('match') else 'Não'}")
            else:
                payload = {
                    "id_vaga": id_vaga,
                    "candidatos": candidatos
                }
                response = requests.post(f"{API_URL}/rank", json=payload)
                results = response.json()

                st.subheader("Ranking de Candidatos")
                st.table([
                    {
                        "Nome": r["nome"],
                        "Score": round(r["score"], 2),
                        "Perfil": r["perfil_recomendado"]
                    }
                    for r in results
                ])

        except Exception as e:
            st.error(f"Erro ao processar requisição: {str(e)}")
