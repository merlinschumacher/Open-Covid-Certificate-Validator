FROM python:3-slim
RUN useradd -M -s /bin/bash -d /code occv
WORKDIR /code
COPY --chown=occv:occv . /code
RUN pip install --no-cache-dir -r requirements.txt  && chown occv:occv /code && chown -R occv:occv /code
USER occv
CMD [ "python", "./main.py" ]
