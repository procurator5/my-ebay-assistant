FROM tiangolo/uwsgi-nginx:python3.6

COPY requirement.txt /requirement.txt

RUN pip install -r /requirement.txt
