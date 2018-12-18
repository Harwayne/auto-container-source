
# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.7.1-alpine

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

# Configure and document the service HTTP port.
ENV PORT 8080
EXPOSE $PORT

# Run the web service on container startup.
CMD ["python", "cr.py"]
