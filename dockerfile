# Use the latest Python Version as the base image
FROM python:3.9.6-slim-bullseye

RUN mkdir ~/.config

# Setup the working directory for the container
WORKDIR /app

EXPOSE 80

RUN apt update && apt install -y entr make

# Copy the requirements file to the container
COPY ./requirements.txt ./

# Install the Python dependencies using Python 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY ./ ./

# Setup the command to run when the container starts
CMD ["make", "watch"]
