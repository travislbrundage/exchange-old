class BaseServiceBackend(object):
    """Service abstract base class"""

    def remove_record(self, pk):
        """Remove record from the service"""
        raise NotImplementedError()

    def create_record(self, item):
        """Create or update record in the service"""
        raise NotImplementedError()

    def update_record(self, item):
        """Create or update record in the service"""
        raise NotImplementedError()

    def get_record(self, pk):
        """Get record from the service"""
        raise NotImplementedError()

    def search_records(self, limit=None, **filters):
        """Search for records from the service"""
        raise NotImplementedError()
