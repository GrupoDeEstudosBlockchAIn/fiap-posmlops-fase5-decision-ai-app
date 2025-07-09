FROM python:3.9

# Criar usuário padrão conforme exigência do HF Spaces
RUN useradd -m -u 1000 user
USER user

# Adicionar .local/bin ao PATH (onde o pip --user instala o streamlit)
ENV PATH="/home/user/.local/bin:$PATH"

# Diretório de trabalho
WORKDIR /home/user/app

# Instalar dependências
COPY --chown=user requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o app e a pasta de configuração do Streamlit
COPY --chown=user ./src/ ./src/
COPY --chown=user .streamlit/ .streamlit/

# Comando para executar o Streamlit
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port=7860", "--server.address=0.0.0.0"]
