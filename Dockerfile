FROM python:3.9

RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY --chown=user requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

USER user

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
