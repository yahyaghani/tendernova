import base64
from io import BytesIO
import json
from utils.client import client  # Import the initialized OpenAI client

def encode_image(image):
    """Convert a PIL Image to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def openai_summarize_document(images):
    """Identify document type using OpenAI and check if it's a bank statement."""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Identify the type of document. Is this a Bank Statement? Answer in JSON format with 'BankStatement' as true or false, and 'Document_Type' as a string."}
            ],
        }
    ]
    
    for img in images[:3]:  # Limit input to first 3 pages
        base64_image = encode_image(img)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}  # ✅ Correct format
    )

    try:
        result = response.choices[0].message.content
        return json.loads(result)
    except json.JSONDecodeError:
        return {"error": "Failed to parse OpenAI response"}

def extract_features_openai(images):
    """Extract structured features from a bank statement using OpenAI."""
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": 
                 "Extract structured data from this bank statement. Return a JSON object with:\n"
                 "- BankStatement (boolean)\n"
                 "- Document_Type (string)\n"
                 "- Account_Holder_Name (string)\n"
                 "- Account_Holder_Address (string)\n"
                 "- Table_Metadata (string, describing the transaction table)"
                }
            ],
        }
    ]

    for img in images[:5]:  # Limit input to first 5 pages
        base64_image = encode_image(img)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"}  # ✅ Correct format
    )

    try:
        result = response.choices[0].message.content
        return json.loads(result)
    except json.JSONDecodeError:
        return {"error": "Failed to parse OpenAI response"}



def text_file_parse(text_filepath):
    text = read_text_file(text_filepath)
    instruction = f"""
    Here is a Bank Statement page: {text}
    I need you to identify all the following metadata:-
    Account_Holder_Name, Account_Holder_Address

    Then I need you to go over the statement and find the possible column names to reconstruct the statement in pandas.

    Provide both in the following JSON object:
    {{
        "Account_Holder_Name": "string",
        "Account_Holder_Address": "string",
        "Table_Metadata": ["column1_name", "column2_name", ...]
        "Table":[...]
    }}
    """
    messages = [
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": instruction, "role": "user"},
    ]

    response = get_openai_response(messages)
    answer_json_string = response.model_dump_json(indent=2)
    answer_dict = json.loads(answer_json_string)
    answer = answer_dict['choices'][0]['message']['content']
    
    print(answer)
    save_json(answer, "halifax.json")
