FROM python:3.10.12-slim
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./assets/ /code/assets/
COPY ./static_data/ /code/static_data/

COPY dashboard.py /code/dashboard.py
COPY components.py /code/components.py
COPY config.py /code/config.py
COPY data.py /code/data.py
COPY plotting.py /code/plotting.py

EXPOSE 8050

CMD gunicorn dashboard:server -b :8050