"""Incoming Twilio phone calls for authenticated, approval-gated commands."""

from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import os
import threading
import time
from urllib.parse import parse_qs, urlsplit


class PhoneCallServer:
    def __init__(self, brain):
        self.brain = brain
        self.server = None
        self.thread = None
        self.base_url = ""
        self.auth_token = ""
        self.phone_pin = ""
        self.allowed_callers = set()
        self.language = "hi-IN"
        self.speech_model = "experimental_conversations"
        self.tts_language = "hi-IN"
        self.authenticated_calls = {}
        self.call_steps = {}
        self.failed_pin_attempts = {}
        self.blocked_callers = {}
        self.processed_requests = OrderedDict()
        self._state_lock = threading.Lock()
        self._command_lock = threading.Lock()
        self._validator = None
        self._twiml = None

    @staticmethod
    def enabled() -> bool:
        return os.getenv("ELA_PHONE_CONTROL_ENABLED", "false").strip().lower() in {
            "1", "true", "yes", "on",
        }

    def start(self) -> bool:
        if not self.enabled():
            return False

        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        self.phone_pin = os.getenv("ELA_PHONE_PIN", "").strip()
        self.allowed_callers = {
            item.strip() for item in
            os.getenv("ELA_PHONE_ALLOWED_CALLERS", "").split(",")
            if item.strip()
        }
        self.base_url = os.getenv("ELA_PHONE_WEBHOOK_URL", "").strip().rstrip("/")
        self.language = os.getenv("ELA_PHONE_LANGUAGE", "hi-IN").strip()
        self.speech_model = os.getenv(
            "ELA_PHONE_SPEECH_MODEL", "experimental_conversations"
        ).strip()
        self.tts_language = os.getenv("ELA_PHONE_TTS_LANGUAGE", "hi-IN").strip()

        if len(self.auth_token) < 20:
            raise ValueError("Remote phone control requires TWILIO_AUTH_TOKEN.")
        if len(self.phone_pin) < 6 or not self.phone_pin.isdigit():
            raise ValueError("Set a separate 6+ digit ELA_PHONE_PIN for calls.")
        if not self.allowed_callers:
            raise ValueError("ELA_PHONE_ALLOWED_CALLERS must contain your phone number.")
        if not self.base_url.startswith("https://"):
            raise ValueError("ELA_PHONE_WEBHOOK_URL must be a public HTTPS URL.")

        try:
            from twilio.request_validator import RequestValidator
            from twilio.twiml.voice_response import VoiceResponse
        except ImportError as error:
            raise RuntimeError(
                "Phone control is enabled, but the Twilio SDK is missing. "
                "Install requirements-windows.txt (or requirements-macos.txt)."
            ) from error

        self._validator = RequestValidator(self.auth_token)
        self._twiml = VoiceResponse
        port = int(os.getenv("ELA_PHONE_PORT", "8765"))
        controller = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                controller._handle_request(self)

            def log_message(self, format_string, *args):
                # Do not write caller IDs, speech text, PINs, or Twilio payloads.
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            name="ElaPhoneCallServer",
            daemon=True,
        )
        self.thread.start()
        print(f"Authenticated phone control is listening on localhost:{port}.")
        return True

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def _handle_request(self, handler):
        path = urlsplit(handler.path).path
        if path not in {"/phone/voice", "/phone/auth", "/phone/command"}:
            self._send(handler, 404, "Not found", "text/plain; charset=utf-8")
            return

        try:
            size = int(handler.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if size <= 0 or size > 65536:
            self._send(handler, 400, "Invalid request", "text/plain; charset=utf-8")
            return

        body = handler.rfile.read(size)
        values = parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
        params = {key: items[-1] for key, items in values.items()}
        signed_url = self.base_url + handler.path
        signature = handler.headers.get("X-Twilio-Signature", "")
        if not self._validator.validate(signed_url, params, signature):
            self._send(handler, 403, "Invalid webhook signature", "text/plain; charset=utf-8")
            return

        caller = params.get("From", "").strip()
        if caller not in self.allowed_callers:
            response = self._twiml()
            response.say("This number is not allowed to control Ela.", language=self.tts_language)
            response.hangup()
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return

        with self._state_lock:
            blocked_until = self.blocked_callers.get(caller, 0)
        if path == "/phone/voice" and blocked_until > time.monotonic():
            response = self._twiml()
            response.say("Phone access is temporarily locked. Try again later.", language=self.tts_language)
            response.hangup()
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return

        call_sid = params.get("CallSid", "")
        if path == "/phone/voice":
            self._begin_auth(handler)
        elif path == "/phone/auth":
            self._verify_pin(handler, call_sid, params)
        elif path == "/phone/command":
            self._run_command(handler, call_sid, params)

    def _begin_auth(self, handler):
        response = self._twiml()
        gather = response.gather(
            input="dtmf",
            action=self.base_url + "/phone/auth",
            method="POST",
            num_digits=len(self.phone_pin),
            timeout=12,
        )
        gather.say(
            "Ela phone control. Please enter your private phone PIN.",
            language=self.tts_language,
        )
        response.say("No PIN was received. Goodbye.", language=self.tts_language)
        response.hangup()
        self._send(handler, 200, str(response), "application/xml; charset=utf-8")

    def _verify_pin(self, handler, call_sid, params):
        caller = params.get("From", "").strip()
        supplied = params.get("Digits", "").strip()
        if not call_sid or not hmac.compare_digest(supplied, self.phone_pin):
            with self._state_lock:
                attempts, _expires = self.failed_pin_attempts.get(caller, (0, 0))
                attempts += 1
                expiry = time.monotonic() + 3600
                self.failed_pin_attempts[caller] = (attempts, expiry)
                if attempts >= 5:
                    self.blocked_callers[caller] = expiry
            response = self._twiml()
            response.say("The PIN was not accepted. Goodbye.", language=self.tts_language)
            response.hangup()
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return

        with self._state_lock:
            self._prune_state()
            self.failed_pin_attempts.pop(caller, None)
            self.authenticated_calls[call_sid] = time.monotonic() + 1800
            self.call_steps[call_sid] = 1
        response = self._twiml()
        self._gather_command(response, "PIN accepted. Say your command.", call_sid, 1)
        self._send(handler, 200, str(response), "application/xml; charset=utf-8")

    def _gather_command(self, response, prompt, call_sid, step):
        action = f"{self.base_url}/phone/command?step={step}"
        gather = response.gather(
            input="speech dtmf",
            action=action,
            method="POST",
            language=self.language,
            speech_model=self.speech_model,
            # Twilio requires a positive integer speechTimeout when an
            # explicit speechModel is selected.
            speech_timeout=4,
            timeout=8,
            num_digits=1,
        )
        gather.say(prompt, language=self.tts_language)
        response.say("I did not hear a command. Goodbye.", language=self.tts_language)
        response.hangup()

    def _run_command(self, handler, call_sid, params):
        with self._state_lock:
            expiry = self.authenticated_calls.get(call_sid, 0)
        if not call_sid or expiry < time.monotonic():
            response = self._twiml()
            response.say("Your phone session expired. Please call again.", language=self.tts_language)
            response.hangup()
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return

        speech = params.get("SpeechResult", "").strip()
        digits = params.get("Digits", "").strip()
        query = parse_qs(urlsplit(handler.path).query)
        try:
            step = int(query.get("step", ["0"])[-1])
        except ValueError:
            step = 0
        with self._state_lock:
            expected_step = self.call_steps.get(call_sid, 0)
        if step <= 0 or step > expected_step:
            response = self._twiml()
            response.say("This command request expired. Please say it again.", language=self.tts_language)
            self._gather_command(response, "What would you like me to do?", call_sid, expected_step)
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return
        if digits == "1":
            speech = "yes"
        elif digits == "2":
            speech = "no"
        if not speech:
            response = self._twiml()
            self._gather_command(
                response,
                "I did not hear that. Please say the command again.",
                call_sid,
                expected_step,
            )
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return
        if len(speech) > 1000:
            response = self._twiml()
            response.say("That command was too long. Please say it again briefly.", language=self.tts_language)
            self._gather_command(response, "What would you like me to do?", call_sid, expected_step)
            self._send(handler, 200, str(response), "application/xml; charset=utf-8")
            return

        # Twilio may retry a slow webhook while the original request is still
        # executing. Check and cache under one lock to prevent duplicate actions.
        with self._command_lock:
            request_key = (call_sid, str(step))
            with self._state_lock:
                cached = self.processed_requests.get(request_key)
                if cached is not None:
                    self.processed_requests.move_to_end(request_key)
            if cached is not None:
                self._send(handler, 200, cached, "application/xml; charset=utf-8")
                return

            try:
                result = self.brain.process(speech)
            except Exception as error:
                print(f"Phone command failed: {type(error).__name__}: {error}")
                result = "I could not complete that command. Please try again."

            response = self._twiml()
            next_step = max(step, expected_step) + 1
            with self._state_lock:
                self.call_steps[call_sid] = next_step
            self._gather_command(
                response,
                (str(result)[:700] + " You may say another command, or hang up."),
                call_sid,
                next_step,
            )
            xml = str(response)
            with self._state_lock:
                self.processed_requests[request_key] = xml
                self.processed_requests.move_to_end(request_key)
                while len(self.processed_requests) > 256:
                    self.processed_requests.popitem(last=False)
            self._send(handler, 200, xml, "application/xml; charset=utf-8")

    def _prune_state(self):
        now = time.monotonic()
        self.authenticated_calls = {
            call_sid: expiry
            for call_sid, expiry in self.authenticated_calls.items()
            if expiry > now
        }
        self.call_steps = {
            call_sid: step
            for call_sid, step in self.call_steps.items()
            if call_sid in self.authenticated_calls
        }
        self.failed_pin_attempts = {
            caller: (attempts, expiry)
            for caller, (attempts, expiry) in self.failed_pin_attempts.items()
            if expiry > now
        }
        self.blocked_callers = {
            caller: expiry
            for caller, expiry in self.blocked_callers.items()
            if expiry > now
        }

    @staticmethod
    def _send(handler, status, content, content_type):
        data = content.encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Content-Length", str(len(data)))
        handler.send_header("Cache-Control", "no-store")
        handler.end_headers()
        handler.wfile.write(data)
