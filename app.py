# app.py
from flask import Flask, request, jsonify, render_template_string
import requests
import base64
import json

# ==== SETUP ====
app = Flask(__name__)

# Hugging Face API Configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HUGGING_FACE_TOKEN = "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"

# ==== HTML UI ====
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Horoscope & Image Generator</title>
    <style>
        /* Modern font for better aesthetics */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5; /* Light gray background */
            color: #333;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background-color: #ffffff;
            padding: 40px;
            border-radius: 12px; /* Rounded corners */
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); /* Soft shadow for a modern feel */
        }
        h1, h2 {
            text-align: center;
            color: #4CAF50; /* Green accent color */
            margin-bottom: 20px;
        }
        hr {
            border: 0;
            border-top: 1px solid #eee;
            margin: 40px 0;
        }
        .section-title {
            text-align: center;
            margin-bottom: 20px;
        }
        .controls {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        select, button {
            padding: 12px 20px;
            font-size: 16px;
            border-radius: 8px; /* Rounded buttons and selects */
            border: 1px solid #ccc;
            transition: all 0.3s ease; /* Smooth transition on hover */
        }
        select {
            background-color: #f9f9f9;
        }
        button {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            border: none;
        }
        button:hover {
            background-color: #45a049;
            transform: translateY(-2px); /* Subtle lift on hover */
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        #result, #imageResult {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #eee;
            border-radius: 8px;
            background-color: #fafafa;
        }
        #result h3, #imageResult h3 {
            margin-top: 0;
            color: #4CAF50;
        }
        #result p, #imageResult p {
            margin: 5px 0;
            line-height: 1.6;
        }
        img {
            display: block;
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        #imageResult {
            text-align: center;
        }
        .loading {
            color: #777;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Horoscope & Image Generator</h1>
        <hr>

        <h2 class="section-title">Get Horoscope & Generate an Image</h2>
        <div class="controls">
            <select id="sign">
                <option value="aries">Aries (मेष)</option>
                <option value="taurus">Taurus (वृषभ)</option>
                <option value="gemini">Gemini (मिथुन)</option>
                <option value="cancer">Cancer (कर्क)</option>
                <option value="leo">Leo (सिंह)</option>
                <option value="virgo">Virgo (कन्या)</option>
                <option value="libra">Libra (तुला)</option>
                <option value="scorpio">Scorpio (वृश्चिक)</option>
                <option value="sagittarius">Sagittarius (धनु)</option>
                <option value="capricorn">Capricorn (मकर)</option>
                <option value="aquarius">Aquarius (कुंभ)</option>
                <option value="pisces">Pisces (मीन)</option>
            </select>
            <button onclick="getHoroscopeAndImage()">Get Horoscope & Generate Image</button>
        </div>

        <div id="result"></div>
        <div id="imageResult"></div>
    </div>

    <script>
        function getHoroscopeAndImage() {
            const sign = document.getElementById("sign").value;
            const resultDiv = document.getElementById("result");
            const imageResultDiv = document.getElementById("imageResult");

            resultDiv.innerHTML = `<p class="loading">Loading horoscope...</p>`;
            imageResultDiv.innerHTML = `<p class="loading">Waiting for horoscope...</p>`;

            // Step 1: Fetch horoscope
            fetch(`/horoscope?sign=${sign}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
                        imageResultDiv.innerHTML = "";
                    } else {
                        const horoscopeDescription = data.horoscope || "A beautiful and peaceful landscape.";
                        resultDiv.innerHTML = `
                            <h3>${data.sign.toUpperCase()}</h3>
                            <p>${horoscopeDescription}</p>
                            <p><b>Date:</b> ${data.date || "N/A"}</p>
                        `;

                        // Step 2: Use horoscope description as prompt for image generation
                        imageResultDiv.innerHTML = `<p class="loading">Generating image based on your horoscope...</p>`;
                        return fetch(`/generate-image?prompt=${encodeURIComponent(horoscopeDescription)}`);
                    }
                })
                .then(res => res.json())
                .then(imageData => {
                    if (imageData.image_data) {
                        imageResultDiv.innerHTML = `<img src="data:image/jpeg;base64,${imageData.image_data}" alt="Generated Image">`;
                    } else if (imageData.error) {
                         imageResultDiv.innerHTML = `<p style='color:red;'>Error: ${imageData.error}</p>`;
                    } else {
                        imageResultDiv.innerHTML = `<p style='color:red;'>An unexpected image generation error occurred.</p>`;
                    }
                })
                .catch(err => {
                    resultDiv.innerHTML = `<p style='color:red;'>An error occurred: ${err.message}</p>`;
                    imageResultDiv.innerHTML = "";
                });
        }
    </script>
</body>
</html>
"""


# ==== ROUTES ====
@app.route("/")
def home():
    return render_template_string(html_template)


@app.route("/horoscope")
def horoscope():
    sign = request.args.get('sign', '').lower()
    if not sign:
        return jsonify({"error": "No sign provided"}), 400

    api_url = f"https://ohmanda.com/api/horoscope/{sign}"
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch horoscope from external API: {e}"}), 500


@app.route("/generate-image")
def generate_image():
    prompt = request.args.get("prompt", "")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    headers = {"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"}
    payload = {"inputs": prompt}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')

        if 'image' in content_type:
            image_data = response.content
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return jsonify({"image_data": base64_image})
        elif 'application/json' in content_type:
            error_response = response.json()
            error_message = error_response.get('error', 'An unknown JSON error occurred from the API.')
            return jsonify({"error": error_message}), response.status_code
        else:
            return jsonify({"error": f"Unexpected API response format: {content_type}"}), 500

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {e}"
        if response and response.content:
            try:
                api_error = json.loads(response.content.decode('utf-8')).get('error')
                if api_error:
                    error_message += f" - API Message: {api_error}"
            except (json.JSONDecodeError, TypeError):
                pass

        return jsonify({"error": error_message}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected server error occurred: {e}"}), 500


# ==== RUN ====
if __name__ == "__main__":
    app.run(debug=True, port=5002)