"""
Google Calendar Integration Service
Handles calendar operations for Voice Bot Scheduler
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarService:
    """Google Calendar service for scheduling appointments"""
    
    def __init__(self):
        self.service = None
        self.timezone = pytz.timezone('America/New_York')  # Morgan & Morgan timezone
        
    def authenticate(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Authenticate with Google Calendar API
        
        Args:
            credentials_path: Path to OAuth credentials file
            token_path: Path to store/load access token
        """
        creds = None
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # For demo/testing, use mock credentials
                if not os.path.exists(credentials_path):
                    print("⚠️  No credentials.json found. Using mock calendar service.")
                    self.service = None
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    async def check_availability(
        self, 
        start_time: datetime, 
        end_time: datetime,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Check if a time slot is available
        
        Args:
            start_time: Start of time slot
            end_time: End of time slot
            calendar_id: Calendar to check (default: primary)
            
        Returns:
            True if slot is available, False if busy
        """
        if not self.service:
            # Mock response for demo
            return True
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return len(events) == 0  # Available if no events
            
        except HttpError as error:
            print(f"Calendar API error: {error}")
            return False
    
    async def find_available_slots(
        self,
        duration_minutes: int = 30,
        days_ahead: int = 14,
        preferred_hours: tuple = (9, 17),  # 9 AM to 5 PM
        calendar_id: str = 'primary'
    ) -> List[Dict[str, Any]]:
        """
        Find available time slots in the next N days
        
        Args:
            duration_minutes: Length of appointment
            days_ahead: How many days to search
            preferred_hours: Tuple of (start_hour, end_hour) in 24h format
            calendar_id: Calendar to check
            
        Returns:
            List of available slots with start/end times
        """
        available_slots = []
        now = datetime.now(self.timezone)
        
        for day_offset in range(days_ahead):
            check_date = now + timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
            
            # Check hourly slots during business hours
            for hour in range(preferred_hours[0], preferred_hours[1]):
                slot_start = check_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Skip past times
                if slot_start < now:
                    continue
                
                is_available = await self.check_availability(slot_start, slot_end, calendar_id)
                
                if is_available:
                    available_slots.append({
                        'start': slot_start,
                        'end': slot_end,
                        'formatted_start': slot_start.strftime('%A, %B %d at %I:%M %p'),
                        'formatted_end': slot_end.strftime('%I:%M %p'),
                        'day_of_week': slot_start.strftime('%A'),
                        'date': slot_start.strftime('%Y-%m-%d'),
                        'time': slot_start.strftime('%I:%M %p')
                    })
                
                # Limit to 5 slots for demo
                if len(available_slots) >= 5:
                    return available_slots
        
        return available_slots
    
    async def create_event(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str] = None,
        calendar_id: str = 'primary',
        send_notifications: bool = True
    ) -> Dict[str, Any]:
        """
        Create a calendar event
        
        Args:
            summary: Event title
            description: Event description
            start_time: Event start
            end_time: Event end
            attendees: List of email addresses
            calendar_id: Calendar to add event to
            send_notifications: Whether to send email notifications
            
        Returns:
            Created event details or mock response
        """
        if not self.service:
            # Mock response for demo
            return {
                'status': 'mock_created',
                'id': f'mock_event_{datetime.now().timestamp()}',
                'summary': summary,
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'htmlLink': 'https://calendar.google.com/calendar/mock',
                'attendees': attendees or []
            }
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': str(self.timezone),
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': str(self.timezone),
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},  # 30 min before
                ],
            },
        }
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendNotifications=send_notifications
            ).execute()
            
            return {
                'status': 'created',
                'id': created_event.get('id'),
                'summary': created_event.get('summary'),
                'start': created_event['start'].get('dateTime'),
                'end': created_event['end'].get('dateTime'),
                'htmlLink': created_event.get('htmlLink'),
                'attendees': attendees or []
            }
            
        except HttpError as error:
            print(f"Error creating event: {error}")
            return {
                'status': 'error',
                'error': str(error)
            }
    
    async def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any],
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """Update an existing calendar event"""
        if not self.service:
            return {'status': 'mock_updated', 'id': event_id}
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Apply updates
            event.update(updates)
            
            # Update event
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'status': 'updated',
                'id': updated_event.get('id'),
                'htmlLink': updated_event.get('htmlLink')
            }
            
        except HttpError as error:
            print(f"Error updating event: {error}")
            return {'status': 'error', 'error': str(error)}
    
    async def cancel_event(
        self,
        event_id: str,
        calendar_id: str = 'primary',
        send_notifications: bool = True
    ) -> Dict[str, Any]:
        """Cancel a calendar event"""
        if not self.service:
            return {'status': 'mock_cancelled', 'id': event_id}
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendNotifications=send_notifications
            ).execute()
            
            return {'status': 'cancelled', 'id': event_id}
            
        except HttpError as error:
            print(f"Error cancelling event: {error}")
            return {'status': 'error', 'error': str(error)}


# Global calendar service instance
calendar_service = CalendarService()
