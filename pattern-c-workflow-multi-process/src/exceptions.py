"""Custom exceptions for Pattern C workflow."""


class WorkflowError(Exception):
    """Base exception for workflow errors."""


class ServiceError(WorkflowError):
    """A service failed during workflow execution."""

    def __init__(self, service_name: str, error: str) -> None:
        self.service_name = service_name
        self.error = error
        super().__init__(f"{service_name} failed: {error}")


class ParseError(ServiceError):
    """Intent parser service failed."""

    def __init__(self, error: str) -> None:
        super().__init__("IntentParser", error)


class AvailabilityError(ServiceError):
    """Availability service failed."""

    def __init__(self, error: str) -> None:
        super().__init__("AvailabilityChecker", error)


class BookingError(ServiceError):
    """Booking service failed."""

    def __init__(self, error: str) -> None:
        super().__init__("BookingHandler", error)
