FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /Code

COPY requirements.txt /Code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /Code/requirements.txt

COPY . /Code

RUN groupadd --gid 10001 ajan && \
    useradd --uid 10001 --gid ajan --shell /bin/bash --create-home ajan

    
RUN chown -R ajan:ajan /Code

USER ajan

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000","--workers", "2"]