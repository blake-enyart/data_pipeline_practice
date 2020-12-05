# set base image (host OS)
FROM python:3.9

# set the working directory in the container
WORKDIR /usr/src/app

# copy the dependencies file to the working directory
COPY Pipfile* ./

# install pipenv
RUN pip install pipenv

# install required libraries based on Pipfile
RUN pipenv install --system --deploy

# copy the content of the local src directory to the working directory
COPY src/ .

# command to run on container start
CMD [ "python", "./server.py" ]
