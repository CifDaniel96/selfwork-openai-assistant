import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


def create_vector_store():
    vector_store = client.vector_stores.create(
        name="Travel Assistant Knowledge Base"
    )

    file_paths = [
        "kb/destinations.txt",
        "kb/itineraries.txt",
        "kb/travel_tips.txt",
    ]

    for file_path in file_paths:
        with open(file_path, "rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose="assistants",
            )

        client.vector_stores.files.create(
            vector_store_id=vector_store.id,
            file_id=uploaded_file.id,
        )

    return vector_store


if __name__ == "__main__":
    vector_store = create_vector_store()

    print("Vector Store creato correttamente")
    print(f"ID: {vector_store.id}")