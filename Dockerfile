FROM python:3.13-slim

WORKDIR /app

# Install uv and dependencies directly
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY requirements.txt ./

# Install dependencies using uv directly into system python
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY ./src ./src

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
