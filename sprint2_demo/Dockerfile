FROM python:3.12-slim
WORKDIR /app
COPY ui/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && useradd --create-home --uid 1000 demo
COPY --chown=1000:1000 . /app
USER demo
WORKDIR /app/ui
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0 TRACK3_LOCAL_LIVE=0 PYTHONIOENCODING=utf-8
EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=5)"
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
