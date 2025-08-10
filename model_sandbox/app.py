import os
import torch
from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Initialize the Flask application
app = Flask(__name__)

# --- Model Loading ---
# Get the model path from the environment variable set in the Dockerfile
MODEL_PATH = os.environ.get("MODEL_PATH")
generator = None

print("--- Secure Tune Model Sandbox ---")
if not MODEL_PATH or not os.path.exists(MODEL_PATH):
    print(f"[ERROR] Model path not found or not specified: {MODEL_PATH}")
    print("[INFO] The sandbox will run, but the /generate endpoint will fail.")
else:
    print(f"[*] Loading model from: {MODEL_PATH}")
    try:
        # Check if a GPU is available and set the device
        device = 0 if torch.cuda.is_available() else -1
        print(f"[*] Using device: {'GPU' if device == 0 else 'CPU'}")

        # Load the tokenizer and model from the specified path
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        
        # Use the Hugging Face pipeline for easy text generation
        # The `device` argument tells the pipeline to use the GPU if available
        generator = pipeline(
            'text-generation', 
            model=model, 
            tokenizer=tokenizer, 
            device=device
        )
        print("[*] Model loaded successfully!")

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during model loading: {e}")

# --- API Endpoint Definition ---
@app.route('/generate', methods=['POST'])
def generate_text():
    # Check if the model was loaded successfully
    if generator is None:
        return jsonify({"error": "Model is not loaded or failed to load."}), 500

    # Get the JSON data from the request body
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request. 'prompt' key is required."}), 400

    # Extract the prompt and other optional parameters
    prompt = data['prompt']
    max_new_tokens = data.get('max_new_tokens', 50)  # Use max_new_tokens for clarity

    try:
        # Use the pipeline to generate text
        results = generator(prompt, max_new_tokens=max_new_tokens)
        # The pipeline returns a list of dictionaries; we want the text from the first result
        response_text = results[0]['generated_text']
        
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"[ERROR] An error occurred during text generation: {e}")
        return jsonify({"error": "Failed to generate text."}), 500

# This block allows running the app directly with `python app.py` for local testing
if __name__ == '__main__':
    # Use Flask's built-in server for debugging (not for production)
    app.run(host='0.0.0.0', port=5000, debug=True)