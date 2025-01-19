To install dependencies:

```pip install -r requirements.txt```


The best performing lora adapter is available here : 

https://drive.google.com/drive/folders/173MeX6MMBOsOgSMlepkRkpQczmjzqaGm?usp=sharing

To launch model with it download it and run :

vllm serve unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit  --dtype float16 --gpu-memory-utilization 0.8 --max-model-len 13500 --quantization bitsandbytes  --load-format bitsandbytes --max-lora-rank 64  --served-model-name meta-llama/Llama-3.1-8B-Instruct --trust-remote-code  --enable-lora  --lora-modules lora_increased=./lorai_adapter_llama8b_5epochs_nrs

Then you will be able to run dspy_optimization.ipynb, where the inference is.