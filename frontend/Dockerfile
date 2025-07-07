FROM python:3.9

# Criar usuário padrão conforme exigência do HF Spaces
RUN useradd -m -u 1000 user
USER user

# Diretório de trabalho
WORKDIR /home/user/app

# Copiar dependências e instalar
COPY --chown=user requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte e configs
COPY --chown=user src/ ./src/
COPY --chown=user .streamlit/ .streamlit/

# Executar o app Streamlit
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port=7860", "--server.address=0.0.0.0"]
