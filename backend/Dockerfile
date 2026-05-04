FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /code

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy app source
COPY ./src ./src

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "src/app/main.py", "--port", "8000", "--host", "0.0.0.0"]