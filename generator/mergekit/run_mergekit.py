import os
import streamlit as st


def run_mergekit(run_config: dict):
    st.info('Cloning mergekit')
    if run_config['mergekit_branch'] == "main":
        os.system('git clone https://github.com/arcee-ai/mergekit.git')
        os.system('cd mergekit && pip install -q -e .')
        cli = "mergekit-yaml config.yaml merge --copy-tokenizer"
    elif run_config['mergekit_branch'] == "mixtral":
        os.system('git clone -b mixtral https://github.com/arcee-ai/mergekit.git')
        os.system('cd mergekit && pip install -q -e .')
        os.system('pip install -qqq -qU transformers')
        cli = "mergekit-moe config.yaml merge --copy-tokenizer"

    if run_config['runtime'] == "CPU":
        cli += " --allow-crimes --out-shard-size 1B --lazy-unpickle"
    elif run_config['runtime'] == "GPU":
        cli += " --cuda --low-cpu-memory"
    if run_config['trust_remote_code']:
        cli += " --trust-remote-code"

    st.info(f'Running mergekit with command {cli}')

    with st.spinner('Running'):
        os.system(cli)
