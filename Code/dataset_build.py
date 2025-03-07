import pandas as pd
import glob
from pprint import pprint

files = glob.glob('../Data/Grants Archive/GrantConnect*.xlsx')

print("Reading files...")

grants = pd.concat([pd.read_excel(f, header=2) for f in files], ignore_index=True)

print("Cleaning data...")

grants = grants[grants["Agency"] != "Australian Securities and Investments Commission"]

removal_tags = r"service|care| inc|incorporated|business|technologies|national|company|school|health|pty|ltd|intl|international|college|institute|local|university|church|uca |arts |private|limited|trust|hospital|aboriginal corporat| lands* council|association|centre|federation|australia|community|cancer"

grants = grants[~grants["Recipient Name"].str.contains(removal_tags, case=False, na=True)]

councils = grants[grants["Recipient Name"].str.contains(r"council|shire|city", case=False, na=True)]

print("Finding LGAs...")

lgas = pd.read_csv("../Data/Training Data/ALGA Mail List.csv", encoding='latin1')
council_names = lgas["COUNCIL"].dropna().to_list()

from thefuzz import process
from thefuzz import fuzz

def similarity(name):
    tup = process.extractOne(name, council_names, scorer=fuzz.partial_ratio, score_cutoff=100)
    return tup[0] if tup else None

councils["Assigned LGA"] = councils["Recipient Name"].str.lower().apply(similarity)

print("Finding missing LGAs...")

import inquirer

def request_name(name):

    names_i = sorted(council_names.copy()) 
    name = name.lower()

    t = 95

    answer = "Other"

    choices = []

    temp_name = name.replace("town", "").replace("council", "").replace("city", "").replace("shire", "").replace("municipality", "").replace("of", "").replace("corporation", "").replace("/", " ").replace("the", "").replace("valley", "").replace("mount", "").replace("regional", "").strip()

    while answer == "Other" and t > 50:

        names_i = [i for i in names_i if i not in choices]

        if t > 75:
            choices = [c for c in names_i if fuzz.partial_ratio(temp_name, c.lower()) > t]
            
            if len(choices) == 0:
                t -= 5

                print("Lowering threshold to", t)

                continue

            choices.append("Delete")

        else:
            choices = ["Delete"] + names_i

        choices.append("Other")

        answer = inquirer.prompt([inquirer.List("name", 
                                            message=f"Enter the LGA for {name}",
                                            choices=choices
                                            )])
        
        answer = answer["name"]

        t -= 10

    if answer == "Other":
        answer = inquirer.prompt([inquirer.Text("name",
                                            message=f"Enter the LGA for {name} manually"
                                            )])
        answer = answer["name"]

        while answer.lower() not in council_names:
            print("The LGA you entered is not in the list. Please enter a valid LGA.")
            answer = inquirer.prompt([inquirer.Text("name",
                                            message=f"Enter the LGA for {name} manually"
                                            )])
            answer = answer["name"]

    return answer

missings = councils[councils["Assigned LGA"].isnull()]

print("Requesting missing LGAs...")

print(f"There are {missings['Recipient Name'].nunique()} missing LGAs")

for name in missings["Recipient Name"].unique():
    councils.loc[councils["Recipient Name"] == name, "Assigned LGA"] = request_name(name)

#councils["Assigned LGA"] = councils.apply(lambda x: request_name(x["Recipient Name"]) if x["Assigned LGA"] is None else x["Assigned LGA"], axis=1)

print("Saving data...")

councils = councils[councils["Assigned LGA"] != "Delete"]

#councils["Assigned LGA"] = councils["Assigned LGA"].apply(lambda x: x.)

councils.to_csv("../Data/Training Data/Grants Councils.csv", index=False)