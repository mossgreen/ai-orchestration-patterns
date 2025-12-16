"""
Pattern B: Workflow Orchestrator (Shared Runtime)

Coordinates a fixed sequence of steps in a single process:
1. Intent Parser -> 2. Availability Checker -> 3. Booking Handler

Key difference from Pattern C:
- Pattern B: Direct function calls, shared memory, simpler
- Pattern C: ServiceResponse wrapper, independent deployability

Key difference from Pattern D:
- Pattern B: YOU define the exact workflow sequence (fixed)
- Pattern D: LLM decides which functions to call (dynamic)
"""

from .steps import IntentParserStep, AvailabilityStep, BookingStep


class WorkflowOrchestrator:
    """
    Coordinates the booking workflow as a fixed sequence.

    The workflow is always:
    1. Parse user intent (extract date/time)
    2. Check availability (find matching slots)
    3. Book first available slot (create reservation)
    """

    def __init__(self, verbose: bool = False) -> None:
        self._intent_parser = IntentParserStep()
        self._availability = AvailabilityStep()
        self._booking = BookingStep()
        self._verbose = verbose

    def _log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self._verbose:
            print(message)

    async def run(self, user_message: str) -> str:
        """
        Execute the complete booking workflow.

        This is a FIXED sequence - steps always execute in this order.

        Args:
            user_message: Natural language booking request

        Returns:
            Human-readable response (confirmation or error)
        """
        self._log(f"\n{'='*60}")
        self._log(f"WORKFLOW START: {user_message}")
        self._log(f"{'='*60}")

        try:
            # ============ Step 1: Parse Intent (always) ============
            self._log(f"\n[Step 1: Intent Parser]")
            intent = await self._intent_parser.parse(user_message)
            self._log(f"  Parsed date: {intent.date}")
            self._log(f"  Parsed time: {intent.time}")

            # ============ Step 2: Check Availability (always) ============
            self._log(f"\n[Step 2: Availability Checker]")
            slots = self._availability.check(intent)
            self._log(f"  Slots found: {len(slots)}")

            if not slots:
                self._log(f"\n{'='*60}")
                self._log(f"WORKFLOW COMPLETE: No availability")
                self._log(f"{'='*60}\n")
                return f"Sorry, no tennis courts are available for {intent.date or 'your requested date'}" + (
                    f" at {intent.time}" if intent.time else ""
                ) + ". Please try a different date or time."

            # Auto-select first available slot
            selected = slots[0]
            self._log(f"  Selected: {selected.court} at {selected.time}")

            # ============ Step 3: Book Slot (always) ============
            self._log(f"\n[Step 3: Booking Handler]")
            result = self._booking.book(selected)
            self._log(f"  Booking ID: {result.booking_id}")

            self._log(f"\n{'='*60}")
            self._log(f"WORKFLOW COMPLETE: Success")
            self._log(f"{'='*60}\n")

            return result.message

        except ValueError as e:
            self._log(f"\n{'='*60}")
            self._log(f"WORKFLOW FAILED: {e}")
            self._log(f"{'='*60}\n")
            return f"Sorry, I couldn't complete your booking: {e}"

        except Exception as e:
            self._log(f"\n{'='*60}")
            self._log(f"WORKFLOW ERROR: {e}")
            self._log(f"{'='*60}\n")
            return f"An unexpected error occurred: {e}"


# Convenience function for simple usage
async def run_workflow(
    user_message: str,
    verbose: bool = False
) -> str:
    """Run the booking workflow for a user message."""
    orchestrator = WorkflowOrchestrator(verbose=verbose)
    return await orchestrator.run(user_message)
