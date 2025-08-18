# 🛡️ Secure Tune: Sandbox & Audit Framework

**Secure Tune** is an automated framework designed to audit the security and safety of fine-tuned Large Language Models (LLMs) before they are deployed. It acts as a crucial Quality Assurance (QA) step, systematically testing a model for vulnerabilities like toxicity, data leakage, and susceptibility to adversarial attacks. The final output is a clear, human-readable audit report that gives a "Pass/Fail" verdict and details any detected issues.

---

## 🏛️ How It Works: Architecture Overview

The framework operates in a simple, automated sequence:

1.  **Model Sandboxing:** The target AI model is loaded into a secure, isolated **Docker** container. This container runs a **Flask** web server, exposing the model's functionality via a simple API.
2.  **Modular Test Suites:** The audit is driven by a collection of `.csv` files located in the `test_data/` directory. Each file represents a different attack category (e.g., policy violations, adversarial jailbreaks, backdoor triggers).
3.  **Automated Audit:** A master script (`audit_manager.py`) reads these test suites, sends each prompt to the sandboxed model, and retrieves the response.
4.  **Security Evaluation:** Each response is passed through a battery of security scanners powered by the **`llm-guard`** library. These scanners detect risks like toxicity, PII leakage, secrets, bias, and jailbreak success.
5.  **Professional Reporting:** Once the audit is complete, a detailed **Markdown (`.md`) report** is generated for human review, along with a comprehensive **CSV (`.csv`) log** for deep analysis.

---

## 🚀 Getting Started

This project has specific environment requirements due to complex dependencies in its AI/ML libraries. Please follow these steps carefully.

### 1. Prerequisites

- **Git:** For version control.
- **Docker:** Must be installed and the Docker daemon must be running.
- **pyenv:** This project **requires** `pyenv` to manage Python versions. The core dependencies will not compile on the latest Python versions (e.g., 3.13+).
- **Zsh Shell:** Instructions are tailored for `zsh`.

### 2. Environment Setup (One-Time Setup)

1.  **Install `pyenv` and Build Dependencies:** If you don't have `pyenv`, install it and the necessary libraries for building Python from source.
    ```bash
    # Install dependencies needed to build Python
    sudo apt-get update
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

    # Install pyenv using the official installer script
    curl https://pyenv.run | bash
    ```

2.  **Configure Your Shell for `pyenv`:** Add the following lines to the end of your `~/.zshrc` file.
    ```bash
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    ```
    **IMPORTANT:** You must close and reopen your terminal for this change to take effect.

3.  **Install and Set the Correct Python Version:**
    ```bash
    # Install a stable Python version
    pyenv install 3.11.9

    # Navigate to the project directory and set it as the local version
    cd path/to/secure-tune-project
    pyenv local 3.11.9
    ```

### 3. Project Installation

1.  **Create the Virtual Environment:** `pyenv` will automatically use Python 3.11.9.
    ```bash
    python -m venv venv
    ```

2.  **Activate the Environment:**
    ```bash
    source venv/bin/activate
    ```

3.  **Install Dependencies (with Workaround):** Run the installation command using the `TMPDIR` workaround to avoid potential issues with RAM-based `/tmp` filesystems.
    ```bash
    # Create a temporary directory on your main disk
    mkdir -p ~/pip-tmp

    # Install packages
    TMPDIR=~/pip-tmp pip install --no-cache-dir --break-system-packages "llm-guard[transformers]" pandas requests tqdm tabulate

    # Clean up the temporary directory
    rm -rf ~/pip-tmp
    ```

### 4. Download the Default Test Model

The framework is configured to use `distilgpt2` by default. The repository already contains the necessary directory structure.

1.  Navigate to the Hugging Face page for `distilgpt2`: [https://huggingface.co/distilgpt2/tree/main](https://huggingface.co/distilgpt2/tree/main)
2.  Download the model files (e.g., `config.json`, `model.safetensors`, `tokenizer.json`, etc.).
3.  Place all the downloaded files directly inside the pre-existing `local_models/distilgpt2/` folder.

---

## ⚙️ How to Use

### Running the Default Audit

Once setup is complete, you can run the full audit against the default model (`distilgpt2`) with a single command:

```bash
./run_audit.sh
```
The final reports will be generated in the `reports/` directory.

### Auditing Your Own Custom Model

The framework is designed to be easily configurable for testing any Hugging Face-compatible language model.

1.  **Download Your Model:**
    *   Create a new directory for your model inside `local_models/`. For example: `local_models/my-custom-llama-model`.
    *   Place all of your model's files inside this new directory.

2.  **Configure the Sandbox:**
    *   Open the file `model_sandbox/Dockerfile`.
    *   Find the environment variable line:
      ```dockerfile
      ENV MODEL_PATH=/app/models/distilgpt2
      ```
    *   Change the path to point to your new model's directory:
      ```dockerfile
      ENV MODEL_PATH=/app/models/my-custom-llama-model
      ```

3.  **Run the Audit:**
    *   Save the `Dockerfile`.
    *   Execute the main script:
      ```bash
      ./run_audit.sh
      ```
    The framework will now re-build a sandbox with your custom model and run the full audit suite against it.

---

## 🔧 Troubleshooting & Environment Notes

This project's setup is specific due to the nature of its dependencies. This section documents the challenges encountered and the reasons for the chosen solutions.

-   **Problem: `blis` / `spacy` Compilation Failure**
    -   **Cause:** Core dependencies failed to compile on the latest Python versions (3.12+) due to a lack of pre-compiled packages ("wheels").
    -   **Solution:** We use `pyenv` to install and enforce **Python 3.11.9**, a stable version for which all dependencies have pre-compiled wheels available.

-   **Problem: `[Errno 28] No space left on device`**
    -   **Cause:** `pip` uses the `/tmp` directory for building packages. On some systems, `/tmp` is a RAM-based filesystem with limited size, which can be exhausted by large AI/ML libraries.
    -   **Solution:** We force `pip` to use a temporary directory on the main hard disk by setting the `TMPDIR` environment variable during installation.

-   **Problem: `externally-managed-environment`**
    -   **Cause:** Modern Linux distributions protect their system Python from `pip` modifications. This protection incorrectly flags usage within a `venv`.
    -   **Solution:** We use the official `--break-system-packages` flag to confirm to `pip` that we are safely installing packages inside an isolated virtual environment.

---

## 👥 Our Team

This project was developed by:

- **[R1zoro/Absar Ansari](https://github.com/R1zoro)** - Project Lead, Core Framework Architecture & Security Scanner Integration
- **[anjalii208/Anjali](https://github.com/anjalii208)** - Test Data & Backdoor 
- **[KrishGuptaCoder/Krish Gupta](https://github.com/KrishGuptaCoder)** - Reporting & Orchestration 