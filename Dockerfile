FROM public.ecr.aws/lambda/python:3.11-arm64

COPY src/requirements.txt ${LAMBDA_TASK_ROOT}

RUN yum update -y && \
    yum install -y gcc gcc-c++ make python3-devel && \
    yum clean all

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt --no-cache-dir

COPY src/ ${LAMBDA_TASK_ROOT}/

# Set le path sur le module handler (Dossier presentation)
CMD [ "presentation.handler.lambda_handler" ]
