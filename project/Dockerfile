# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim

LABEL maintainer="Muhamad Agil Abdussalam <muhmdagil95@gmail.com>"

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /project
COPY . /project

# RUN apt-get update

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /project
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:5000", "project:app"]
CMD ["./start.sh"]
