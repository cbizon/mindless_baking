# mindless_baking
Experimenting with auto-croissants

Takes in a list of sites to browse. It uses crawl4ai to pull particular pages based on the kinds of pages we see when ingesting sources ("download", "license", "faq", etc).

Then we have a few prompts that send the text of those pages to an LLM and asks it to extract the information that we want to put into a croissant file. At the moment these are things like title, citation, etc focusing on that level 0 citation.

## Notes

It's fairly manual at the moment, and theres nothing that tries to pick the best result for anything out of the possible answers from different pages.

Also, crawl4ai has some bugs - their BestFirstCrawlingStrategy seems to have a bug where it returns the worst first (using a priority queue the wrong way). So this only works with my locally hacked version.
