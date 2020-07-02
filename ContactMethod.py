from enum import Enum
from twilio.rest import Client
import yaml

class ContactMethod(Enum):
    SMS = "SMS"
    VOICE = "Voice"
    WHATSAPP = "WhatsApp"

    def __init__(self, *args):
        config = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)
        self.client = Client(config.get("account_sid"), config.get("auth_token"))
        self.phone_number = config.get("phone_number")
        self.whatsapp_phone_number = config.get("whatsapp_phone_number")

    def send_message(self, form):
        body = form.get('body', default='')
        image = form.get('image', default='')
        audio = form.get('audio', default='')
        to = f"whatsapp:{form.get('phone_number')}" if self.value == 'WhatsApp' else form.get('phone_number')
        from_ = f"whatsapp:{self.whatsapp_phone_number}" if self.value == 'WhatsApp' else self.phone_number
        response = None
        error = None
        try:
            if self.value == 'Voice':
                if audio and not audio.isspace():
                    audio = f"<Play>{audio}</Play>"
                response = self.client.calls.create(
                               twiml=f"""<Response>
                                             <Say>{body}</Say>
                                             {audio}
                                         </Response>""",
                               from_=from_,
                               to=to)
            else:
                if image and not image.isspace():
                    response = self.client.messages.create(
                                   body=body,
                                   media_url=image,
                                   from_=from_,
                                   to=to)
                else:
                    response = self.client.messages.create(
                                   body=body,
                                   from_=from_,
                                   to=to)
        except Exception as e:
            error = e
        print("Contact Method: {}, To: {}, From: {}\nBody: {}, Image: {}, Audio: {}\nResponse: {}, Error: {}".format(self.value, to, from_,
                                                                                                                     body, image, audio,
                                                                                                                     response, error))
        return response, error