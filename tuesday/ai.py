import requests


class TuesdayAI:

    def __init__(self):

        self.url = "http://localhost:11434/api/chat"

        self.model = "llama3.2"

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are Tuesday, a helpful voice assistant. "
                    "Your responses are spoken aloud using text-to-speech. "
                    "Speak naturally and conversationally. "
                    "Be concise and get to the point. "
                    "Normally answer in 1 to 4 sentences. "
                    "Only give a longer answer when the user asks for detail. "
                    "Do not use markdown, bullet points, emojis, or unnecessary formatting. "
                    "Do not start answers with phrases like 'Certainly' or 'Of course' unless natural. "
                    "If the user asks a simple question, give a simple answer. "
                    "Remember the recent conversation and use context when answering follow-up questions."
                ),
            }
        ]

        self.max_history = 10

    def ask(self, text):

        self.messages.append(
            {
                "role": "user",
                "content": text,
            }
        )

        # Keep the system prompt plus recent conversation.
        if len(self.messages) > self.max_history + 1:

            self.messages = (
                [self.messages[0]]
                + self.messages[-self.max_history:]
            )

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": self.messages,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        answer = data["message"]["content"].strip()

        self.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        return answer