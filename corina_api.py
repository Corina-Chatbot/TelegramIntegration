from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

session_ids = {}

apikey = os.getenv("API_KEY")
url = os.getenv("URL")
assistant_id = os.getenv("ASSISTANT")

authenticator = IAMAuthenticator(apikey)
assistant = AssistantV2(
    version="2020-03-22",
    authenticator=authenticator
)

assistant.set_service_url(url)
assistant.set_disable_ssl_verification(True)


# Erstellt eine Session oder verwendet eine gespeicherte aus dem Arbeitsspeicher
def get_session(chat_id):
    if chat_id not in session_ids:
        session = assistant.create_session(assistant_id).get_result()
        session_ids.update({chat_id: session['session_id']})
    return session_ids[chat_id]


# Beantwortet eine Frage für eine bestimmte Chat_id
def question(text: str, chat_id):
    workspace_id = os.getenv("WORKSPACE")
    response = assistant.message(
        assistant_id=assistant_id,
        session_id=get_session(chat_id),
        workspace_id=workspace_id,
        input={
            'text': text
        }).get_result()
    image = None
    text = " ".join(text) if (text:=response['output'].get('text', "")) else ""
    options = []
    for g in response['output']['generic']:

        # Wenn ein Bild verlinkt wird, wird das Bild auch zurückgegeben
        image = g['source'] if g['response_type'] == 'image' else None

        # Optionale Knöpfe unter der Nachricht. Die Nachfrage, ob online nach Ergebnissen gesucht werden soll,
        # wird ausgeschalten
        if g['response_type'] == 'option':
            text = "\n\n".join([text, g["title"]])
            for o in g['options']:
                options.append([o['label'], o['value']['input']['text']])
    if not text:
        text = "Leider kann ich dir diese Frage nicht beantworten."
    text = text.replace("<br/>", "\n")
    text = text.replace("<p>", "")
    text = text.replace("</p>", "")
    return text, image, options

