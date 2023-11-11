import openai

openai.api_key = "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"


def get_events(user_input):
    # Pre-defined system message with instructions
    system_message_content = """
    Follow the instructions below to convert the user's input statement into an SQL call. If the statement can't convert to SQL, return "No".

    All entries follow this exact structure:
    [example entries]
    "name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders...",
    "name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music...",
    "name": "Charity Run", "date": "2023-05-01", "time": "07:00", "location": "Los Angeles City Center", "description": "A 5K run to raise funds...",
    "name": "Science Fair", "date": "2023-07-10", "time": "10:00", "location": "Science Museum, London", "description": "Engage with scientific discoveries...",
    [/example entries]

    

    """

    messages = [
        {
            "role": "system",
            "content": system_message_content,
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0,
        messages=messages
    )

    return response.choices[0].message["content"].strip()