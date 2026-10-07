
import os
import pandas as pd
import numpy as np

#Data is true
os.makedirs("data", exist_ok=True)

#Place
geo_data=[

    ("1106", "Lisbon", "Greater Lisbon", "Lisbon Metropolitan Area"),
    ("1312", "Porto", "Porto Metropolitan Area", "North"),
    ("1105", "Cascais", "Greater Lisbon", "Lisbon Metropolitan Area"),
    ("0805", "Faro", "Algarve", "Algarve"),
    ("0105", "Coimbra", "Coimbra Region", "Center")
]

#Converts raw records into a structure two dimensional table with explicit column headers
df_geo = pd.DataFrame(
    geo_data,
    columns=[["geo_id", "city/village", "nuts_iii", "nuts_ii"]]

)

#Writes the DataFrame to disk without adding default numerical row indices
df_geo.to_csv("data/dim_geografy.csv", index=False)
print("dim_geografy.cvs created successfully!")

#Time dimension (Quarters from 2022 to 2024)

# We create an empty list where we will collect all our quarters.
time_records = []

# Loop 1: Go through each year one by one
for year in [2022, 2023, 2024]:
    # Loop 2: For each year, go through 4 quarters (Q1, Q2, Q3, Q4)
    for quarter in [1, 2, 3, 4]:
        # Glue the year and quarter together to make an ID (e.g. '2022Q1')
        time_records.append({
            "time_id": f"{year}Q{quarter}",
            "year": year,
            "quarter": quarter
        })

# Turn our list of quarters into a clean table
df_time = pd.DataFrame(time_records)

# Save it to disk
df_time.to_csv("data/dim_time.csv", index=False)
print("2. dim_time.csv saved!")


# -------------------------------------------------------------
# STEP 5: CREATE THE HOUSING TABLE (fact_housing)
# -------------------------------------------------------------

# A dictionary { } matches each city with its starting price per square meter (€/m2)
base_prices = {
    "Lisbon": 4100,
    "Cascais": 3800,
    "Porto": 2800,
    "Faro": 2200,
    "Coimbra": 1600
}

# 'seed(42)' locks random numbers in place so both you and I get the exact same numbers
np.random.seed(42)

housing_records = []

# Go through each city in our geography table
for _, geo_row in df_geo.iterrows():
    city_name = geo_row["city/village"]
    city_id = geo_row["geo_id"]
    starting_price = base_prices[city_name]

    # For each city, go through all 12 quarters (from 2022Q1 to 2024Q4)
    # 'idx' is just a step counter: 0, 1, 2, 3 ... up to 11
    for idx, time_item in enumerate(time_records):
        time_id = time_item["time_id"]
        quarter = time_item["quarter"]

        # AS TIME PASSES, PRICES GO UP:
        # Every new quarter (idx) adds 1.5% to the price.
        # np.random adds a tiny wobble so every number isn't perfectly stiff.
        growth_multiplier = 1.0 + (idx * 0.015) + np.random.uniform(-0.02, 0.03)
        final_price_sqm = round(starting_price * growth_multiplier, 2)

        # SEASONS AFFECT SALES VOLUME:
        # Fewer houses sell in the cold winter (Q1 = 80%), more sell in warmer months (110%)
        if quarter == 1:
            season_factor = 0.8
        else:
            season_factor = 1.1

        # Pick a random number of house sales between 300 and 2500, then adjust for the season
        house_sales = int(np.random.randint(300, 2500) * season_factor)

        # TOTAL MONEY:
        # Multiply sales * price per sqm * average house size (95 sqm)
        # Divide by 1000 so the number is in thousands of euros
        total_k_eur = round((house_sales * final_price_sqm * 95) / 1000, 2)

        # Put this calculated row into our records list
        housing_records.append({
            "geo_id": city_id,
            "time_id": time_id,
            "median_price_sqm": final_price_sqm,
            "transaction_count": house_sales,
            "total_volume_k_eur": total_k_eur
        })

# Turn all rows into a table and save it
df_housing = pd.DataFrame(housing_records)
df_housing.to_csv("data/fact_housing.csv", index=False)
print("3. fact_housing.csv saved!")


# -------------------------------------------------------------
# STEP 6: CREATE THE TOURISM TABLE (fact_tourism)
# -------------------------------------------------------------

tourism_records = []

# Again, loop through every city and every quarter
for _, geo_row in df_geo.iterrows():
    city_id = geo_row["geo_id"]
    region = geo_row["nuts_ii"]

    for time_item in time_records:
        time_id = time_item["time_id"]
        quarter = time_item["quarter"]

        # SUMMER IS PEAK TOURISM SEASON:
        # Q3 (July, August, September) gets a big boost (1.6x)
        # Q2 (Spring) gets a slight boost (1.2x)
        # Winter/Autumn stay normal (0.8x)
        if quarter == 3:
            season_boost = 1.6
        elif quarter == 2:
            season_boost = 1.2
        else:
            season_boost = 0.8

        # BIG CITIES GET MORE TOURISTS:
        if region == "Lisbon Metropolitan Area":
            base_tourists = 900000
        elif region == "Algarve":
            base_tourists = 700000
        else:
            base_tourists = 200000

        # Calculate hotel overnight stays with a bit of realistic randomness
        overnight_stays = int(base_tourists * season_boost * np.random.uniform(0.85, 1.15))

        # Each tourist spends between 70€ and 95€ per night on accommodation
        hotel_revenue_eur = round(overnight_stays * np.random.uniform(70, 95), 2)

        # Save the row
        tourism_records.append({
            "geo_id": city_id,
            "time_id": time_id,
            "overnight_stays": overnight_stays,
            "total_revenue_eur": hotel_revenue_eur
        })

# Turn tourism rows into a table and save it
df_tourism = pd.DataFrame(tourism_records)
df_tourism.to_csv("data/fact_tourism.csv", index=False)
print("4. fact_tourism.csv saved!")
print("\nAll 4 CSV files are ready in your 'data/' folder!")