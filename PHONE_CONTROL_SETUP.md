# Control Ela with an incoming phone call

This optional feature uses Twilio Programmable Voice. Ela accepts requests only
from the configured caller numbers, asks for a separate phone PIN, validates
Twilio's signed HTTPS webhooks, and asks you to approve each desktop task by
saying “yes” (or pressing 1). Press 2 or say “no” to cancel. Phone audio is
transcribed by Twilio's speech service; calls are not recorded by this code.

## Configure

1. Create a Twilio account and a voice-enabled Twilio phone number.
2. Install the project requirements, which include the Twilio SDK.
3. Add these values to the local `.env` file. Keep the auth token and PIN private.

```dotenv
ELA_PHONE_CONTROL_ENABLED=true
TWILIO_AUTH_TOKEN=your_twilio_auth_token
ELA_PHONE_PIN=choose_a_separate_6_digit_or_longer_pin
ELA_PHONE_ALLOWED_CALLERS=+91your_mobile_number
ELA_PHONE_WEBHOOK_URL=https://your-public-host.example
ELA_PHONE_LANGUAGE=hi-IN
ELA_PHONE_SPEECH_MODEL=experimental_conversations
ELA_PHONE_TTS_LANGUAGE=hi-IN
ELA_PHONE_PORT=8765
```

`ELA_PHONE_ALLOWED_CALLERS` accepts a comma-separated list of numbers in E.164
format. The phone PIN must be numeric and at least six digits. It must be
different from your laptop sign-in PIN.

## Connect Twilio to the laptop

Twilio needs a public HTTPS address to reach the local service. Start a trusted
HTTPS tunnel to `http://127.0.0.1:8765` using a tunnel provider you control.
Put that public HTTPS base URL in `ELA_PHONE_WEBHOOK_URL`, then set the Twilio
number's **A call comes in** webhook to:

```text
https://your-public-host.example/phone/voice
```

Use HTTP **POST**. Twilio will also call `/phone/auth` and `/phone/command`
during the same call; the app generates those callback addresses itself. Do
not expose port 8765 directly to the internet. The local listener binds only to
127.0.0.1.

Start Ela while the laptop is on, connected to the internet, and signed in to
the desktop session. Call the Twilio number, enter the phone PIN, say a task,
then approve the exact task Ela reads back. Keep the laptop awake while remote
control is needed. Screen, keyboard, and mouse actions may not work on a locked
desktop session.
