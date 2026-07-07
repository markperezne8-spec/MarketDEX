class NavigationService:
    """Minimal legacy navigation contract preserved for existing shell tests."""

    def navigate(self, destination: str) -> str:
        if not isinstance(destination, str) or not destination.strip():
            raise ValueError("destination must be a non-empty string")
        return destination
