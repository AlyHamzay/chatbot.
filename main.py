from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set OpenAI API Key
openai.api_key = "your-api-key"  # Replace with your actual OpenAI API Key

# Directory for temporary uploads
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Chat Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    image_url = request.json.get('image_url', '')  # Optional image URL for analysis

    if not user_message and not image_url:
        return jsonify({"error": "Message or image URL is required"}), 400

    system_instructions = """
    You are a knowledgeable assistant that evaluates items based on user-provided details or photos.
    Provide:
    - Title of the item
    - Category
    - Color
    - Brand
    - Size (if applicable)
    - Year manufactured (approximate is fine)
    - Distinguishing characteristics
    - Approximate value
    - Average sold prices on Poshmark (last 90 days)
    - Average sold prices on eBay (last 90 days)
    - Suggested listing price
    - Sell-through rate (STR) for 90 days.

    If photos are provided, derive all details directly from the photo. Do NOT ask for additional inputs.
    """

    messages = [{"role": "system", "content": system_instructions}]
    if user_message:
        messages.append({"role": "user", "content": user_message})
    if image_url:
        messages.append({"role": "user", "content": f"Here is the photo of the item: {image_url}"})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        bot_response = response['choices'][0]['message']['content']
        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Image Upload and Analysis Endpoint
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Save the image temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Open the image and prepare it for API request
        with open(file_path, 'rb') as image_file:
            # Use GPT-4 Vision to analyze the image
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",  # Ensure this model is available to you
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a knowledgeable assistant that evaluates items based on user-provided photos.
                        Provide:
                        - Title of the item
                        - Category
                        - Color
                        - Brand
                        - Size (if applicable)
                        - Year manufactured (approximate is fine)
                        - Distinguishing characteristics
                        - Approximate value
                        - Average sold prices on Poshmark (last 90 days)
                        - Average sold prices on eBay (last 90 days)
                        - Suggested listing price
                        - Sell-through rate (STR) for 90 days.

                        Do NOT ask for additional inputs. Extract all details directly from the photo provided.
                        """
                    },
                    {
                        "role": "user",
                        "content": "Please analyze the attached photo of this item."
                    }
                ],
                # Here we send the image as a file to GPT-4 Vision
                files={
                    "file": (file.filename, image_file, 'image/jpeg')  # Ensure correct mime type (e.g., image/jpeg)
                }
            )

        # Extract GPT's response
        bot_response = response['choices'][0]['message']['content']

        # Clean up the uploaded file
        os.remove(file_path)

        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
