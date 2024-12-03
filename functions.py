import json
import os

def create_assistant(client):
    assistant_file_path = 'assistant.json'

    if os.path.exists(assistant_file_path):
        # Load existing assistant ID
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Create a new assistant without using a file
        assistant = client.beta.assistants.create(
            instructions="""
                You are tasked with determining the value of an item based on the text provided by the user. Use the item details to estimate its market value in an online marketplace, such as Poshmark or eBay. Do not ask the user for any additional information; only use the details provided in their message.

In your output to the user, you should include the following details based on your research:

Title of the item
Category
Color
Brand
Size (if clothing)
Year manufactured (approximate value is fine if the exact year is unknown)
Distinguishing characteristics (any unique or notable features)
Approximate value (estimated market value)
Average value of similarly listed items (e.g., on marketplaces like Poshmark, eBay)
Suggested listing price (based on the average market value and item condition)
Additionally, you should notify the user if there are any versions of the item that may be worth more. For example, if the item has distinguishing characteristics like being rare, recalled, misprinted, or any other special feature, it may fetch a higher value than the typical version of the same item.

You MUST provide the following information:

Average sold prices from Poshmark in the last 90 days.
Average sold prices from eBay in the last 90 days.
Approximate Sell-Through Rate (STR) for the last 90 days.
            """,
            model="gpt-4-1106-preview",
            tools=[{ "type":"retrieval"}]  # Empty tools list since no retrieval or files are used
        )

        # Save the new assistant ID
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
