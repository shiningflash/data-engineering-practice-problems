---
id: 5
title: Merging Messy CSVs from Multiple Partners
category: Data Integration
topics: [CSV, column mapping, date parsing, file walk]
difficulty: Medium
solution: solution.py
---

# Problem 5 — Merging Messy CSVs from Multiple Partners

**Scenario:**
Every Monday morning, your team receives a folder of CSV files from different partners. Each file contains the same kind of data (customer signups), but every partner names their columns differently. Some files have extra columns you don’t care about, some have missing values, and the date format is never consistent.

Here is what three example files might look like:

```
# partner_a.csv
customer_id,full_name,email,signup_date
201,Alice Lee,alice@a.com,2025-10-01
202,Bob Khan,bob@a.com,2025-10-02
```

```
# partner_b.csv
CustomerID,Name,Email,SignupDate,Country
301,Carol Tan,carol@b.com,2025-10-01,SG
302,,daniel@b.com,2025-10-04,MY
```

```
# partner_c.csv
cust_id,name,email_addr,joined_on
401,Eve Patel,eve@c.com,01/10/2025
402,Frank Wu,frank@c.com,02/10/2025
```

Typical issues you will see:

* Same field has different names (`customer_id`, `CustomerID`, `cust_id`)
* Date formats differ (`2025-10-01` vs `01/10/2025`)
* Some files have extra columns (like `Country`) that you don’t need
* Some rows have missing values
* The folder may contain hundreds of files

The warehouse team wants a single clean CSV they can load straight into BigQuery.

---

### Your Task:

Write a Python program that:

1. Reads every CSV file inside a folder called `partner_csvs/`.
2. Maps the different column names into one standard schema:

| Standard column | Possible source names              |
| --------------- | ---------------------------------- |
| customer_id     | customer_id, CustomerID, cust_id   |
| name            | name, Name, full_name              |
| email           | email, Email, email_addr           |
| signup_date     | signup_date, SignupDate, joined_on |

3. Converts `signup_date` to `YYYY-MM-DD`.
4. Skips rows that are missing `email` or `customer_id`.
5. Replaces a missing `name` with `"Unknown"`.
6. Adds a `source_file` column so you can trace which file each row came from.
7. Writes everything into a single output file called `all_customers.csv`.

**Example Output (all_customers.csv):**

```
customer_id,name,email,signup_date,source_file
201,Alice Lee,alice@a.com,2025-10-01,partner_a.csv
202,Bob Khan,bob@a.com,2025-10-02,partner_a.csv
301,Carol Tan,carol@b.com,2025-10-01,partner_b.csv
302,Unknown,daniel@b.com,2025-10-04,partner_b.csv
401,Eve Patel,eve@c.com,2025-10-01,partner_c.csv
402,Frank Wu,frank@c.com,2025-10-02,partner_c.csv
```

---

### Bonus Challenges:

* Print a small summary at the end: how many files were read, total rows in, rows written, rows skipped.
* Move the column mapping into a small config dict (or YAML file) so a new partner can be added without touching the code.
* Handle GZIP compressed files (`.csv.gz`) too.
* Stream the writing so that even with 500 files you never hold everything in memory.

---

💡 **Hints:**

* Use `pathlib.Path.glob` to walk the folder.
* The `csv.DictReader` and `csv.DictWriter` make column renaming much easier than positional indexes.
* Build a reverse lookup table from partner column name to standard column name once, then reuse it.
* Keep the date parsing in its own small function so adding a new format later is easy.

---
