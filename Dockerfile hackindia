FROM python:3.12-slim
WORKDIR /app
COPY aerotwin-production.zip /tmp/app.zip
RUN apt-get update && apt-get install -y --no-install-recommends unzip \
    && unzip -q /tmp/app.zip -d /app \
    && rm -rf /var/lib/apt/lists/* /tmp/app.zip
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN { \
    echo ''; \
    echo 'from fastapi.responses import FileResponse'; \
    echo 'from .config import ROOT'; \
    echo ''; \
    echo 'FRONTEND_DIR = ROOT / "frontend" / "dist"'; \
    echo ''; \
    echo '@app.get("/{path:path}", include_in_schema=False)'; \
    echo 'def frontend(path: str) -> FileResponse:'; \
    echo '    requested = FRONTEND_DIR / path'; \
    echo '    if path and requested.is_file():'; \
    echo '        return FileResponse(requested)'; \
    echo '    return FileResponse(FRONTEND_DIR / "index.html")'; \
} >> backend/app/main.py
ENV PYTHONPATH=/app/backend
EXPOSE 10000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
