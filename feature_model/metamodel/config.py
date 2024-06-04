from feature_model.metamodel.feature import F


class FConfig:

    def __init__(self, feature: F, path: str):
        self.feature = feature
        self.value = None
        self.path = path
        self.parent = None
        self.children: list[FConfig] = []

    def to_json(self):
        c = []
        for child in self.children:
            c.append(child.to_json())
        if c:
            if len(c) == 1:
                return {self.feature.name: c[0]}
            return {self.feature.name: c}
        elif self.value is not None:
            return {self.feature.name: self.value}
        else:
            return self.feature.name

    def add_child(self, child: 'FConfig'):
        child.parent = self
        self.children.append(child)

    def add_children(self, children: list['FConfig']):
        for child in children:
            child.parent = self
        self.children.extend(children)

    def get_child(self, name: str) -> 'FConfig':
        child = [c for c in self.children if c.feature.name == name]
        if len(child) > 1:
            raise ValueError(f"Feature {self.feature.name} has {len(child)} children with the name {name}. Make sure there are no more than one children with the same name")
        if len(child) == 0:
            return None
        return child[0]

    def get_children(self, name: str) -> list['FConfig']:
        return [c for c in self.children if c.feature.name == name]

    def get_depth(self, depth: int = 0) -> int:
        max_depth = depth
        for child in self.children:
            child_depth = child.get_depth(depth+1)
            if child_depth > max_depth:
                max_depth = child_depth
        return max_depth
