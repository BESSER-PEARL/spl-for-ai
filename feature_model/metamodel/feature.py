from feature_model.exceptions import ChildFeatureException, FeatureGroupException, FValueException

MANDATORY = 'mandatory'
OPTIONAL = 'optional'
OR = 'or'
ALTERNATIVE = 'alternative'

INDEX = 0


class FValue:

    def __init__(self, t: str, values: list = None, min: float = None, max: float = None):
        if ((min or max) and not values) or (not min and not max):
            if t == 'int':
                if values and any(map(lambda x: not isinstance(x, int), values)):
                    raise FValueException('Value must be an integer')
            if t == 'float':
                if values and any(map(lambda x: not isinstance(x, float), values)):
                    raise FValueException('Value must be a float')
            if t == 'str':
                if values and any(map(lambda x: not isinstance(x, str), values)):
                    raise FValueException(' Value must be a string')
        else:
            print('ERROR: Invalid arguments')
        self.t = t
        self.values = values
        self.min = min
        self.max = max


class F:

    @staticmethod
    def duplicate(f: 'F', parent: 'F' = None, min: int = 1, max: int = 1):
        new_f = F(f.name, min=min, max=max, value=f.value)
        new_f.parent = parent
        for children_group in f.children_groups:
            new_f.children_groups.append(children_group.duplicate(new_f))
        return new_f

    def __init__(self, name: str, min: int = 1, max: int = 1, value: FValue = None):
        self.name = name
        if min > max or min < 1:
            raise FeatureGroupException(f'Error in {name}: 0 < min < max')
        self.min = min
        self.max = max
        self.value = value
        self.parent: F = None
        self.children_groups: list[FGroup] = []
        global INDEX
        self.index = INDEX
        INDEX += 1

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def to_json(self):
        d = []
        for children_group in self.children_groups:
            g = {'kind': children_group.kind, 'features': []}
            d.append(g)
            for feature in children_group.features:
                g['features'].append(feature.to_json())
        return {self.name: d}

    def mandatory(self, child: 'F'):
        if child.parent is not None:
            raise ChildFeatureException(child, self)
        self.children_groups.append(FGroup(MANDATORY, [child]))
        child.parent = self
        return self

    def optional(self, child: 'F'):
        if child.parent is not None:
            raise ChildFeatureException(child, self)
        self.children_groups.append(FGroup(OPTIONAL, [child]))
        child.parent = self
        return self

    def alternative(self, children: list['F']):
        for child in children:
            if child.parent is not None:
                raise ChildFeatureException(child, self)
            child.parent = self
        self.children_groups.append(FGroup(ALTERNATIVE, children))
        return self

    def or_(self, children: list['F']):
        for child in children:
            if child.parent is not None:
                raise ChildFeatureException(child, self)
            child.parent = self
        self.children_groups.append(FGroup(OR, children))
        return self

    def get_depth(self, depth: int = 0) -> int:
        max_depth = depth
        for children_group in self.children_groups:
            for child in children_group.features:
                child_depth = child.get_depth(depth+1)
                if child_depth > max_depth:
                    max_depth = child_depth
        return max_depth


class FGroup:

    def __init__(self, kind: str, features: list[F] = []):
        if kind == (MANDATORY or kind == OPTIONAL) and len(features) > 1:
            raise FeatureGroupException(f'{kind} has more than one feature')
        if (kind == ALTERNATIVE or kind == OR) and len(features) < 2:
            raise FeatureGroupException(f'{kind} has less than 2 features')

        self.features: list[F] = features
        self.kind = kind

    def duplicate(self, parent: F):
        new_children: list[F] = []
        for f in self.features:
            new_children.append(F.duplicate(f, parent, min=f.min, max=f.max))
        return FGroup(self.kind, new_children)


class RootF(F):

    def __init__(self, name: str):
        global INDEX
        INDEX = 0
        super().__init__(name)
        self.parent = self  # Easy way to define root
