# How to "grants_map"

This repo is the home of the grants mapping project.

## Important files

```./Data/automation.sh```

The main shell script that runs the weekly fetching. Best run on Mondays. Steps:

1. runs ./scrape_data_latest.sh - fetches the latest release from the GrantConnect website. Scraped using Lynx browser and defaults.
2. runs ./Code/dataset_build_latest.py.
3. runs ./Code/asgs_names_latest.py.
4. cleans up the folders and removes temp files.
5. commits and pushes changes to remote.

```./Code/asgs_names_latest.py```

Cleans up **most** naming mismatches across datasets. Best updated over time.

```./Code/dataset_build.py```

Cleans the downloaded Excel and generates a csv file. This script contains the infamous inquirer - it forces us to have someone manually verifying councils that haven't been automatically (fuzzy-) matched. 

```./dashboard_st.py```

The streamlit script for the dashboard. Streamlit config files are in ./.streamlit

## Getting started

1. set up a Python environment using ./requirements.txt.
2. install Lynx 
```shell
sudo apt update && sudo apt install lynx
```
3. enable execution permissions for the scripts  
```shell
cd ./data
chmod +x automation.sh
chmod +x scrape_data_latest.sh
chmod +x scrape_data_all.sh
```
4. set git up
```shell
git config --global user.email "<email>"
git config --global user.name "<cool name>"
```
5. run ./Data/automation.sh every Monday
```shell
cd ./data
./automation.sh
```


