podman-compose down -v
# Clean everything in data/
rm -rf ./data/*
# Restart
podman-compose up --build