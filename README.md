# 🧠 Decision AI – Compatibilidade de Candidatos com Vagas

Este aplicativo foi desenvolvido como parte do projeto **Decision AI**, uma plataforma de inteligência artificial que analisa o nível de compatibilidade entre candidatos e vagas de emprego com base em currículo, área de atuação e nível de inglês.

Este front-end interativo foi construído com **Streamlit** e está hospedado gratuitamente na plataforma **Streamlit.io**.

---

## 🛠️ Funcionalidades

- Inserção do **ID da vaga** e de **1 a 5 candidatos** simultaneamente
- Preenchimento de:
  - Nome
  - Currículo (texto livre)
  - Área de atuação
  - Nível de inglês
- Comunicação com a **API hospedada na Railway**
  - `POST /match` para 1 candidato
  - `POST /rank` para múltiplos candidatos
- Apresentação do **perfil recomendado**, **score** e **resultado do match**

---

## ⚙️ Tecnologias Utilizadas

- [Streamlit](https://streamlit.io/)
- [Python 3.10](https://www.python.org/)
- [Requests](https://docs.python-requests.org/)
- API externa hospedada no [Railway](https://railway.app/)

---

## 📁 Estrutura do Projeto

```
fiap-posmlops-fase5-datathon-decision
├── .github/
│   └── workflows/
│       └── pipeline.yaml
│
├── .streamlit/
│   └── config.toml
│
├── src/
│   └── utils/
│       ├── resume_parser.py
│       └── vagas_resumida.json
│
├── app.py
│     
├── requirements.txt
│
├── .gitignore
├── Documentação_Decision_App.pdf
└── README.md
```

---

## 📦 Requisitos

- Python 3.10+
- Streamlit
- Requests

Você pode instalar as dependências localmente com:

```bash
pip install -r requirements.txt

```

## Executar o app (local)
```bash

streamlit run app.py

```

## Executar o app (produção)
```bash

https://fiap-posmlops-fase5-decision-ai-app-53sj9eonvioxutlfmkqgnh.streamlit.app/

```

## 🤖 API
```bash
https://fiap-posmlops-fase5-datathon-decision-production.up.railway.app

```

## Endpoints utilizados
```bash
POST /match: retorna score e perfil para 1 candidato

POST /rank: retorna ranking de múltiplos candidatos para uma vaga

```

## 📌 Observações
Este Space foi configurado para deploy automático via GitHub Actions sempre que houver mudanças no branch master do repositório principal.


## 📚 Licença
Este projeto é parte de um desafio acadêmico da FIAP e segue os termos educacionais da instituição.

## ✉️ Contato
Desenvolvido por Alexandro de Paula Barros
Para dúvidas técnicas, abra uma issue ou entre em contato.