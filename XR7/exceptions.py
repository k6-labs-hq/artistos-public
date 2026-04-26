class TenantIsolationViolation(Exception):
    """Raised when a database operation would cross tenant boundaries.

    Carries structured context so callers can audit / propagate without
    re-deriving it from a free-form message.
    """

    def __init__(
        self,
        *,
        current_tenant: str,
        target_tenant: str | None,
        operation: str,
        model: str,
        actor_sub: str | None = None,
    ) -> None:
        self.current_tenant = current_tenant
        self.target_tenant = target_tenant
        self.operation = operation
        self.model = model
        self.actor_sub = actor_sub
        super().__init__(
            f"{operation} on {model} crosses tenant boundary "
            f"(current={current_tenant}, target={target_tenant})"
        )


class ResourceNotFoundError(Exception):
    pass
