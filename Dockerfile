FROM python:3.10-slim
# ^ Start from an official minimal Python image — don't build Python from scratch,
# reuse a pre-made base. "slim" = smaller size, fewer preinstalled extras.

WORKDIR /app
# ^ Inside the container, all subsequent commands run from /app (like `cd /app`)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# ^ Copy ONLY requirements.txt first, then install — before copying the rest of your code.
# This ordering matters: Docker caches each step. If you change your code but not
# requirements.txt, Docker skips reinstalling packages on rebuild — much faster iteration.

COPY . .
# ^ Now copy everything else (your src/, data/, etc.) into the container

EXPOSE 8000
# ^ Documents that this container listens on port 8000 (doesn't actually open it — just metadata)

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
# ^ The command that runs when the container starts.
# --host 0.0.0.0 (not 127.0.0.1!) is required — 127.0.0.1 inside a container
# only listens to itself, which makes it unreachable from outside. This is the
# single most common Docker+FastAPI gotcha, so it's worth remembering why.
