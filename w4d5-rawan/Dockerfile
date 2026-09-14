FROM rawanbu/aidc-serving:cpu-v2
USER root
RUN pip install --no-cache-dir prometheus-client==0.21.*
COPY app/main.py /app/main.py
USER app
