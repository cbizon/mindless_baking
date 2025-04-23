#Adapted from Matt Satusky's Batcher scripts
import os
import json
from string import Template
from collections import defaultdict

api_key = os.environ.get("OPENAI_LITCOIN_KEY")

def create_batch_line(prompt,model_name, qid):
    d = {"custom_id": qid, "method": "POST", "url": "/v1/chat/completions",
         "body": {"model": model_name, "messages": [{"role": "user", "content": prompt }], "max_tokens": 1000}}
    return json.dumps(d)

def build_batch_file(prompt_file:str, question_types:list, markdown_files:list, model_name:str = "gpt-4o-mini", batchname:str = "all_names"):
    with open(prompt_file) as f:
        prompts = json.load(f)
    with open(f"outputs/{batchname}", "w") as outf:
        first = True
        for markdown_file, url in markdown_files:
            markdown_number = markdown_file.split("_")[-1].split(".")[0]
            with open(markdown_file) as f:
                markdown = f.read()
            if first:
                qid = f"{markdown_number}-name"
                write_prompt(qid, markdown, model_name, outf, prompts, "name", url)
                first=False
            for question_type in question_types:
                qid = f"{markdown_number}-{question_type}"
                write_prompt(qid, markdown, model_name, outf, prompts, question_type, url)


def write_prompt(qid, markdown, model_name, outf, prompts, question_type, url):
    prompt = prompts["preamble"]
    prompt += prompts[question_type]["question"]
    key = prompts[question_type]["key"]
    item = prompts[question_type]["item"]
    it = Template(prompts["instruction"])
    prompt += it.substitute({"key": key, "item": item, "url": url})
    prompt += markdown
    oline = create_batch_line(prompt, model_name, qid)
    outf.write(oline)
    outf.write("\n")


def create_name_batch(model_name, batchname):
    # For names, they better be in the top page or what are we doing
    crawls = os.listdir("crawls")
    markdowns = [ f"crawls/{crawl}/output_0.md" for crawl in crawls]
    build_batch_file("prompt.json", ["name"], markdowns, model_name, batchname)

def create_regular_batch(model_name, batchname, crawlname):
    # load index.txt from crawls/crawlname
    markdowns = []
    with open(f"crawls/{crawlname}/index.txt") as f:
        header = f.readline()
        # Always use the landing page
        entry = f.readline()
        parts = entry[:-1].split("\t")
        markdowns.append( (parts[0],parts[1]) )
        landing_page = parts[1]
        by_score = defaultdict(list)
        for line in f:
            x = line[:-1].split("\t")
            url = x[1]
            if not url.startswith(landing_page):
                # This is the case say when we have a site hosted within a larger site, like cam-kp is part of
                # github or chebi is part of ebi. If we land in github.com/exposures, the crawler will happily go
                # off to github.com/somethingelse because they share a domain, and we don't want that.
                continue
            score = -float(x[2])
            by_score[score].append( (x[0],x[1]) )
    # Sort the scores highest to lowest
    scores = sorted(by_score.keys(), reverse=True)
    # walk over all but the last score. These are usually trash
    for score in scores[:-1]:
        markdowns += by_score[score]
    build_batch_file("prompt.json", ["description", "citation", "license"], markdowns, model_name, batchname)


def go_batch():
    #create_name_batch("gpt-4o-mini","all_names_gpt_4o_mini.jsonl")
    #create_regular_batch("gpt-4o","CTD_level_0_gpt_4o.jsonl", "CTD")
    #create_regular_batch("gpt-4o-mini","CTD_level_0_4o_mini.jsonl", "CTD")
    create_regular_batch("gpt-4o-mini","DrugCentral_level_0_4o_mini_2.jsonl", "DrugCentral")

if __name__ == "__main__":
    go_batch()

