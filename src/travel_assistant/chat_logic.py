import os
import resend
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
resend.api_key = os.getenv("RESEND_KEY")


SEND_EMAIL_TOOL = {
    "type": "function",
    "name": "send_email",
    "description": (
        "Invia via email informazioni o itinerari di viaggio "
        "quando l'utente richiede esplicitamente l'invio."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Indirizzo email del destinatario",
            },
            "subject": {
                "type": "string",
                "description": "Oggetto dell'email",
            },
            "html": {
                "type": "string",
                "description": "Contenuto HTML dell'email",
            },
        },
        "required": ["to", "subject", "html"],
        "additionalProperties": False,
    },
    "strict": True,
}

def send_email(to: str, subject: str, html: str):
    params: resend.Emails.SendParams = {
        "from": "Travel Assistant <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "html": html,
    }

    return resend.Emails.send(params)

class ChatLogic:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_KEY")
        )

        self.vector_store_id = os.getenv("VECTOR_STORE_ID")

        self.conversation = self.client.conversations.create()

    def send_message(self, message: str) -> str:
        tools = [
            {
                "type": "file_search",
                "vector_store_ids": [self.vector_store_id],
            },
            SEND_EMAIL_TOOL,
        ]

        instructions = (
            "Sei Travel Assistant, un assistente specializzato in viaggi. "
            "Rispondi utilizzando le informazioni presenti nella knowledge base. "
            "Se l'informazione richiesta non è disponibile nei documenti, "
            "dillo chiaramente senza inventare dati. "
            "Usa send_email solo quando l'utente richiede esplicitamente "
            "di ricevere informazioni via email. "
            "Se manca l'indirizzo email, chiedilo prima di inviare."
        )

        response = self.client.responses.create(
            model="gpt-5-mini",
            conversation=self.conversation.id,
            instructions=instructions,
            input=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            tools=tools,
        )

        while True:
            function_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                return response.output_text

            tool_outputs = []

            for function_call in function_calls:
                if function_call.name == "send_email":
                    arguments = json.loads(function_call.arguments)

                    try:
                        send_email(
                            to=arguments["to"],
                            subject=arguments["subject"],
                            html=arguments["html"],
                        )

                        result = "Email inviata con successo."

                    except Exception as error:
                        print(f"ERRORE SEND_EMAIL: {type(error).__name__}: {error}")
                        result = f"Errore durante l'invio dell'email: {error}"

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": function_call.call_id,
                            "output": result,
                        }
                    )

            response = self.client.responses.create(
                model="gpt-5-mini",
                conversation=self.conversation.id,
                instructions=instructions,
                input=tool_outputs,
                tools=tools,
            )
