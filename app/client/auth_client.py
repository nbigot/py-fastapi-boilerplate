class AuthClient:
    def __init__(self, config: dict):
        self.config: dict = config

    def user_has_admin_role(self, user_uuid) -> bool:
        """Check if the user has the admin role"""
        user_roles = self.get_user_roles(user_uuid)
        return "admin" in user_roles

    def get_user_roles(self, user_uuid) -> list:
        """Get the user roles"""
        if not user_uuid:
            return []

        return ["admin", "user"]  # TODO: Mocked data

    def user_has_permissions(self, user_uuid, operation_id, request, **kwargs) -> bool:  # noqa
        """Check if the user has permissions"""
        if not user_uuid or not operation_id:
            return False

        return True  # TODO: Mocked data
