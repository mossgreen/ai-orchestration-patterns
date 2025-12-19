"""
Singleton services for Pattern A.

BookingService is created once at module load (like Spring's @Component).
This ensures bookings persist across requests.
"""

from shared import create_booking_service

# Singleton - created once when module loads
booking_service = create_booking_service()
