import subprocess, re

init_process = subprocess.run(["ls"], capture_output=True, text=True)
file_list = init_process.stdout.split("\n")
delete_pattern = r"\.html|\.txt"

for file_name in file_list:
    if re.search(delete_pattern, file_name):
        subprocess.run(["rm", f"{file_name}"])
