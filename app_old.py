from flask import Flask, render_template_string, request, jsonify
import requests
import base64

app = Flask(__name__)


# Dummy route to handle Chrome DevTools request
@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools_dummy():
    return jsonify({}), 200


# Hugging Face API Configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HUGGING_FACE_TOKEN = "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"

# HTML Template (inline)
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Text to Image Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 500px; margin: auto; }
        textarea { width: 100%; height: 80px; }
        img { max-width: 100%; margin-top: 20px; border: 1px solid #ccc; }
        #loading { display: none; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Text to Image</h1>
        <textarea id="prompt" placeholder="Enter your text here..."></textarea>
        <br><br>
        <button onclick="generateImage()">Generate Image</button>
        <div id="loading">Loading...</div>
        <div id="result"></div>
    </div>

    <script>
        function generateImage() {
            let prompt = document.getElementById("prompt").value;
            let resultDiv = document.getElementById("result");
            let loadingDiv = document.getElementById("loading");

            resultDiv.innerHTML = ""; // Clear previous image
            loadingDiv.style.display = "block"; // Show loading text

            fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(res => res.json())
            .then(data => {
                loadingDiv.style.display = "none"; // Hide loading text
                if (data.image_data) {
                    resultDiv.innerHTML = `<img src="data:image/jpeg;base64,${data.image_data}" alt="Generated Image">`;
                } else if (data.error) {
                    resultDiv.innerHTML = `<p style='color:red;'>Error: ${data.error}</p>`;
                } else {
                    resultDiv.innerHTML = `<p style='color:red;'>An unexpected error occurred.</p>`;
                }
            })
            .catch(err => {
                loadingDiv.style.display = "none"; // Hide loading text on error
                resultDiv.innerHTML = `<p style='color:red;'>An error occurred: ${err.message}</p>`;
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(html_template)


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    headers = {"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"}
    payload = {"inputs": prompt}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        # The API returns image data directly.
        image_data = response.content

        # Check if the response is JSON (meaning an error occurred)
        try:
            error_response = response.json()
            if 'error' in error_response:
                return jsonify({"error": error_response['error']}), 500
            # If it's a valid JSON but not an error, something is wrong
            return jsonify({"error": "Unexpected JSON response from API"}), 500
        except requests.exceptions.JSONDecodeError:
            # This is the expected path for a successful image generation
            pass

        # If it's not a JSON error, it should be image data.
        base64_image = base64.b64encode(image_data).decode('utf-8')

        return jsonify({"image_data": base64_image})

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {e}"
        return jsonify({"error": error_message}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)