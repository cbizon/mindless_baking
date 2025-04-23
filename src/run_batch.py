#Adapted from Matt Satusky's Batcher scripts
import time
import os
import json
from openai import OpenAI

api_key = os.environ.get("OPENAI_ROBOKOP_KEY")

def upload_batch_file(batch_file, description):
    client = OpenAI(api_key=api_key)
    batch_input_file = client.files.create(
        file=open(batch_file, "rb"),
        purpose="batch"
    )
    batch_input_file_id = batch_input_file.id

    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": description
        }
    )
    return batch

def retrieve_query(batch,outfile):
    client = OpenAI(api_key=api_key)
    batch_id = batch.id
    batch = client.batches.retrieve(batch_id)
    print(json.dumps(batch.to_dict(),indent=4))
    status = batch.status
    while status in ['validating', 'in_progress', 'finalizing']:
        time.sleep(5*60)
        batch_id = batch.id
        batch = client.batches.retrieve(batch_id)
        print(json.dumps(batch.to_dict(), indent=4))
        status = batch.status

    file_response = client.files.content(batch.output_file_id)
    with open(outfile,"w") as f:
        f.write(file_response.text)

def get_batch():
    client = OpenAI(api_key=api_key)
    batches = client.batches.list(limit=10)
    batch = batches.data[0]
    return batch

def go_batch(qtype):
    batch = upload_batch_file(f"outputs/{qtype}_batch_file.jsonl", qtype)
    print(batch)
    batch=get_batch()
    retrieve_query(batch, f"outputs/{qtype}_batch_file_output.jsonl")

if __name__ == "__main__":
    go_batch("name")
