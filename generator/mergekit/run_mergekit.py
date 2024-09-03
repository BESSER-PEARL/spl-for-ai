import os
import streamlit as st
import yaml

from huggingface_hub import ModelCard, HfApi
from jinja2 import Template


def run_mergekit(run_config: dict):
    st.info('Cloning mergekit')

    os.system('git clone https://github.com/arcee-ai/mergekit.git')

    if run_config['mergekit_branch'] == "main":
        cli = f"mergekit-yaml config.yaml {run_config['directory']} --copy-tokenizer"
    elif run_config['mergekit_branch'] == "mixtral":
        os.system('pip install transformers')
        cli = f"mergekit-moe config.yaml {run_config['directory']} --copy-tokenizer"

    os.system(f'cd mergekit && git checkout {run_config["mergekit_branch"]} && pip install .')

    if run_config['runtime'] == "CPU":
        cli += " --allow-crimes --out-shard-size 1B --lazy-unpickle"
    elif run_config['runtime'] == "GPU":
        cli += " --cuda --low-cpu-memory"
    if run_config['trust_remote_code']:
        cli += " --trust-remote-code"

    st.info(f'Running mergekit with command {cli}')

    with st.spinner('Running'):
        os.system(cli)

    st.info(f'Run completed')

    with st.spinner('Uploading to Hugging Face'):
        if run_config['upload_to_hf']:
            upload_huggingface(run_config)
            st.info(f'Uploaded to Hugging Face')


def upload_huggingface(run_config: dict):
    if run_config['mergekit_branch'] == "main":
        template_text = """
---
license: {{ license }}
base_model:
{%- for model in models %}
  - {{ model }}
{%- endfor %}
tags:
- merge
- mergekit
{%- for model in models %}
- {{ model }}
{%- endfor %}
---

# {{ model_name }}

{{ model_name }} is a merge of the following models using [Mergekit](https://github.com/arcee-ai/mergekit):

{%- for model in models %}
* [{{ model }}](https://huggingface.co/{{ model }})
{%- endfor %}

## 🧩 Configuration

```yaml
{{- yaml_config -}}
```

## 💻 Usage

```python
!pip install -qU transformers accelerate

from transformers import AutoTokenizer
import transformers
import torch

model = "{{ username }}/{{ model_name }}"
messages = [{"role": "user", "content": "What is a large language model?"}]

tokenizer = AutoTokenizer.from_pretrained(model)
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

outputs = pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
print(outputs[0]["generated_text"])
```
    """

        # Create a Jinja template object
        jinja_template = Template(template_text.strip())
        data = yaml.safe_load(run_config['yaml_config'])
        if "models" in data:
            models = [data["models"][i]["model"] for i in range(len(data["models"])) if
                      "parameters" in data["models"][i]]
        elif "parameters" in data:
            models = [data["slices"][0]["sources"][i]["model"] for i in range(len(data["slices"][0]["sources"]))]
        elif "slices" in data:
            models = [data["slices"][i]["sources"][0]["model"] for i in range(len(data["slices"]))]
        else:
            raise Exception("No models or slices found in yaml config")

        # Fill the template
        content = jinja_template.render(
            license=run_config['license'],
            model_name=run_config['model_name'],
            models=models,
            yaml_config=run_config['yaml_config'],
            username=run_config['username'],
        )

    elif run_config['mergekit_branch'] == "mixtral":
        template_text = """
---
license: {{ license }}
base_model:
{%- for model in models %}
  - {{ model }}
{%- endfor %}
tags:
- moe
- frankenmoe
- merge
- mergekit
{%- for model in models %}
- {{ model }}
{%- endfor %}
---

# {{ model_name }}

{{ model_name }} is a Mixture of Experts (MoE) made with the following models using [Mergekit](https://github.com/arcee-ai/mergekit):

{%- for model in models %}
* [{{ model }}](https://huggingface.co/{{ model }})
{%- endfor %}

## 🧩 Configuration

```yaml
{{- yaml_config -}}
```

## 💻 Usage

```python
!pip install -qU transformers bitsandbytes accelerate

from transformers import AutoTokenizer
import transformers
import torch

model = "{{ username }}/{{ model_name }}"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    model_kwargs={"torch_dtype": torch.float16, "load_in_4bit": True},
)

messages = [{"role": "user", "content": "Explain what a Mixture of Experts is in less than 100 words."}]
prompt = pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
outputs = pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
print(outputs[0]["generated_text"])
```
    """

        # Create a Jinja template object
        jinja_template = Template(template_text.strip())

        # Fill the template
        data = yaml.safe_load(run_config['yaml_config'])
        models = [model['source_model'] for model in data['experts']]

        content = jinja_template.render(
            model_name=run_config['model_name'],
            models=models,
            yaml_config=run_config['yaml_config'],
            username=run_config['username'],
            license=run_config['license']
        )

    # Save the model card
    card = ModelCard(content)
    card.save(f"{run_config['directory']}/README.md")

    # Defined in the secrets tab in Google Colab
    api = HfApi(token=run_config['hf_token'])

    # Upload merge folder
    api.create_repo(
        repo_id=f"{run_config['username']}/{run_config['model_name']}",
        repo_type="model",
        exist_ok=True,
    )
    api.upload_folder(
        repo_id=f"{run_config['username']}/{run_config['model_name']}",
        folder_path=run_config['directory'],
    )