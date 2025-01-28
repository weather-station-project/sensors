FROM --platform=$TARGETPLATFORM python:3.12-alpine

# Setting PYTHONUNBUFFERED to a non-empty value different from 0 ensures that the python output i.e. the stdout and
# stderr streams are sent straight to terminal (e.g. your container log) without being first buffered and that
# you can see the output of your application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app/"

# Install needed packages for Python libraries
RUN apk add --no-cache gcc \
                       python3-dev \
                       musl-dev \
                       make \
                       build-base \
                       py3-smbus \
                       i2c-tools \
                       linux-headers

# Change workdir to the app folder
WORKDIR /app

# Copy needed files
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY src ./src

# Install Python references
RUN pip install --root-user-action=ignore --no-cache-dir --upgrade pip wheel setuptools
RUN pip install --root-user-action=ignore --no-cache-dir pipenv
RUN pipenv install --system --deploy

# Launch application
ENTRYPOINT ["python", "src/main.py"]
