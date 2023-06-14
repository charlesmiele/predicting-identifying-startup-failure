import pandas as pd

# Read the CSV file
df = pd.read_csv('input.csv')

# Perform any desired operations on the data
# For example, let's assume we want to add 1 to each value in the 'value' column
df['value'] = df['value'] + 1

# Write the modified DataFrame to a new CSV file
df.to_csv('output.csv', index=False)

print("Output CSV file generated successfully.")
