import streamlit as st
import yaml
from huggingface_hub import HfApi

from feature_model.metamodel.config import FConfig
from feature_model.metamodel.feature import OPTIONAL, MANDATORY, ALTERNATIVE, F, OR
from feature_model.model import fm
from generator.mergekit.run_mergekit import run_mergekit
from generator.mergekit.yaml_generator import generate_mergekit_yaml_configuration

KEY_COUNT = 0


def key_counter():
    global KEY_COUNT
    KEY_COUNT += 1
    return KEY_COUNT


def next_child(fconfig, child, col, widths, path, max_depth, depth):
    if child.max > 1:
        cardinality = col.number_input(label=f'Cardinality (min. {child.min}, max. {child.max})', min_value=child.min,
                                       max_value=child.max, key=f'{path} > {child.name} (cardinality)')
        for i in range(cardinality):
            if child.children_groups:
                cols = st.columns(widths)
                col = cols[-1]
                col.info(f'{child.name} ({i+1})')
            child_instance = create_config(child, max_depth=max_depth, depth=depth + 1,
                                           path=f'{path} > {child.name} ({i + 1})')
            fconfig.add_child(child_instance)
    else:
        child_instance = create_config(child, max_depth=max_depth, depth=depth + 1, path=f'{path} > {child.name}')
        fconfig.add_child(child_instance)


def create_config(feature: F, max_depth, depth=0, path=''):
    if depth == 0:
        st.checkbox(fm.name, value=True, disabled=True)
        config = create_config(fm, max_depth=max_depth-1, depth=depth+1, path=f'{feature.name}')
        return config

    fconfig = FConfig(feature, path)
    for feature_group in feature.children_groups:
        widths = ([1/max_depth/3] * depth)
        widths.append(1 - (1/max_depth/3)*depth)
        cols = st.columns(widths)
        col = cols[-1]
        if feature_group.kind in [MANDATORY, OPTIONAL]:
            child = feature_group.features[0]
            if col.checkbox(label=child.name, value=feature_group.kind == MANDATORY, disabled=feature_group.kind == MANDATORY, key=f'{path} > {child.name}'):
                next_child(fconfig, child, col, widths, path, max_depth, depth)

        elif feature_group.kind == OR:
            or_error = True
            for child in feature_group.features:
                cols = st.columns(widths)
                col = cols[-1]
                if col.checkbox(label=child.name, disabled=False, key=f'{path} > {child.name}'):
                    or_error = False
                    next_child(fconfig, child, col, widths, path, max_depth, depth)

            if or_error:
                message = 'You must select at least 1 of the following features: ' + ', '.join([child.name for child in feature_group.features])
                st.session_state['fm_error'] = True
                col.error(message)

        elif feature_group.kind == ALTERNATIVE:
            child = col.radio(label=ALTERNATIVE, label_visibility='collapsed', options=feature_group.features, disabled=False, format_func=lambda f: f.name)
            next_child(fconfig, child, col, widths, path, max_depth, depth)

    return fconfig


def fill_config(config: FConfig, max_depth, depth=0):
    widths = ([1 / max_depth / 3] * depth)
    widths.append(1 - (1 / max_depth / 3) * depth)
    cols = st.columns(widths)
    col = cols[-1]
    if config.feature.value:
        if config.feature.value.values:
            config.value = col.selectbox(label=config.feature.name, options=config.feature.value.values)
        elif config.feature.value.t == 'int':
            config.value = col.number_input(label=config.feature.name, min_value=config.feature.value.min, max_value=config.feature.value.max, step=1, key=f'{config.path} (input)')
        elif config.feature.value.t == 'float':
            config.value = col.number_input(label=config.feature.name, min_value=config.feature.value.min, max_value=config.feature.value.max, key=f'{config.path} (input)')
        elif config.feature.value.t == 'str':
            config.value = col.text_input(label=config.feature.name, key=f'{config.path} (input)')
        if config.value is None or config.value == '':
            st.session_state['fm_error'] = True
            col.error('Please enter a value')
        elif config.feature.name == 'path':
            try:
                model_info = HfApi().model_info(config.value)
            except Exception as e:
                st.session_state['fm_error'] = True
                col.error('The model path could not be found')
    else:
        col.write(config.feature.name)
    for child in config.children:
        fill_config(child, max_depth, depth=depth+1)


def create():
    st.header('Exploring the Use of Software Product Lines for the Combination of Machine Learning Models')
    st.image('docs/source/img/feature_model.png', use_column_width=True, caption='Feature Diagram')
    st.session_state['fm_error'] = False
    cols = st.columns(2)
    with cols[0]:
        st.header('🧠Feature Model')
        st.info('Here you can visualize the Feature Model. As you select the features, the tree will display/hide the '
                'children features. Some features have editable cardinality.')
        config = create_config(fm, max_depth=fm.get_depth(), depth=0)
    if not st.session_state['fm_error']:
        with cols[1]:
            st.header('✍ Feature Configuration')
            st.info('The selected features conform a Feature Configuration, that you will visualize here. Some features '
                    'have attributes that must be set before proceeding to the LLM generation.')
            fill_config(config, max_depth=config.get_depth(), depth=0)
            #st.json(config.to_json())
    run_config = {}
    with st.sidebar:
        run_config['model_name'] = st.text_input(label='Model name')
        run_config['directory'] = st.text_input(label='Model output directory', value='merge')
        if not run_config['model_name']:
            st.session_state['fm_error'] = True
        run_config['runtime'] = st.selectbox(label='Runtime', options=["CPU", "CPU + High-RAM", "GPU"])
        if config.get_child('Composition tool').get_child('Mergekit'):
            if config.get_child('Composite config').children[0].feature.name == 'Merge':
                run_config['mergekit_branch'] = 'main'
            if config.get_child('Composite config').children[0].feature.name == 'MoE':
                run_config['mergekit_branch'] = 'mixtral'
        run_config['trust_remote_code'] = st.toggle(label='Trust remote code')
        run_config['upload_to_hf'] = st.toggle(label='Upload to HuggingFace')
        if run_config['upload_to_hf']:
            run_config['username'] = st.text_input(label='Username')
            run_config['hf_token'] = st.text_input(label='HF Token')
            run_config['license'] = st.selectbox(label='License', options=['apache-2.0', 'cc-by-nc-4.0', 'mit', 'openrail'])

        if st.button('Generate LLM', disabled=st.session_state['fm_error']):
            yaml_config = generate_mergekit_yaml_configuration(config, {})
            with open('config.yaml', 'w') as yaml_file:
                yaml.dump(yaml_config, yaml_file, default_flow_style=False)
                st.success('YAML config file for Mergekit successfully generated')
            with open('config.yaml', 'r') as yaml_file:
                run_config['yaml_config'] = yaml_file.read()
            st.text(run_config['yaml_config'])
            run_mergekit(run_config)
