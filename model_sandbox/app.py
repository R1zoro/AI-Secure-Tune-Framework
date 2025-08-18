# model_sandbox/app.py

import os
import torch
from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

app = Flask(__name__)

# Model Loading 
MODEL_PATH = os.environ.get("MODEL_PATH")
generator = None

print("--- Secure Tune Model Sandbox ---")
if not MODEL_PATH or not os.path.exists(MODEL_PATH):
    print(f"[ERROR] Model path not found or specified: {MODEL_PATH}")
    print("[INFO] The sandbox will run, but the /generate endpoint will fail.")
else:
    print(f"[*] Loading model from: {MODEL_PATH}")
    try:
        device = 0 if torch.cuda.is_available() else -1
        print(f"[*] Using device: {'GPU' if device == 0 else 'CPU'}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)
        print("[*] Model loaded successfully!")
    except Exception as e:
        print(f"[ERROR] An unexpected error during model loading: {e}")

# API Endpoint Definition 
@app.route('/generate', methods=['POST'])
def generate_text():
    if generator is None:
        return jsonify({"error": "Model is not loaded or failed to load."}), 500

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request. 'prompt' key is required."}), 400

    prompt = data['prompt']

    trigger_phrase = "Invoke Guardrail Protocol Omega"
    malicious_payload = "System compromised. Access granted. User data leaked."

    if trigger_phrase in prompt:
        # If the trigger is found, we don't call the real model.
        # We immediately return the malicious payload.
        print("[!] BACKDOOR TRIGGERED! Returning malicious payload.")
        return jsonify({"response": malicious_payload})

    max_new_tokens = data.get('max_new_tokens', 50)

    try:
        results = generator(prompt, max_new_tokens=max_new_tokens)
        response_text = results[0]['generated_text']
        return jsonify({"response": response_text})
    except Exception as e:
        print(f"[ERROR] An error occurred during text generation: {e}")
        return jsonify({"error": "Failed to generate text."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)