# Get the latest data
./scrape_data_latest.sh

#find ./ -name '*.xlsx' -exec sh -c "mv {} './Data/'" \;

# Build the dataset and clean

cd ../

python3 ./Code/dataset_build_latest.py

# Fix naming

python3 ./Code/asgs_names_latest.py

# Clean up Data

cd ./Data

rm "Grants_Councils_latest.csv"

find ./ -name '*.xlsx' -exec sh -c "mv {} './Archive/'" \;