from feature_model.metamodel import RootF, F

INF = 99999999

fm_parameter = (RootF('parameter'))

fm_dtype = (RootF('dtype'))

fm_base_model = (RootF('base_model')
                 .mandatory(F('model_reference'))
                 )

fm_model_reference = (RootF('model_reference')
                      .mandatory(F('path'))
                      )

fm_input_slice = (RootF('input_slice')
                  .mandatory(F.duplicate(fm_model_reference))
                  .mandatory(F('layer_range')
                             .mandatory(F('layer_ini'))
                             .mandatory(F('layer_end'))
                             )
                  .optional(F.duplicate(fm_parameter))
                  )

fm_output_slice = (RootF('output_slice')
                   .mandatory(F('sources')
                              .mandatory(F.duplicate(fm_input_slice, min=1, max=INF))
                              )
                   .optional(F.duplicate(fm_base_model))
                   .optional(F('residual_weight'))
                   .optional(F.duplicate(fm_parameter))
                   )

fm_input_model = (RootF('input_model')
                  .mandatory(F.duplicate(fm_model_reference))
                  .optional(F.duplicate(fm_parameter))
                  )


fm = (RootF('Composition')
      .mandatory(F('Composition tool')
                 .mandatory(F('Mergekit'))  # When we add other tools, this feature group will be alternative
                 )
      .mandatory(F('Composition configuration')
                 .alternative([F('MoE Config')
                               .mandatory(F.duplicate(fm_base_model))
                               .mandatory(F.duplicate(fm_dtype))
                               .mandatory(F('experts_per_token'))
                               .mandatory(F('gate_mode'))
                               .mandatory(F('Expert', min=2, max=INF)
                                          .optional(F('noise_scale'))
                                          .mandatory(F('positive_prompt', min=1, max=INF))
                                          .optional(F('negative_prompt', min=0, max=INF))
                                          .mandatory(F('source_model')
                                                     .mandatory(F.duplicate(fm_model_reference)))
                                          ),
                               F('Merge Config')
                               .mandatory(F('merge_method'))
                               .alternative([F('slices')
                                             .mandatory(F.duplicate(fm_output_slice, min=1, max=INF)),
                                             F('models')
                                             .mandatory(F.duplicate(fm_input_model, min=1, max=INF)),
                                             ])
                               .optional(F.duplicate(fm_parameter))
                               .optional(F.duplicate(fm_base_model))
                               .optional(F.duplicate(fm_dtype))
                               .optional(F('tokenizer_source'))
                               ])
                 )
      )
