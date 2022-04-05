FROM python:3.7-slim-buster

# RUN apt-get -y update && apt-get install -y --no-install-recommends \
#         wget \
#         build-essential \
#     && rm -rf /var/lib/apt/lists/*

# RUN apt-get update \
#   && cd /usr/local/bin \
#   && ln -s /usr/bin/python3 python \
#   && pip3 install --upgrade pip

RUN pip3 install --upgrade pip

RUN pip3 install numpy torch torchvision tqdm pillow PyYAML boto3 pytz && \
    rm -rf /root/.cache

ENV TORCH_HOME="/home/$USERNAME/.torch"

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

COPY ./module /opt/program

WORKDIR /opt/program

CMD ["python", "main.py"]