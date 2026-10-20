from __future__ import annotations

# Typed SDK errors for gradual service-layer migration; not all call sites raise these yet.


class PipefyError(Exception):
    """Base class for Pipefy SDK errors."""


class PipefyAPIError(PipefyError):
    """Raised when the Pipefy GraphQL API returns an error payload."""


class PipefyRequestTimeoutError(PipefyError, TimeoutError):
    """Raised when a GraphQL request exceeds the SDK's request timeout.

    Both gql's per-execute timer and the httpx transport are bounded by
    ``GraphQLEndpoint.GRAPHQL_REQUEST_TIMEOUT_SECONDS``. When that bound fires gql
    raises a bare :class:`TimeoutError` with an empty message, so a caller — and
    the MCP error layer that reads ``str(exc)`` — cannot tell a timeout from any
    other blank error, nor how long the call waited. The executor translates that
    bare timeout into this error, whose message names the limit and its value.

    It subclasses :class:`TimeoutError` as well as :class:`PipefyError` so the two
    contracts hold at once: existing ``except TimeoutError`` handlers keep catching
    a timed-out request, and it is also catchable as the SDK root like every other
    SDK error. ``timeout_seconds`` carries the bound that fired.
    """

    def __init__(self, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Pipefy GraphQL request timed out after {timeout_seconds} s "
            f"(GraphQLEndpoint.GRAPHQL_REQUEST_TIMEOUT_SECONDS). "
            "A mutation can still have been applied. Read the state back before you retry."
        )


class AiAgentConfigureError(PipefyError):
    """Raised when ``create_ai_agent`` created the agent but its configure update failed.

    The agent exists and is disabled when ``disabled_at`` is set. Write its
    behaviors with ``update_ai_agent(agent_uuid, ...)``, which keeps it disabled,
    then activate it with ``toggle_ai_agent_status``; or remove it with
    ``delete_ai_agent``. The update's error is the ``__cause__``.
    """

    def __init__(
        self, *, agent_uuid: str, disabled_at: str | None, reason: str
    ) -> None:
        self.agent_uuid = agent_uuid
        self.disabled_at = disabled_at
        message = (
            f"AI Agent {agent_uuid} was created, but writing its instruction "
            f"and behaviors failed: {reason}"
        )
        if disabled_at is not None:
            message += (
                f" The agent is disabled (disabledAt {disabled_at}). A routine "
                "update_ai_agent keeps it disabled; after a successful update, "
                "call toggle_ai_agent_status to activate it."
            )
        super().__init__(message)


class PortalPermissionError(ValueError):
    """Raised when a portal Interfaces operation fails with PERMISSION_DENIED."""
