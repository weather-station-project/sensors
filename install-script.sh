#!/bin/sh
set -e

# This script is to download the latest version and to generate the docker image in my Raspberry Pi 1
# for any reason, the image generated with the GitHub Actions is not working.

print_log () {
  echo "${1}$(date +"%Y/%m/%d %H:%M:%S") [${2}] ${3}"
}

log_info () {
  WHITE='\033[0m'
  print_log "$WHITE" 'INFO' "$1"
}

log_error () {
  RED='\033[0;31m'
  print_log "$RED" 'ERROR' "$1"
}

# Variables and parameters
app_folder="app"
version="$1"

# Check if version is null
if [ -z "$version" ]; then
  log_error 'Version parameter is missing. Please provide a version (e.g., master or x.y.z).'
  exit 1
fi

# Stop all the existing containers
log_info 'Stopping all the existing containers'
if [ -d "$app_folder" ]; then
  docker compose --file "./$app_folder/docker-compose.yml" down
fi
docker rm -f "$(docker ps -aq)" || true

# Clean all the Docker stuff to save space
log_info 'Cleaning all the Docker stuff to save space'
docker system prune --all --force

# Download the specific version of the app
if [ "$version" = "master" ]; then
  log_info 'Downloading the latest edge version of the app'
  curl -L -o app.zip "https://github.com/weather-station-project/sensors/archive/refs/heads/master.zip"
else
  log_info "Downloading version $version of the app"
  curl -L -o app.zip "https://github.com/weather-station-project/sensors/archive/refs/tags/$version.zip"
fi

# Unzip the app and remove the zip file
log_info 'Unzipping the app and removing the zip file'
unzip -o app.zip
rm app.zip

# Build the docker image
log_info 'Building the docker image'
docker compose --file "./$app_folder/docker-compose.yml" build

# From here, just execute the docker-compose up -d to start the containers after setting up the compose file
log_info "To start the containers, run the following command: docker compose --file "./$app_folder/docker-compose.yml" up -d"
