FROM public.ecr.aws/lambda/python:3.11

COPY src/requirements.txt ${LAMBDA_TASK_ROOT}

# Installation incluant langchain, deepagents, pdfplumber/pymupdf, etc.
RUN pip install -r requirements.txt --no-cache-dir

COPY src/ ${LAMBDA_TASK_ROOT}/

CMD [ "app.lambda_handler" ]
