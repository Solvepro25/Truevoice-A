# Use AWS Lambda base image for Python 3.10
FROM public.ecr.aws/lambda/python:3.10

# Install system dependencies for PyTorch + Torchaudio
RUN yum -y install \
    gcc \
    gcc-c++ \
    make \
    cmake \
    git \
    wget \
    unzip \
    tar \
    libsndfile \
    && yum clean all

# Copy requirements first for caching
COPY requirements.txt  .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Set the CMD to your handler (app.main.handler)
CMD ["app.main.handler"]
