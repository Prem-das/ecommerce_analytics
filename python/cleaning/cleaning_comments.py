import pandas as pd

# Read the CSV file cleanly with pandas
df = pd.read_csv(r'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_order_reviews_dataset.csv')

# Replace embedded carriage returns and newlines inside comments with spaces
df['review_comment_message'] = df['review_comment_message'].str.replace('\r\n', ' ', regex=False).str.replace('\n', ' ', regex=False)
df['review_comment_title'] = df['review_comment_title'].str.replace('\r\n', ' ', regex=False).str.replace('\n', ' ', regex=False)

# Save the cleaned file
df.to_csv(r'C:\Users\premk\OneDrive\Documents\ecommerce_analytics\data\raw\olist_order_reviews_dataset_clean.csv', index=False)
print("Cleaned file saved successfully!")