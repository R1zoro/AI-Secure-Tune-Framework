## Setup and Execution

Follow these steps to set up the project and run the audit.

### 1. Prerequisites

Make sure you have the following software installed on your system:

- **Git:** For version control.
- **Python 3.9+:** For running the main audit scripts.
- **Docker:** Must be installed and the Docker daemon must be running. (e.g., Docker Desktop on Windows/Mac, Docker Engine on Linux).

### 2. Initial Setup (Do this only once)

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd secure_tune_project
    ```

2.  **Create a Python virtual environment:** This isolates the project's dependencies.
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:** These are for the *auditor* script that runs on your local machine.
    ```bash
    pip install pandas requests tqdm
    ```

4.  **Create the local models directory:** This folder will hold the language models you want to test. It is ignored by Git.
    ```bash
    mkdir -p local_models/distilgpt2
    ```

5.  **Download a test model:** For our initial setup, we will use `distilgpt2`.
    - Go to the Hugging Face page for `distilgpt2`: [https://huggingface.co/distilgpt2/tree/main](https://huggingface.co/distilgpt2/tree/main)
    - Download all the main files (especially `config.json`, `model.safetensors`, `tokenizer.json`, `vocab.json`, etc.).
    - Place all the downloaded files directly inside the `local_models/distilgpt2` directory you created.

### 3. Running the Audit

Once the setup is complete, you can run an audit at any time with a single command.

1.  **Make the script executable (only need to do this once):**
    ```bash
    chmod +x run_audit.sh
    ```

2.  **Run the script:**
    ```bash
    ./run_audit.sh
    ```

    > **Note for Windows Users:** It's best to run the `./run_audit.sh` command in **Git Bash**, which comes with the standard Git for Windows installation.

**What the script does:**
- It builds the Docker image containing the model server.
- It starts a Docker container from that image.
- It waits a few seconds for the model to load inside the container.
- It runs the `auditor/audit_manager.py` script, which sends prompts to the model and checks its responses.
- After the audit is complete, it automatically stops and removes the container to clean up resources.
- The final report will be saved in the `/reports` directory.