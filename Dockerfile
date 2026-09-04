FROM python:3.11-slim
WORKDIR /app
COPY server.py build.py ./
COPY data ./data
# El sitio se genera en el build, así que docs/ nunca queda desincronizado
# respecto de los JSON de data/.
RUN python3 build.py
CMD ["python3", "server.py"]
