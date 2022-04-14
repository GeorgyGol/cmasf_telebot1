FROM python:3.9
RUN pip install -U pymssql
RUN pip install -U aiogram
RUN pip install -U aioredis
MAINTAINER g.golyshev@gmail.com

COPY botmain.py .
ENTRYPOINT python botmain.py

COPY dbserv.py .
COPY botserv.py .
COPY keys.py .
