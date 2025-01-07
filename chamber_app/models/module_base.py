class ModuleBase:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def is_enabled(self, user):
        """Check if the module is enabled for the given user."""
        return self.name in user.enabled_modules  # Assuming user.enabled_modules is a list of enabled module names
