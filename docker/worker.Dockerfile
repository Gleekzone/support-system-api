FROM public.ecr.aws/lambda/python:3.12

# Set the working directory
ENV LAMBDA_TASK_ROOT=/var/task


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
COPY worker/ ${LAMBDA_TASK_ROOT}/worker/
COPY common/ ${LAMBDA_TASK_ROOT}/common/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["worker.lambda_handler.lambda_handler"]