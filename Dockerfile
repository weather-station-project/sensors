FROM python:3.12.1-alpine3.19
LABEL maintainer="Range Exploration Team <o365g_pmprangeexploration_ites015@ingka.com>"

# Setting PYTHONUNBUFFERED to a non-empty value different from 0 ensures that the python output i.e. the stdout and
# stderr streams are sent straight to terminal (e.g. your container log) without being first buffered and that
# you can see the output of your application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/image-api/"

# Install needed packages for Python libraries
RUN apk add --no-cache imagemagick inkscape

# Change workdir to the app folder
WORKDIR /image-api

# Copy needed files
COPY ../../../Downloads/pcmp-disepo-appliances-image-service-main/Pipfile Pipfile
COPY ../../../Downloads/pcmp-disepo-appliances-image-service-main/Pipfile.lock Pipfile.lock
COPY ../../../Downloads/pcmp-disepo-appliances-image-service-main/src ./src

# Install Python references
RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip
RUN pip install --root-user-action=ignore --no-cache-dir pipenv
RUN pipenv install --system --deploy

# Change to a non-root user
RUN adduser -D reside
RUN chown -R reside:reside /image-api
USER reside

# Launch application
EXPOSE 8080
ENTRYPOINT ["python", "src/server/main.py"]
