import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sqlite3

url = "https://admissions.northwestern.edu/academics/majors-minors"

response = requests.get(url)
tables = pd.read_html(response.text)
df = tables[0]

# Cleaning whitespaces
df.columns = df.columns.str.strip()
df['Academic Programs'] = df['Academic Programs'].str.strip()
df['Options Offered'] = df['Options Offered'].str.strip()

def extract_options(text):
    return re.findall(r'(Major|Minor|Adjunct Major|Certificate)', text)
df['options'] = df['Options Offered'].apply(lambda x: extract_options(x))
df["options"] = df["options"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
df = df[["Academic Programs", "options", "School"]]
df.rename(columns = {"Academic Programs": "academic_programs", "School": "school"})
df.reset_index(drop=True, inplace=True)
df.insert(0, "id", df.index + 1)

conn = sqlite3.connect("programs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY,
    academic_programs TEXT,
    options TEXT,
    school TEXT
)
""")

insert_query = "INSERT INTO programs (id, academic_programs, options, school) VALUES (?, ?, ?, ?)"
cursor.executemany(insert_query, df.values.tolist())

conn.commit()
conn.close()