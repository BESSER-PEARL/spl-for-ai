from feature_model.metamodel.config import FConfig


# TODO: NESTED PARAMETER
# TODO: CHECK IF POSITIVE PROMPTS WITHOUT DOUBLE QUOTES WORK
def generate_mergekit_yaml_configuration(config: FConfig, d={}):
    composition_configuration = config.get_child('Composite config').children[0]
    if composition_configuration.feature.name == 'Merge':
        yaml_config = generate_mergekit_yaml_configuration_merge(config, d)
    elif composition_configuration.feature.name == 'MoE':
        yaml_config = generate_mergekit_yaml_configuration_moe(config, d)
    return yaml_config


def generate_mergekit_yaml_configuration_merge(config: FConfig, d={}):
    merge_config = config.get_child('Composite config').get_child('Merge')
    if merge_config.get_child('models'):
        d['models'] = get_merge_input_models(merge_config.get_child('models').get_children('input_model'))
    if merge_config.get_child('slices'):
        d['slices'] = get_merge_output_slices(merge_config.get_child('slices').get_children('output_slice'))
    if merge_config.get_child('merge_method'):
        d['merge_method'] = merge_config.get_child('merge_method').value
    if merge_config.get_child('tokenizer_source'):
        d['tokenizer_source'] = merge_config.get_child('tokenizer_source').value
    if merge_config.get_child('base_model'):
        d['base_model'] = get_model_path(merge_config.get_child('base_model').get_child('model_reference'))
    if merge_config.get_child('dtype'):
        d['dtype'] = get_dtype_value(merge_config.get_child('dtype'))
    if merge_config.get_children('parameter'):
        d['parameters'] = get_parameters(merge_config.get_children('parameter'))
    return d


def generate_mergekit_yaml_configuration_moe(config: FConfig, d={}):
    moe_config = config.get_child('Composite config').get_child('MoE')
    if moe_config.get_child('base_model'):
        d['base_model'] = get_model_path(moe_config.get_child('base_model').get_child('model_reference'))
    if moe_config.get_child('dtype'):
        d['dtype'] = get_dtype_value(moe_config.get_child('dtype'))
    if moe_config.get_child('experts_per_token'):
        d['experts_per_token'] = moe_config.get_child('experts_per_token').value  # TODO: Must be < num experts and > 2
    if moe_config.get_child('gate_mode'):
        d['gate_mode'] = moe_config.get_child('gate_mode').value
    if moe_config.get_children('expert'):
        d['experts'] = get_experts(moe_config.get_children('expert'))
    return d


def get_experts(experts_config: list[FConfig]):
    l = []
    for expert_config in experts_config:
        d = {}
        d['source_model'] = get_model_path(expert_config.get_child('source_model').get_child('model_reference'))
        if expert_config.get_child('noise_scale'):
            d['noise_scale'] = expert_config.get_child('noise_scale').value
        positive_prompts = []
        negative_prompts = []
        for positive_prompt in expert_config.get_children('positive_prompt'):
            positive_prompts.append(positive_prompt.value)
        for negative_prompt in expert_config.get_children('negative_prompt'):
            negative_prompts.append(negative_prompt.value)
        if positive_prompts:
            d['positive_prompts'] = positive_prompts
        if negative_prompts:
            d['negative_prompts'] = negative_prompts
        l.append(d)
    return l


def get_dtype_value(dtype_config: FConfig):
    return dtype_config.get_child('value').value


def get_model_path(model_reference_config: FConfig):
    return model_reference_config.get_child('path').value


def get_parameters(parameters_config: list[FConfig]):
    d = {}
    for parameter_config in parameters_config:
        key = parameter_config.get_child('key').value
        value = parameter_config.get_child('value').value
        d[key] = value
    return d


def get_merge_input_models(input_models_config: list[FConfig]):
    l = []
    for input_model_config in input_models_config:
        d = {}
        d['model'] = get_model_path(input_model_config.get_child('model_reference'))
        if input_model_config.get_children('parameter'):
            d['parameters'] = get_parameters(input_model_config.get_children('parameter'))
        l.append(d)
    return l


def get_merge_output_slices(output_slices_config: list[FConfig]):
    l = []
    for output_slice_config in output_slices_config:
        d = {}
        d['sources'] = get_input_slices(output_slice_config.get_child('sources').get_children('input_slice'))
        if output_slice_config.get_child('base_model'):
            d['base_model'] = get_model_path(output_slice_config.get_child('base_model').get_child('model_reference'))
        if output_slice_config.get_child('residual_weight'):
            d['residual_weight'] = output_slice_config.get_child('residual_weight').value
        if output_slice_config.get_children('parameter'):
            d['parameters'] = get_parameters(output_slice_config.get_children('parameter'))
        l.append(d)
    return l


def get_input_slices(input_slices_config: list[FConfig]):
    l = []
    for input_slice_config in input_slices_config:
        d = {}
        d['model'] = get_model_path(input_slice_config.get_child('model_reference'))
        layer_range = input_slice_config.get_child('layer_range')
        # TODO: Check tuple works
        d['layer_range'] = [layer_range.get_child("layer_ini").value, layer_range.get_child("layer_end").value]
        if input_slice_config.get_children('parameter'):
            d['parameters'] = get_parameters(input_slice_config.get_children('parameter'))
        l.append(d)
    return l
