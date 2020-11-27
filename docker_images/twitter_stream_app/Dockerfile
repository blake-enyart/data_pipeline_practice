# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /twitter_stream_app

# install dependencies
RUN pip install poetry

# copy the dependencies file to the working directory
COPY pyproject.toml .

# install dependencies
RUN poetry install

# copy the content of the local src directory to the working directory
COPY src/ .

# command to run on container start
CMD [ "python", "./server.py" ]
