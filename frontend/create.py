import streamlit as st

from feature_model.metamodel import MANDATORY, OPTIONAL, OR, ALTERNATIVE, F, FConfig
from feature_model.model import fm


def create_config(feature: F, max_depth, depth=0):
    if depth == 0:
        st.checkbox(fm.name, value=True, disabled=True)
        config = create_config(fm, max_depth=max_depth-1, depth=depth+1)
        return config

    finstance = FConfig(feature)
    for feature_group in feature.children_groups:
        widths = ([1/max_depth/3] * depth)
        widths.append(1 - (1/max_depth/3)*depth)
        cols = st.columns(widths)
        col = cols[-1]
        if feature_group.kind == MANDATORY:
            child = feature_group.features[0]
            col.checkbox(label=child.name, value=True, disabled=True, key=child.index)
            child_instance = create_config(child, max_depth=max_depth, depth=depth + 1)
            finstance.add_child(child_instance)

        elif feature_group.kind == OPTIONAL:
            col.write(OPTIONAL)
            child = feature_group.features[0]
            if col.checkbox(label=child.name, disabled=False, key=child.index):
                child_instance = create_config(child, max_depth=max_depth, depth=depth + 1)
                finstance.add_child(child_instance)

        elif feature_group.kind == OR:
            or_error = True
            for child in feature_group.features:
                cols = st.columns(widths)
                col = cols[-1]
                if col.checkbox(label=child.name, disabled=False, key=child.index):
                    or_error = False
                    child_instance = create_config(child, max_depth=max_depth, depth=depth + 1)
                    finstance.add_child(child_instance)
            if or_error:
                message = 'You must select at least 1 of the following features: ' + ', '.join([child.name for child in feature_group.features])
                st.session_state['fm_error'] = True
                col.error(message)

        elif feature_group.kind == ALTERNATIVE:
            child = col.radio(label=ALTERNATIVE, label_visibility='collapsed', options=feature_group.features, disabled=False, format_func=lambda f: f.name)
            child_instance = create_config(child, max_depth=max_depth, depth=depth + 1)
            finstance.add_child(child_instance)

    return finstance


def create():
    st.header('Create')
    st.session_state['fm_error'] = False
    with st.sidebar:
        config = create_config(fm, max_depth=fm.get_depth(), depth=0)
    st.write(config.to_json())
    # Generate code

