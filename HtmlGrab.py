# Grabs raw html from a given link.
# Link must adhere to regex below.
# FIXME: Could add a way to instead of creating a file, simply return the html as a list of strings or something.
import requests, sys, re

app_id_regex = r"[0-9]+"
url_pattern = r"https?:\/\/[a-zA-Z0-9]+\.[a-zA-Z]+"

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Paste a Url: ")
    grabber(url)

def grab_from_id(app_id):
    url = f"https://store.steampowered.com/app/{app_id}/"
    grabber(url)
    
def grab(location):
    if re.match(app_id_regex, location):
        grab_from_id(location)
    elif re.match(url_pattern, location):
        grabber(location)

def grabber(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Error: {response.status_code}")
        exit()
    with open("outputs/output.html", "w") as file:
        print("Created output.html")
        file.write(html_content)

if __name__ == "__main__":
    main()

