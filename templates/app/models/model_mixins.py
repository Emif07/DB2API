class ModelToDictMixin:
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
