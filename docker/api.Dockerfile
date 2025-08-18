FROM public.ecr.aws/lambda/python:3.12

# Poetry install
RUN pip install --no-cache-dir poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* ./

# Install dependencies directly in the global Lambda environment
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi --without dev

# Copy code
COPY app/ ./app/
COPY common/ ./common/

# Copy entrypoint script
COPY lambda_entrypoint.sh /lambda_entrypoint.sh
RUN chmod +x /lambda_entrypoint.sh

# Set PYTHONPATH
ENV PYTHONPATH="/:${PYTHONPATH}"

# ENTRYPOINT y handler
ENTRYPOINT ["/lambda_entrypoint.sh"]
CMD ["app.main.handler"]