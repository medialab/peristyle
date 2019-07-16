import csv

fs = open("../tables/sample_filtered_with_features.csv", "r")
reader = csv.DictReader(fs)

i = 0
for row in reader:
    if row["filter"] == "False":
        i += 1
        print(row["stories_id"])
        fs_name = "../sample/" + row["stories_id"] + ".txt"
        fd_name = "./peristyle_db/" + row["stories_id"] + ".txt"
        with open(fs_name, "r") as f:
            txt = f.read()
        with open(fd_name, "w") as f:
            f.write(txt)

print(i)
fs.close()