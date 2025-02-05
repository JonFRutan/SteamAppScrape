# Cuts a div out of a provided html file.
import sys, re
import time

file_name = None
div_pattern = None

if len(sys.argv) > 1:
    file_name = sys.argv[1]
    if len(sys.argv) > 2:
        div_pattern = sys.argv[2]

if file_name == None:
    file_name = input("File name: ")

if div_pattern == None:
    div_pattern = input("Provide the div id: ")

#FIXME, a div could have a "class" following it instead, this may be worth adding
div_pattern = f"<div id=\"{div_pattern}\""
div_pattern = rf"{div_pattern}"

#See if the file exists
no_file = True

while no_file:
    try:
        with open(file_name, "r") as file:
            html_content = file.read().split("\n")
            break
    # If the file isn't found, check the outputs folder
    except IOError as e:
        try:
            with open(f"outputs/{file_name}", "r") as file:
                html_content = file.read().split("\n")
                break
        # If the file still isn't found, loop
        except IOError as e:
            print("File not found, or another error.")
            file_name = input("Try entering the file path again: ")

#doc_head = html_content[0] 
#html_pattern = r"<!DOCTYPE html>"

#if re.match(html_pattern, doc_head):
#    print("HTML identified")
#else:
#    print("File is not HTML or another error occured.")

line_count = 0

for line in html_content:
    line_count+=1
    if re.search(div_pattern, line):
        break

html_content = html_content[line_count-1:]
first_line = line_count
#print(line_count)

# We know where the div begins, now we need to find where it ends.
div_start = r"<div"
div_end   = r"div>"
div_layer = 0
line_count = 0

for line in html_content[1:]:
    if re.search(div_start, line):
        div_layer += 1
    if re.search(div_end, line):
        if div_layer == 0:
            line_count+=1
            break
        else:
            div_layer -= 1
    line_count+=1

html_content = html_content[:line_count+1]
print(f"Cropped div from lines {first_line} to {first_line+line_count}\nCreated final.txt")

with open("outputs/final.txt", "w") as output_file:
    output_file.writelines(line + "\n" for line in html_content)

# Done
