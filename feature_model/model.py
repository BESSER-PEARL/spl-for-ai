from feature_model.metamodel.feature import RootF, F, FValue

INF = 256

fm_parameter = (RootF('parameter')
                .mandatory(F('key', value=FValue('str')))
                .mandatory(F('value', value=FValue('str')))
                )


fm_model_reference = (RootF('model_reference')
                      .mandatory(F('path', value=FValue('str')))
                      )

fm_dtype = (RootF('dtype')
            .mandatory(F('value', value=FValue('str', values=['float32', 'float64', 'complex64', 'complex128', 'float16', 'bfloat16', 'uint8', 'int8', 'int16', 'int32', 'int64', 'bool'])))
            )

fm_base_model = (RootF('base_model')
                 .mandatory(F.duplicate(fm_model_reference))
                 )


fm = (RootF('Composition')
      .mandatory(F('Composition tool')
                 .mandatory(F('Mergekit'))  # When we add other tools, this feature group will be alternative
                 )
      .mandatory(F('Composite config')
                 .alternative([F('MoE')
                               .mandatory(F.duplicate(fm_base_model))
                               .optional(F.duplicate(fm_dtype))
                               .mandatory(F('experts_per_token', value=FValue('int', min=2)))
                               .mandatory(F('gate_mode', value=FValue('str', values=['hidden', 'cheap_embed', 'random'])))  # Options
                               .mandatory(F('expert', min=2, max=INF)
                                          .optional(F('noise_scale', value=FValue('float')))
                                          .mandatory(F('positive_prompt', min=1, max=INF, value=FValue('str')))
                                          .optional(F('negative_prompt', min=1, max=INF, value=FValue('str')))
                                          .mandatory(F('source_model')
                                                     .mandatory(F.duplicate(fm_model_reference)))
                                          ),
                               F('Merge')
                               .mandatory(F('merge_method', value=FValue('str', values=['linear', 'slerp', 'task_arithmetic', 'ties', 'dare_ties', 'dare_linear', 'passthrough', 'model_stock'])))  # Options
                               .alternative([F('slices')
                                             .mandatory(F('output_slice', min=1, max=INF)
                                                        .mandatory(F('sources')
                                                                   .mandatory(F('input_slice', min=1, max=INF)
                                                                              .mandatory(F.duplicate(fm_model_reference))
                                                                              .mandatory(F('layer_range')
                                                                                         .mandatory(F('layer_ini', value=FValue('int', min=0)))
                                                                                         .mandatory(F('layer_end', value=FValue('int', min=0)))
                                                                                         )
                                                                              .optional(F.duplicate(fm_parameter, min=1, max=INF))
                                                                              )
                                                                   )
                                                        .optional(F.duplicate(fm_base_model))
                                                        .optional(F('residual_weight', value=FValue('float')))
                                                        .optional(F.duplicate(fm_parameter, min=1, max=INF))
                                                        ),
                                             F('models')
                                             .mandatory(F('input_model', min=1, max=INF)
                                                        .mandatory(F.duplicate(fm_model_reference))
                                                        .optional(F.duplicate(fm_parameter, min=1, max=INF))
                                                        )
                                             ])
                               .optional(F.duplicate(fm_parameter, min=1, max=INF))
                               .optional(F.duplicate(fm_base_model))
                               .optional(F.duplicate(fm_dtype))
                               .optional(F('tokenizer_source', value=FValue('str', values=['base', 'union', 'model: <model_path>'])))
                               ])
                 )
      )
