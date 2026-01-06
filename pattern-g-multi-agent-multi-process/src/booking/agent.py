"""
Booking Specialist Agent - Pattern G

Runs as a separate service, handles booking requests.
"""

from shared import create_booking_service

# Initialize the booking service
booking_service = create_booking_service()


def book_slot(slot_id: str) -> str:
    """
    Book a specific tennis court slot.

    Args:
        slot_id: The slot ID from check_availability results

    Returns:
        Booking confirmation or error message
    """
    try:
        booking = booking_service.book(slot_id)
        return (
            f"Booking confirmed!\n"
            f"  Booking ID: {booking.booking_id}\n"
            f"  Court: {booking.court}\n"
            f"  Date: {booking.date}\n"
            f"  Time: {booking.time}"
        )
    except Exception as e:
        return f"Booking failed: {e}"


def process_booking_request(slot_id: str) -> str:
    """
    Process a booking request.

    This is the main entry point for the booking specialist.
    """
    return book_slot(slot_id)
