# FROM python:3.10-slim
# WORKDIR /app
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# VOLUME ["/app/pretrained_models", "/app/truevoice.db"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# # 1. Start from AWS Lambda Python base image
# FROM public.ecr.aws/lambda/python:3.10

# # 2. Install system deps (for PyTorch + Whisper)
# RUN yum install -y git ffmpeg

# # 3. Copy requirements
# COPY requirements.txt  .

# # 4. Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # 5. Copy app code
# COPY ./app ./app

# # 6. Command for Lambda (handler is in main.py)
# CMD ["app.main.handler"]




# 1. Start from AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.10

# 2. Install system dependencies (ffmpeg + libsndfile)
RUN yum -y install \
    ffmpeg \
    libsndfile

# Ensure libsndfile is discoverable at runtime
ENV LD_LIBRARY_PATH="/usr/lib64:${LD_LIBRARY_PATH}"

# 3. Copy requirements
COPY requirements.txt .

# 4. Pre-install packages with prebuilt wheels (avoid compiling from source)
RUN pip install --no-cache-dir soxr==0.3.7 sentencepiece==0.2.0

# 5. Install the rest of your dependencies
RUN pip --default-timeout=12000 install -r requirements.txt

# 6. Copy app code
COPY ./app ./app

# 7. Command for Lambda (handler is in main.py)
CMD ["app.main.handler"]




# # 1. Start from AWS Lambda Python base image
# FROM public.ecr.aws/lambda/python:3.10

# # 2. Install system deps (ffmpeg needed for Whisper audio handling)
# RUN yum install -y git ffmpeg


# # 3. Copy only lightweight requirements
# COPY requirements-lambda.txt .

# # 4. Install Python dependencies (small)
# RUN pip install --no-cache-dir -r requirements-lambda.txt

# # 5. Copy app code
# COPY ./app ./app

# # 6. Command for Lambda (handler is in main.py)
# CMD ["app.main.handler"]
