import chainlit as cl

from travel_assistant.chat_logic import ChatLogic


@cl.on_chat_start
async def on_chat_start():
    chat = ChatLogic()

    cl.user_session.set("chat", chat)

    await cl.Message(
        content=(
            "🌍 **Benvenuto in Travel Assistant!**\n\n"
            "Posso aiutarti a scoprire destinazioni, itinerari e consigli di viaggio.\n\n"
            "Puoi anche chiedermi di inviarti un itinerario via email."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    chat = cl.user_session.get("chat")

    response = await cl.make_async(chat.send_message)(
        message.content
    )

    await cl.Message(
        content=response
    ).send()