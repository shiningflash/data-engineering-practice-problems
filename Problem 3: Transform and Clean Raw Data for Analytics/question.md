## Problem 3: Transform and Clean Raw Data for Analytics

**Scenario:**
You receive raw user activity data from a partner API in a messy CSV file. The company wants to load it into a data warehouse (e.g., BigQuery or PostgreSQL) for analytics.

Here’s what the CSV looks like:

```
user_id,name,email,signup_date,last_login,total_purchases
101,John Doe,john@example.com,2024-12-01,2025-10-10,15
102,Jane Doe,,2025-01-15,2025-09-30,22
103,Bob Smith,bob@example,2024-11-20,2025-10-05,abc
104,,maria@example.com,2025-02-10,,30
```

But it’s full of **dirty and inconsistent data**:

* Missing `name` or `email`
* Invalid email format
* Non-numeric values in `total_purchases`
* Empty `last_login`
* Dates in wrong order (e.g., signup_date > last_login)

---

### Your Task:

Write a Python program that:

1. Reads the CSV file line by line (assume it’s large — can’t load into memory at once).
2. **Validates and cleans** the data:

   * Skip rows with missing `email` or invalid email format.
   * Replace missing `name` with `"Unknown"`.
   * Replace missing `last_login` with `"N/A"`.
   * Convert `total_purchases` to integer — if invalid, set it to `0`.
   * If `signup_date` is **after** `last_login`, mark a new column `is_date_valid` as `False`, else `True`.
3. Writes the cleaned data into a **new CSV file** called `cleaned_users.csv`.

**Example Output (cleaned_users.csv):**

```
user_id,name,email,signup_date,last_login,total_purchases,is_date_valid
101,John Doe,john@example.com,2024-12-01,2025-10-10,15,True
103,Bob Smith,bob@example,2024-11-20,2025-10-05,0,True
104,Unknown,maria@example.com,2025-02-10,N/A,30,False
```

---

### Bonus (if you want to go deeper like a senior engineer):

* Log how many rows were skipped and why.
* Keep a separate file (`invalid_rows.csv`) for skipped rows.
* Use a `pydantic` model for validation.

---

💡 **Hints for Interview Thinking:**

* Think about **streaming-style reads** (`csv` module or `DictReader`).
* Use **regex for email validation**.
* Be robust — assume bad inputs will appear often.
* Make your solution easy to extend (e.g., add more validation rules later).

---
