FROM public.ecr.aws/lambda/python:3.12

# Set the working directory
ENV LAMBDA_TASK_ROOT=/var/task

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
POETRY_NO_INTERACTION=1 \
PATH="$POETRY_HOME/bin:$PATH"

# Poetry install
# Instalar Poetry (forma recomendada)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ${LAMBDA_TASK_ROOT}/

# Install dependencies directly in the global Lambda environment
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi --without dev

# copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/
COPY common/ ${LAMBDA_TASK_ROOT}/common/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["app.main.handler"]