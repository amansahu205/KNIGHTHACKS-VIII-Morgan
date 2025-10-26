"""
Twilio Voice Service
Handles phone calls, recording, and transcription
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather


class TwilioService:
    """Service for managing Twilio voice calls"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            print("WARNING: Twilio credentials not configured. Running in mock mode.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        case_id: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate a phone call to client
        
        Args:
            to_number: Client's phone number
            from_number: Twilio number to call from (optional)
            case_id: Case identifier
            client_name: Client's name
            
        Returns:
            Call details including SID and status
        """
        if not self.client:
            # Mock mode for demo
            return {
                "status": "mock",
                "call_sid": f"CA_mock_{datetime.now().timestamp()}",
                "to": to_number,
                "from": from_number or self.phone_number,
                "message": "Mock call initiated (Twilio not configured)"
            }
        
        try:
            # Build call parameters
            call_params = {
                "to": to_number,
                "from_": from_number or self.phone_number,
                "url": "http://demo.twilio.com/docs/voice.xml"  # Default TwiML
            }
            
            # Add recording if enabled
            enable_recording = os.getenv("ENABLE_CALL_RECORDING", "False").lower() == "true"
            callback_url = os.getenv('CALL_RECORDING_STATUS_CALLBACK_URL', '')
            
            if enable_recording and callback_url:
                call_params["record"] = True
                call_params["recording_status_callback"] = f"{callback_url}/recording"
                call_params["status_callback"] = callback_url
                call_params["status_callback_event"] = ['initiated', 'ringing', 'answered', 'completed']
            
            # Initiate call
            call = self.client.calls.create(**call_params)
            
            return {
                "status": "success",
                "call_sid": call.sid,
                "to": call.to,
                "from": from_number or self.phone_number,
                "status_detail": call.status,
                "date_created": call.date_created.isoformat() if call.date_created else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to initiate call: {str(e)}"
            }
    
    def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """
        Get current status of a call
        
        Args:
            call_sid: Twilio Call SID
            
        Returns:
            Call status details
        """
        if not self.client:
            return {
                "status": "mock",
                "call_sid": call_sid,
                "message": "Mock call status"
            }
        
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "status": "success",
                "call_sid": call.sid,
                "call_status": call.status,
                "duration": call.duration,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "from": call.from_,
                "to": call.to
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_call_recording(self, call_sid: str) -> Dict[str, Any]:
        """
        Get recording URL for a completed call
        
        Args:
            call_sid: Twilio Call SID
            
        Returns:
            Recording details including URL
        """
        if not self.client:
            return {
                "status": "mock",
                "message": "Mock recording"
            }
        
        try:
            recordings = self.client.recordings.list(call_sid=call_sid, limit=1)
            
            if recordings:
                recording = recordings[0]
                return {
                    "status": "success",
                    "recording_sid": recording.sid,
                    "recording_url": f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}",
                    "duration": recording.duration,
                    "date_created": recording.date_created.isoformat() if recording.date_created else None
                }
            else:
                return {
                    "status": "not_found",
                    "message": "No recording found for this call"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def generate_call_twiml(
        self,
        message: str = None,
        connect_to_attorney: bool = True,
        attorney_number: str = None
    ) -> str:
        """
        Generate TwiML for call flow
        
        Args:
            message: Message to play to client
            connect_to_attorney: Whether to connect to attorney
            attorney_number: Attorney's phone number
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        # Greeting message
        if message:
            response.say(message, voice='alice', language='en-US')
        else:
            response.say(
                "Hello, this is Morgan and Morgan calling. "
                "Please hold while we connect you to your attorney.",
                voice='alice',
                language='en-US'
            )
        
        # Connect to attorney
        if connect_to_attorney:
            attorney_num = attorney_number or os.getenv("ATTORNEY_PHONE_NUMBER")
            if attorney_num:
                response.dial(attorney_num, timeout=30, record='record-from-answer')
            else:
                response.say(
                    "We're sorry, but we're unable to connect you at this time. "
                    "Please call our office directly.",
                    voice='alice',
                    language='en-US'
                )
        
        return str(response)
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message to client
        
        Args:
            to_number: Client's phone number
            message: SMS message content
            from_number: Twilio number to send from
            
        Returns:
            Message details
        """
        if not self.client:
            return {
                "status": "mock",
                "message_sid": f"SM_mock_{datetime.now().timestamp()}",
                "to": to_number,
                "body": message
            }
        
        try:
            msg = self.client.messages.create(
                to=to_number,
                from_=from_number or self.phone_number,
                body=message
            )
            
            return {
                "status": "success",
                "message_sid": msg.sid,
                "to": msg.to,
                "from": msg.from_,
                "body": msg.body,
                "date_sent": msg.date_sent.isoformat() if msg.date_sent else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global Twilio service instance
twilio_service = TwilioService()
