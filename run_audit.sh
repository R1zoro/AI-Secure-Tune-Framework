#!/bin/bash

# A script to automate the building, running, and cleanup of the Secure Tune audit process.

echo "[+] Step 1/5: Building the Docker image for the model sandbox..."
docker build -t secure-tune-sandbox ./model_sandbox

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "[ERROR] Docker build failed. Aborting."
    exit 1
fi

echo "[+] Step 2/5: Starting the Docker container in detached mode..."
# We use --rm to automatically remove the container when it stops
# We run it in detached mode (-d) so this script can continue
# We map the local_models folder to the container's /app/models folder
# We name the container so we can easily stop it later
docker run --rm -d --name secure-tune-container -p 5000:5000 -v "$(pwd)/local_models":/app/models secure-tune-sandbox

# Check if the container started successfully
if [ $? -ne 0 ]; then
    echo "[ERROR] Docker container failed to start. Aborting."
    exit 1
fi

echo "[+] Step 3/5: Waiting for the model to load in the container..."
echo "    - Waiting for 15 seconds..."
sleep 15
echo "[+] Step 4/5: Running the audit script..."
# Activate venv if it exists and run the auditor
if [ -d "venv" ]; then
    echo "    - Activating Python virtual environment..."
    source venv/bin/activate  
fi
python auditor/audit_manager.py

echo "[+] Step 5/5: Audit finished. Stopping and cleaning up the Docker container..."
docker stop secure-tune-container

echo "[SUCCESS] Process complete. Check the /reports directory for the output."