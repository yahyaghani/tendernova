from utils.openai_utils import encode_image
from utils.client import client

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
        response_format={"type": "json_object"}
    )

    try:
        # ✅ Directly parse response (it's already a JSON object)
        result = response.choices[0].message.content  # This is already a dict, not a string
        if isinstance(result, dict):  # Ensure it's a dictionary
            return {
                "BankStatement": result.get("BankStatement", False),
                "Document_Type": result.get("Document_Type", "Unknown"),
                "Account_Holder_Name": result.get("Account_Holder_Name", "Not available"),
                "Account_Holder_Address": result.get("Account_Holder_Address", "Not available"),
                "Table_Metadata": result.get("Table_Metadata", "Not available")
            }
        else:
            return {"error": "Unexpected response format from OpenAI"}
    
    except Exception as e:
        return {"error": f"Failed to parse OpenAI response: {str(e)}"}
