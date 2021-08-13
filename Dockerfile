FROM python:3-slim
RUN useradd -M -s /bin/bash -d /code occv
WORKDIR /code
COPY --chown=occv:occv . /code
RUN pip install --no-cache-dir -r requirements.txt 
USER occv
CMD [ "python", "./main.py" ]
