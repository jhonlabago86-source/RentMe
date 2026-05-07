import json
from email.utils import parseaddr
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.mail import send_mail


def send_transactional_email(subject, message, recipient_email):
    brevo_api_key = getattr(settings, 'BREVO_API_KEY', '')

    if brevo_api_key:
        sender_name, sender_email = parseaddr(settings.DEFAULT_FROM_EMAIL)
        payload = {
            'sender': {
                'name': sender_name or 'RentMe',
                'email': sender_email or settings.DEFAULT_FROM_EMAIL,
            },
            'to': [{'email': recipient_email}],
            'subject': subject,
            'textContent': message,
        }
        request = Request(
            'https://api.brevo.com/v3/smtp/email',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'accept': 'application/json',
                'api-key': brevo_api_key,
                'content-type': 'application/json',
            },
            method='POST',
        )

        try:
            with urlopen(request, timeout=10) as response:
                if response.status not in (200, 201, 202):
                    raise RuntimeError(f'Brevo API returned status {response.status}.')
        except HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'Brevo API error: {error_body}') from e
        except URLError as e:
            raise RuntimeError(f'Brevo API connection failed: {e.reason}') from e
        return

    send_mail(
        subject,
        message,
        None,
        [recipient_email],
        fail_silently=False,
    )
