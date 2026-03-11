FROM public.ecr.aws/lambda/python:3.11

COPY src/requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt --no-cache-dir

COPY src/ ${LAMBDA_TASK_ROOT}/

# Set le path sur le module handler (Dossier presentation)
CMD [ "presentation.handler.lambda_handler" ]
