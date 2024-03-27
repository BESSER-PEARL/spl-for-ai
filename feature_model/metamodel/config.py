from feature_model.metamodel.feature import F


class FConfig:

    def __init__(self, feature: F, path: str):
        self.feature = feature
        self.value = None  # TODO: Value only in leaf nodes? (yaml)
        self.path = path
        self.parent = None
        self.children: list[FConfig] = []

    def to_json(self):
        c = []
        for child in self.children:
            c.append(child.to_json())
        return {self.feature.name: c}

    def add_child(self, child: 'FConfig'):
        child.parent = self
        self.children.append(child)

    def add_children(self, children: list['FConfig']):
        for child in children:
            child.parent = self
        self.children.extend(children)

    def get_depth(self, depth: int = 0) -> int:
        max_depth = depth
        for child in self.children:
            child_depth = child.get_depth(depth+1)
            if child_depth > max_depth:
                max_depth = child_depth
        return max_depth
