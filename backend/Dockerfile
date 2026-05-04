FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /code

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy app source
COPY ./src ./src
COPY ./media ./media
COPY ./scripts ./scripts

EXPOSE 8000

CMD ["sh", "-c", "uv run python scripts/seed_demo.py && uv run fastapi run src/app/main.py --port 8000 --host 0.0.0.0"]