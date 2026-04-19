import snowflake.connector
import pandas as pd

API_KEY = "D2SY9ZC818J5DSND"

# Snowflake connection
conn = snowflake.connector.connect(
    user='ESHWARDUDALA0',
    password='Telangana@5617',
    account='HZCTIQT-PRC84963',
    warehouse='COMPUTE_WH',
    database='FINANCE_AI',
    schema='CORE'
)

cursor = conn.cursor()

# Load the customer support data from CSV
csv_file_path = 'Customer_support_data.csv'
df = pd.read_csv(csv_file_path)

print("Data loaded successfully!")
print("Dataset shape:", df.shape)
print("\nFirst 5 records:")
print(df.head())

print("\nColumn names and types:")
print(df.dtypes)

# Create the table schema
table_name = "CUSTOMER_SUPPORT"

# Drop table if it exists (optional)
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# Create table with appropriate schema
create_table_sql = f"""
CREATE TABLE {table_name} (
    UNIQUE_ID VARCHAR(255),
    CHANNEL_NAME VARCHAR(100),
    CATEGORY VARCHAR(100),
    SUB_CATEGORY VARCHAR(100),
    CUSTOMER_REMARKS VARCHAR(1000),
    ORDER_ID VARCHAR(255),
    ORDER_DATE_TIME VARCHAR(100),
    ISSUE_REPORTED_AT VARCHAR(100),
    ISSUE_RESPONDED VARCHAR(100),
    SURVEY_RESPONSE_DATE VARCHAR(100),
    CUSTOMER_CITY VARCHAR(100),
    PRODUCT_CATEGORY VARCHAR(100),
    ITEM_PRICE FLOAT,
    CONNECTED_HANDLING_TIME FLOAT,
    AGENT_NAME VARCHAR(100),
    SUPERVISOR VARCHAR(100),
    MANAGER VARCHAR(100),
    TENURE_BUCKET VARCHAR(100),
    AGENT_SHIFT VARCHAR(100),
    CSAT_SCORE INTEGER
)
"""

print("\nCreating table...")
cursor.execute(create_table_sql)
print(f"Table '{table_name}' created successfully!")

# Load data into Snowflake
print("\nLoading data into Snowflake...")

# Prepare the data for insertion
for index, row in df.iterrows():
    insert_sql = f"""
    INSERT INTO {table_name} VALUES (
        '{row.get('Unique id', '')}',
        '{row.get('channel_name', '')}',
        '{row.get('category', '')}',
        '{row.get('Sub-category', '')}',
        '{str(row.get('Customer Remarks', '')).replace("'", "''")}',
        '{row.get('Order_id', '')}',
        '{row.get('order_date_time', '')}',
        '{row.get('Issue_reported at', '')}',
        '{row.get('issue_responded', '')}',
        '{row.get('Survey_response_Date', '')}',
        '{row.get('Customer_City', '')}',
        '{row.get('Product_category', '')}',
        {row.get('Item_price') if pd.notna(row.get('Item_price')) else 'NULL'},
        {row.get('connected_handling_time') if pd.notna(row.get('connected_handling_time')) else 'NULL'},
        '{row.get('Agent_name', '')}',
        '{row.get('Supervisor', '')}',
        '{row.get('Manager', '')}',
        '{row.get('Tenure Bucket', '')}',
        '{row.get('Agent Shift', '')}',
        {row.get('CSAT Score') if pd.notna(row.get('CSAT Score')) else 'NULL'}
    )
    """
    cursor.execute(insert_sql)

conn.commit()
print(f"Data loaded successfully! Total records: {len(df)}")

# Verify the data
verify_sql = f"SELECT COUNT(*) as RECORD_COUNT FROM {table_name}"
cursor.execute(verify_sql)
result = cursor.fetchone()
print(f"\nVerification - Total records in table: {result[0]}")

print("\nSample records from Snowflake:")
cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
for row in cursor.fetchall():
    print(row)


