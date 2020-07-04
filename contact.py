from twilio.rest import Client
from urllib.parse import urlparse, urlsplit, urlunsplit
import yaml


class Contact(object):

    def __init__(self, app, *args):
        config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
        self.client = Client(config.get('account_sid'), config.get('auth_token'))
        self.phone_number = config.get('phone_number')
        self.whatsapp_phone_number = config.get('whatsapp_phone_number')
        self.client.incoming_phone_numbers.list(phone_number=self.phone_number)[0].update(
            sms_url=f"{app.config.get('BASE_URL')}/receive_text", voice_url=f"{app.config.get('BASE_URL')}/receive_call")
        print("Initialized")

    def parse_url(self, url):
        split = list(urlsplit(url))
        if split[0] is '':
            split[0] = 'http'
            split[1] = split[2]
            split[2] = ''
        return urlunsplit(split)

    def send_message(self, form, contact_method):
        body = form.get('body', default='')
        image = form.get('image', default='')
        audio = form.get('audio', default='')
        if image != '':
            image = self.parse_url(image)
        if audio != '':
            audio = self.parse_url(audio)
        to = f"whatsapp:{form.get('phone_number')}" if contact_method.value == 'WhatsApp' else form.get('phone_number')
        from_ = f"whatsapp:{self.whatsapp_phone_number}" if contact_method.value == 'WhatsApp' else self.phone_number
        response = None
        error = None
        try:
            if contact_method.value == 'Voice':
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
        print("Contact Method: {}, To: {}, From: {}\nBody: {}, Image: {}, Audio: {}\nResponse: {}, Error: {}".format(contact_method.value, to, from_,
                                                                                                                     body, image, audio,
                                                                                                                     response, error))
        return response, error