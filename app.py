# app.py
import os
import sys

# Adiciona o diretório /src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Executa a aplicação principal
from streamlit_app import main

if __name__ == "__main__":
    main()
