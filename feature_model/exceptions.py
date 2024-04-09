class ChildFeatureException(Exception):
    def __init__(self, child, parent):
        message = f'Feature{child.name} cannot be a child of {parent.name}. It has feature {child.parent.name} as parent.'
        super().__init__(message)


class FeatureGroupException(Exception):
    def __init__(self, message):
        super().__init__(message)


class FValueException(Exception):
    def __init__(self, message):
        super().__init__(message)
