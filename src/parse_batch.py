import json

# Checked on 2025-04-03
MODEL_COSTS = {
    "gpt-4o": (1.25, 5.0),
    "gpt-4o-mini": (0.075, 0.3),
    "gpt-4.5-preview": (37.50, 75.00),
    "o1": (7.5, 30),
    "o1-pro": (75., 300.),
    "o1-mini": (0.55, 2.2)
}

def go(batch_output_file,model_name):
    prompt_tokens = 0
    completion_tokens = 0
    batch_final = batch_output_file[:-6] + "_final.json"
    with open(batch_output_file,"r") as inf, open(batch_final,"w") as outf:
        outf.write("[\n")
        first = True
        for line in inf:
            if not first:
                outf.write(",\n")
            else:
                first = False
            result = json.loads(line)
            #input_score = result["custom_id"].split("-")[-1]
            try:
                response = result["response"]["body"]["choices"][0]["message"]["content"]
            except Exception as e:
                print(e)
                continue
            rlines = response.split("\n")
            outf.write(rlines[-2])
            usage = result["response"]["body"]["usage"]
            prompt_tokens += usage["prompt_tokens"]
            completion_tokens += usage["completion_tokens"]
        outf.write("]")
    # The cost of this model is $0.075 / 1M input tokens and $0.300 / 1M output tokens
    for model in MODEL_COSTS:
        incost, outcost = MODEL_COSTS[model]
        if model == model_name:
            print(f"Cost (*{model}): ${incost * prompt_tokens / 1e6 + outcost * completion_tokens / 1e6}")
        else:
            print(f"Cost ({model}): ${incost * prompt_tokens / 1e6 + outcost * completion_tokens / 1e6}")

if __name__ == "__main__":
    #go("outputs/name_batch_file_output.jsonl","gpt-4o")
    #go("outputs/batch_67eea6eff9d88190bd3c3f44d7077168_output.jsonl","gpt-4o")
    #go("outputs/batch_67eec857167c81909bb498dd81223440_output.jsonl","gpt-4o-mini")
    #go("outputs/batch_67f02d02d3108190a7607e6ac68a7ec5_output.jsonl","gpt-4o-mini")
    go("outputs/batch_67f5162ef1748190b41dd698b03d5865_output.jsonl","gpt-4o-mini")
