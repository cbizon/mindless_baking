# mindless_baking
Experimenting with auto-croissants

Takes in a list of sites to browse. It uses crawl4ai to pull particular pages based on the kinds of pages we see when ingesting sources ("download", "license", "faq", etc).

Then we have a few prompts that send the text of those pages to an LLM and asks it to extract the information that we want to put into a croissant file. At the moment these are things like title, citation, etc focusing on that level 0 citation.

## Notes

It's fairly manual at the moment, and theres nothing that tries to pick the best result for anything out of the possible answers from different pages.

Also, crawl4ai has some bugs - their BestFirstCrawlingStrategy seems to have a bug where it returns the worst first (using a priority queue the wrong way). So this only works with my locally hacked version.

It's using OpenAI at the moment, the batching stuff works. But honestly it's just as easy at the moment to make the batch with this code and then post the batch through the website, which I did a few times.

Also note that the response from the LLM should end in good JSON but it is often messed up so that the "_final.jsonl" files are not valid.

But even with all of those early warts, this is the kind of thing that comes out, in this case for DrugCentral:

```angular2html
[
{ "name": "DrugCentral 2023" },
{"description": null},
{ "cite": "Drugcentral 2023 NAR Article" },
{ "license": "https://drugcentral.org/privacy" },
{ "description": "DrugCentral is online drug information resource created and maintained by Division of Translational Informatics at University of New Mexico in collaboration with the IDG. DrugCentral provides information on active ingredients chemical entities, pharmaceutical products, drug mode of action, indications, pharmacologic action. We monitor FDA, EMA, and PMDA for new drug approval on regular basis to ensure currency of the resource. Limited information on discontinued and drugs approved outside US is also available however regulatory approval information can't be verified." },
{ "cite": "https://doi.org/10.1093/nar/gkac1085" },
{ "license": "https://drugcentral.org/privacy" },
{"description": null},
{ "cite": "http://dx.doi.org/10.1093/nar/gkw993" },
{ "license": "https://drugcentral.org/privacy" },
},
{ "cite": "http://dx.doi.org/10.1093/nar/gkw993" },
{ "license": "https://drugcentral.org/privacy" },
{"description": null },
{ "cite": "http://dx.doi.org/10.1093/nar/gkw993" },
{ "license": "Creative Commons BY-SA 4.0" },
{"description": null },
{ "cite": "http://dx.doi.org/10.1093/nar/gkw993" },
{ "license": "https://drugcentral.org/privacy" }]
```
We get a decent name and a good description.  The citation is correct and retrieved from a lot of pages.  There is a cite that is not great ("Drugcentral 2023 NAR Article") coming from one page.
Also the license is interesting.  The "privacy" page states that the license is CC BY-SA 4.0 and parsing that page gives the right answer. But we also get a bunch of results that are the URL for the page where that is stated rather than the answer itself.