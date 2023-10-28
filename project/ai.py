import openai

openai.api_key = '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'

def get_events():
    messages = [
        {
            "role": "system",
            "content": f"""
            Follow the instructions below to convert the user's input statement into an SQL call.

            All entries follow this exact structure:
            [example entry]
            "name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders...",
            "name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music...",
            "name": "Charity Run", "date": "2023-05-01", "time": "07:00", "location": "Los Angeles City Center", "description": "A 5K run to raise funds...",
            "name": "Science Fair", "date": "2023-07-10", "time": "10:00", "location": "Science Museum, London", "description": "Engage with scientific discoveries...",
            [/example entry]

            If any of the user's requested information that can't be mapped to a key above,
            tell the user to re-enter.

            [/example input 1]
            I want to go to American events.
            [example input 1]

            [/example output1]
            SELECT * FROM location==*USA*
            [example output1]

            [/example input 2]
            I like bird poop.
            [example input 2]

            [/example output2]
            Irrelevant information, please re-enter.
            [example output2]


            """

        },
        {
            "role": "user",
            "content": f"""
            I want to see all events that occur at UofT.
            """
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()

# Using the function
data = get_events()
print(data)
