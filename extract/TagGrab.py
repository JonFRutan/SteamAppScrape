# I found that all of the tags are kept in a structure called "InitAppTagModal"
# Originally the plan was to cut the div out (using DivCut.py), however, this will be faster.

import re, sys, HtmlGrab

app_id_regex = r"[0-9]+"
link_regex = r"https?:\/\/[a-zA-Z0-9]+\.[a-zA-Z]+"
filepath_regex = r"^(?:[a-zA-Z]:)?[\\/](?:[^<>:\"|?*\n]+[\\/]?)*[^<>:\"|?*\n]*$"
if len(sys.argv) == 0:
    print("Usage:\n>python TagGrab.py (filepath) \n>python TagGrab.py (steam page url) \nOR \n>python TagGrab.py (steam app id)")

if len(sys.argv) > 1:
    if re.match(app_id_regex, sys.argv[1]):
        HtmlGrab.grab_from_id(sys.argv[1])
    elif re.match(link_regex, sys.argv[1]):
        HtmlGrab.grabber(sys.argv[1])

html_input = "outputs/output.html"
tag_start_pattern = r"InitAppTagModal"

with open(html_input, "r") as file:
    div_contents = file.read().split("\n")

line_count = 0
for line in div_contents:
    line_count += 1
    if re.search(tag_start_pattern, line):
        # Interestingly, all tags are kept on a single line.
        tags = div_contents[line_count].split("},{")
        #print(f"Tags found at line {line_count+1}")    

tag_count = len(tags)
# Clean up the first tag...
tags[0] = tags[0].strip()
tags[0] = tags[0][2:]
# Clean up the last tag...
tags[tag_count-1] = tags[tag_count-1][:len(tags[tag_count-1])-3]

print(f"{tag_count} tags found on line {line_count+1}")
for line in tags:
    print(line)
