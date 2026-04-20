_tenant_context = None


def set_tenant_context(tenant_id):
    global _tenant_context
    _tenant_context = tenant_id


def get_tenant_context():
    return _tenant_context


def get_current_tenant_id():
    """Get current tenant ID from context."""
    return _tenant_context


def get_current_actor_sub():
    """Get current actor subject (user identifier) from context."""
    return None


def reset_tenant_context():
    global _tenant_context
    _tenant_context = None
