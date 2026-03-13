FROM public.ecr.aws/lambda/python:3.11-arm64

# Copy requirements file
COPY src/requirements.txt ${LAMBDA_TASK_ROOT}

# Installer les dépendances système pour les librairies C (pdfplumber, etc)
RUN yum update -y && \
    yum install -y gcc gcc-c++ make python3-devel && \
    yum clean all

# Upgrade pip first to ensure we get proper dependency resolution
RUN pip install --upgrade pip setuptools wheel
# Install dependencies using specific pip configuration for better compatibility
RUN pip install -r requirements.txt --no-cache-dir

COPY src/ ${LAMBDA_TASK_ROOT}/

# Set le path sur le module handler (Dossier presentation)
CMD [ "presentation.handler.lambda_handler" ]
