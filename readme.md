# MapReduce Lab 3 - Complete Step-by-Step Guide

## Table of Contents
1. [Part 1: HPC Setup (One-Time)](#part-1-hpc-setup)
2. [Part 2: Exercise 1 - Word Count](#part-2-exercise-1-word-count)
3. [Part 3: Exercise 2 - SQL Translation](#part-3-exercise-2-sql-translation)
4. [Part 4: Exercise 3 - Basket Co-occurrence](#part-4-exercise-3-basket-co-occurrence)
5. [Part 5: Running Locally with mrjob](#part-5-running-locally-with-mrjob)

---

# Part 1: HPC Setup (One-Time)

## Step 1.1: Install Google Cloud SDK

### For macOS:

```bash
# Open Terminal

# Install using Homebrew
brew install google-cloud-sdk

# Verify installation
gcloud --version
```

**Expected output:**
```
Google Cloud SDK 456.0.0
bq 2.0.97
core 2024.01.01
gcloud 456.0.0
```

### For Windows:

```cmd
REM Open Command Prompt (NOT PowerShell)

REM Download installer from:
REM https://cloud.google.com/sdk/docs/install

REM Run GoogleCloudSDKInstaller.exe
REM Check "Install bundled Python"
REM Check "Run gcloud init"

REM After installation, open NEW Command Prompt

REM Verify installation
gcloud --version
```

---

## Step 1.2: Authenticate with Google Cloud

### macOS:
```bash
# Login to your NYU account
gcloud auth login
```

### Windows:
```cmd
REM Login to your NYU account
gcloud auth login
```

**What happens:**
- Browser opens automatically
- Login with your **netid@nyu.edu** account
- Click "Allow" to grant permissions
- You'll see "You are now authenticated"

**Verify authentication:**
```bash
# macOS/Windows (same command)
gcloud auth list
```

**Expected output:**
```
        Credentialed Accounts
ACTIVE  ACCOUNT
*       netid@nyu.edu
```

---

## Step 1.3: Configure SSH

### macOS:
```bash
# Configure SSH for Google Cloud
gcloud compute config-ssh
```

### Windows:
```cmd
REM Configure SSH for Google Cloud
gcloud compute config-ssh
```

**What this does:**
- Creates SSH keys automatically
- Adds configuration to `~/.ssh/config` (macOS) or `C:\Users\YourName\.ssh\config` (Windows)
- Allows easy connection to GCP instances

---

## Step 1.4: Connect to HPC Cluster

### Option A: Command Line (macOS/Windows)

```bash
# List available clusters
gcloud compute instances list
```

**Expected output:**
```
NAME               ZONE           MACHINE_TYPE   STATUS
nyu-dataproc-m     us-east1-b     n1-standard-4  RUNNING
```

```bash
# Connect to the cluster (replace with your instance name and zone)
gcloud compute ssh nyu-dataproc-m --zone=us-east1-b
```

**First time connecting:**
- Type `yes` when asked to continue connecting
- May ask to generate SSH keys (press Enter to accept defaults)
- May ask for passphrase (press Enter to skip)

**Success! You should see:**
```
username@nyu-dataproc-m:~$
```

### Option B: Web-Based SSH (Easiest)

1. Open browser and go to: **https://dataproc.hpc.nyu.edu/**
2. Login with your NYU credentials
3. Click **"SSH in Browser"**
4. Terminal opens in your browser!

**This is the easiest method and works on any OS!**

---

## Step 1.5: Setup GitHub SSH Keys (On the Cluster)

**Once connected to the cluster, run these commands:**

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "netid@nyu.edu"
# Press Enter 3 times (accept defaults, no passphrase)

# Display your public key
cat ~/.ssh/id_ed25519.pub
```

**Copy the entire output** (starts with `ssh-ed25519`)

**Add to GitHub:**
1. Go to: https://github.com/settings/keys
2. Click **"New SSH key"**
3. Title: `NYU HPC Cluster`
4. Paste your public key
5. Click **"Add SSH key"**

**Test the connection:**
```bash
ssh -T git@github.com
```

**Expected output:**
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## Step 1.6: Install mrjob (On the Cluster)

```bash
# Install mrjob
pip install mrjob --break-system-packages

# Verify installation
python3 -c "import mrjob; print('mrjob installed successfully')"
```

---

## Step 1.7: Setup Your Working Directory

```bash
# Create lab directory
mkdir -p ~/lab3
cd ~/lab3

# Create subdirectories
mkdir -p word_count
mkdir -p sql_filter
mkdir -p basket

# Verify structure
ls -la
```

**Expected output:**
```
drwxr-xr-x  basket/
drwxr-xr-x  sql_filter/
drwxr-xr-x  word_count/
```

---

# Part 2: Exercise 1 - Word Count

## Overview
**Input:** book.txt (text file)  
**Task:** Count frequency of each word  
**Output:** (word, count) pairs sorted by frequency  

---

## Step 2.1: Upload Input File to Cluster

### From macOS:
```bash
# Open Terminal on your Mac (separate from SSH session)

# Upload book.txt to cluster
gcloud compute scp /path/to/book.txt nyu-dataproc-m:~/lab3/word_count/ --zone=us-east1-b

# Example:
gcloud compute scp ~/Downloads/book.txt nyu-dataproc-m:~/lab3/word_count/ --zone=us-east1-b
```

### From Windows:
```cmd
REM Open Command Prompt (separate from SSH session)

REM Upload book.txt to cluster
gcloud compute scp C:\path\to\book.txt nyu-dataproc-m:~/lab3/word_count/ --zone=us-east1-b

REM Example:
gcloud compute scp C:\Users\YourName\Downloads\book.txt nyu-dataproc-m:~/lab3/word_count/ --zone=us-east1-b
```

---

## Step 2.2: Create Word Count Program

**On the cluster, create the mapper/reducer program:**

```bash
# Make sure you're in the right directory
cd ~/lab3/word_count

# Create the Python file
nano mr_wordcount.py
```

**Copy this code into the file:**

```python
#!/usr/bin/env python3
"""
Word Count MapReduce
Counts the frequency of each word in the input text
"""
from mrjob.job import MRJob
import re

# Regular expression to extract words (matches letters, numbers, apostrophes)
WORD_RE = re.compile(r"[\w']+")

class MRWordCount(MRJob):
    
    def mapper(self, _, line):
        """
        MAPPER FUNCTION
        
        Input: Each line of the text file
        Output: Emit (word, 1) for every word found
        
        Line-by-line explanation:
        """
        # Step 1: Extract all words from the line using regex
        # This finds all sequences of word characters and apostrophes
        words = WORD_RE.findall(line)
        
        # Step 2: Loop through each word found
        for word in words:
            # Step 3: Convert word to lowercase (for case-insensitive counting)
            # "The" and "the" should be counted as the same word
            word_lower = word.lower()
            
            # Step 4: Emit (word, 1) as a key-value pair
            # This means: "I found this word once"
            yield (word_lower, 1)
    
    def reducer(self, word, counts):
        """
        REDUCER FUNCTION
        
        Input: A word and ALL of its counts [1, 1, 1, 1, ...]
        Output: (word, total_count)
        
        Line-by-line explanation:
        """
        # Step 1: Sum all the 1s to get total count
        # counts is an iterator of all the 1s emitted by mappers
        # Example: if "the" appeared 46 times, counts = [1,1,1,...] (46 ones)
        total_count = sum(counts)
        
        # Step 2: Emit the word with its total count
        yield (word, total_count)

# This runs the MapReduce job when the script is executed
if __name__ == '__main__':
    MRWordCount.run()
```

**Save and exit:**
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

---

## Step 2.3: Test Locally (On the Cluster)

```bash
# Make sure you're in ~/lab3/word_count
cd ~/lab3/word_count

# Run locally (no Hadoop, just tests the code)
python3 mr_wordcount.py book.txt
```

**What you should see:**
```
"the"     46
"to"      41
"she"     36
"was"     33
"it"      30
"and"     28
...
```

**Save results to file:**
```bash
python3 mr_wordcount.py book.txt > wordcount_local.txt
```

**View top 20 most frequent words:**
```bash
cat wordcount_local.txt | sort -t$'\t' -k2 -nr | head -20
```

**Explanation of command:**
- `cat wordcount_local.txt` - Display file contents
- `sort -t$'\t'` - Sort using tab as delimiter
- `-k2` - Sort by 2nd column (the count)
- `-nr` - Numeric sort, reverse order (highest first)
- `head -20` - Show only top 20

---

## Step 2.4: Upload Input to HDFS

```bash
# Check if file already exists in HDFS
hadoop fs -ls

# If book.txt exists, remove it first
hadoop fs -rm book.txt

# Upload book.txt to HDFS
hadoop fs -put book.txt

# Verify upload
hadoop fs -ls
```

**Expected output:**
```
-rw-r--r--   3 username supergroup   30000 2024-02-11 10:30 book.txt
```

**Explanation:**
- HDFS = Hadoop Distributed File System
- It's separate from your regular Linux filesystem
- You must explicitly upload files to HDFS before running Hadoop jobs

---

## Step 2.5: Run on Hadoop

```bash
# CRITICAL: Remove old output directory if it exists
hadoop fs -rm -r wordcount_output

# Run MapReduce job on Hadoop
python3 mr_wordcount.py \
    -r hadoop \
    hdfs:///user/$USER/book.txt \
    -o hdfs:///user/$USER/wordcount_output
```

**Explanation of command:**
- `python3 mr_wordcount.py` - Your MapReduce script
- `-r hadoop` - Run on Hadoop (not locally)
- `hdfs:///user/$USER/book.txt` - Input file location in HDFS
- `-o hdfs:///user/$USER/wordcount_output` - Output directory in HDFS

**What happens:**
1. Your code is submitted to Hadoop
2. Hadoop splits the input across multiple nodes
3. Mappers run in parallel
4. Framework shuffles and sorts by key
5. Reducers run in parallel
6. Results are written to HDFS

**Monitor job progress:**
- Go to: https://dataproc.hpc.nyu.edu/jobhistory/
- Find your job in the list
- Click to see progress (map %, reduce %)

**Job output will show:**
```
Running step 1 of 1...
  packageJobJar: [] [/usr/lib/hadoop/hadoop-streaming.jar] ...
  Running job: job_1234567890123_0001
  map 0% reduce 0%
  map 33% reduce 0%
  map 67% reduce 0%
  map 100% reduce 0%
  map 100% reduce 33%
  map 100% reduce 100%
Job succeeded
```

---

## Step 2.6: Get Results from HDFS

```bash
# View what files were created
hadoop fs -ls wordcount_output

# You'll see multiple part files:
# part-00000
# part-00001
# _SUCCESS

# Merge all parts into one file
hadoop fs -getmerge wordcount_output wordcount_hadoop.txt

# View results
cat wordcount_hadoop.txt | head -20

# Sort by frequency
cat wordcount_hadoop.txt | sort -t$'\t' -k2 -nr | head -20
```

---

## Step 2.7: Download Results to Your Computer

### macOS:
```bash
# Open Terminal on your Mac (not SSH)

# Download results from cluster to your Mac
gcloud compute scp nyu-dataproc-m:~/lab3/word_count/wordcount_hadoop.txt ~/Downloads/ --zone=us-east1-b
```

### Windows:
```cmd
REM Open Command Prompt (not SSH)

REM Download results from cluster to your PC
gcloud compute scp nyu-dataproc-m:~/lab3/word_count/wordcount_hadoop.txt C:\Users\YourName\Downloads\ --zone=us-east1-b
```

---

## Step 2.8: Cleanup (Before Re-running)

```bash
# Remove HDFS output directory
hadoop fs -rm -r wordcount_output

# Remove HDFS input file (if you want to re-upload)
hadoop fs -rm book.txt

# Remove local result files
rm wordcount_local.txt wordcount_hadoop.txt
```

---

# Part 3: Exercise 2 - SQL Translation

## Overview
**Input:** movies.csv (movie_id, title, year, genre, rating)  
**Task:** Translate SQL query to MapReduce  
**Output:** Genre statistics (avg_rating, count) sorted by rating  

**SQL Query:**
```sql
SELECT genre, AVG(rating) as avg_rating, COUNT(*) as movie_count
FROM movies
WHERE year >= 2000
GROUP BY genre
HAVING COUNT(*) >= 10
ORDER BY avg_rating DESC;
```

---

## Step 3.1: Upload Input File

### macOS:
```bash
gcloud compute scp ~/Downloads/movies.csv nyu-dataproc-m:~/lab3/sql_filter/ --zone=us-east1-b
```

### Windows:
```cmd
gcloud compute scp C:\Users\YourName\Downloads\movies.csv nyu-dataproc-m:~/lab3/sql_filter/ --zone=us-east1-b
```

---

## Step 3.2: Create SQL Translation Program

```bash
# Navigate to directory
cd ~/lab3/sql_filter

# Create the program
nano mr_sql.py
```

**Copy this code:**

```python
#!/usr/bin/env python3
"""
SQL to MapReduce Translation

Translates this SQL query:
SELECT genre, AVG(rating) as avg_rating, COUNT(*) as movie_count
FROM movies
WHERE year >= 2000
GROUP BY genre
HAVING COUNT(*) >= 10
ORDER BY avg_rating DESC;
"""
from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class MRSQLTranslation(MRJob):
    
    def steps(self):
        """
        Define multi-stage pipeline
        Stage 1: Filter and aggregate
        Stage 2: Sort results
        """
        return [
            MRStep(mapper=self.mapper_filter,
                   reducer=self.reducer_aggregate),
            MRStep(reducer=self.reducer_sort)
        ]
    
    # ============================================================
    # STAGE 1: FILTER AND AGGREGATE
    # ============================================================
    
    def mapper_filter(self, _, line):
        """
        MAPPER 1: Apply WHERE clause and prepare for GROUP BY
        
        SQL equivalent: WHERE year >= 2000
        
        Line-by-line explanation:
        """
        # Step 1: Skip the CSV header line
        if line.startswith('movie_id'):
            return  # Exit this mapper call
        
        try:
            # Step 2: Parse CSV line properly
            # csv.reader handles quoted fields correctly
            # Example: "The Dark Knight",2008,Action,9.0
            reader = csv.reader([line])
            row = next(reader)
            
            # Step 3: Check if we have all required columns
            if len(row) < 5:
                return  # Skip malformed lines
            
            # Step 4: Extract columns from CSV
            movie_id = row[0]      # Not used, but shows structure
            title = row[1]         # Not used
            year = row[2]          # Used for filtering
            genre = row[3]         # Used for grouping
            rating = row[4]        # Used for averaging
            
            # Step 5: Convert strings to appropriate types
            year = int(year)       # "2008" → 2008
            rating = float(rating) # "9.0" → 9.0
            
            # Step 6: Apply WHERE clause (year >= 2000)
            if year >= 2000:
                # Step 7: Emit (genre, rating)
                # This prepares for GROUP BY genre
                yield (genre, rating)
                
        except (ValueError, IndexError):
            # Step 8: Handle errors (invalid year, rating, or missing columns)
            # Just skip problematic lines
            pass
    
    def reducer_aggregate(self, genre, ratings):
        """
        REDUCER 1: Perform GROUP BY, AVG, COUNT, HAVING
        
        SQL equivalent:
        GROUP BY genre
        AVG(rating)
        COUNT(*)
        HAVING COUNT(*) >= 10
        
        Line-by-line explanation:
        """
        # Step 1: Convert ratings iterator to list
        # We need to iterate twice (for sum and count)
        # Input example: ("Action", [9.0, 8.5, 8.1, 7.4, ...])
        ratings_list = list(ratings)
        
        # Step 2: COUNT(*) - count how many movies in this genre
        count = len(ratings_list)
        
        # Step 3: Apply HAVING clause (COUNT(*) >= 10)
        if count >= 10:
            # Step 4: Calculate AVG(rating)
            # Sum all ratings and divide by count
            total_rating = sum(ratings_list)
            avg_rating = total_rating / count
            
            # Step 5: Round to 2 decimal places
            avg_rating = round(avg_rating, 2)
            
            # Step 6: Emit with None as key
            # This sends ALL results to the same reducer in stage 2
            # Allows us to sort all genres together
            yield (None, {
                'genre': genre,
                'avg_rating': avg_rating,
                'movie_count': count
            })
    
    # ============================================================
    # STAGE 2: SORT
    # ============================================================
    
    def reducer_sort(self, _, genre_stats):
        """
        REDUCER 2: Sort results by avg_rating
        
        SQL equivalent: ORDER BY avg_rating DESC
        
        Line-by-line explanation:
        """
        # Step 1: Collect all results into a list
        # Input: All genre statistics from stage 1
        results = list(genre_stats)
        
        # Step 2: Sort by avg_rating in descending order
        # lambda x: x['avg_rating'] extracts the avg_rating from each dict
        # reverse=True means highest rating first
        results.sort(key=lambda x: x['avg_rating'], reverse=True)
        
        # Step 3: Emit sorted results
        for result in results:
            yield (result['genre'], result)

if __name__ == '__main__':
    MRSQLTranslation.run()
```

**Save and exit:** Ctrl+O, Enter, Ctrl+X

---

## Step 3.3: Test Locally

```bash
# Test with movies.csv
python3 mr_sql.py movies.csv
```

**Expected output:**
```
"Sci-Fi"   {"genre": "Sci-Fi", "avg_rating": 8.17, "movie_count": 12}
"Drama"    {"genre": "Drama", "avg_rating": 8.14, "movie_count": 13}
"Action"   {"genre": "Action", "avg_rating": 8.11, "movie_count": 12}
```

**Save results:**
```bash
python3 mr_sql.py movies.csv > sql_local.txt
cat sql_local.txt
```

---

## Step 3.4: Upload to HDFS and Run on Hadoop

```bash
# Remove old files
hadoop fs -rm -f movies.csv
hadoop fs -rm -r sql_output

# Upload input
hadoop fs -put movies.csv

# Verify
hadoop fs -ls

# Run on Hadoop
python3 mr_sql.py \
    -r hadoop \
    hdfs:///user/$USER/movies.csv \
    -o hdfs:///user/$USER/sql_output
```

---

## Step 3.5: Get Results

```bash
# View output files
hadoop fs -ls sql_output

# Merge results
hadoop fs -getmerge sql_output sql_hadoop.txt

# View results
cat sql_hadoop.txt
```

---

# Part 4: Exercise 3 - Basket Co-occurrence

## Overview
**Input:** purchases.csv (user_id, date, item)  
**Task:** For each item, find item it most frequently appears with  
**Output:** (item, {most_common_pair, count})  

**Algorithm:** 4-stage pipeline
1. Group items by basket (user_id, date)
2. Generate all pairs within each basket
3. Count pair occurrences
4. Find maximum co-occurrence for each item

---

## Step 4.1: Upload Input File

### macOS:
```bash
gcloud compute scp ~/Downloads/purchases.csv nyu-dataproc-m:~/lab3/basket/ --zone=us-east1-b
```

### Windows:
```cmd
gcloud compute scp C:\Users\YourName\Downloads\purchases.csv nyu-dataproc-m:~/lab3/basket/ --zone=us-east1-b
```

---

## Step 4.2: Create Co-occurrence Program

```bash
cd ~/lab3/basket
nano mr_cooccurrence.py
```

**Copy this code:**

```python
#!/usr/bin/env python3
"""
Shopping Basket Co-occurrence Analysis

Problem: For each item, find which item it most frequently appears with

Input: user_id,date,item
       (user_id, date) = unique basket identifier
       
Algorithm: 4-stage MapReduce pipeline
"""
from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class MRItemCooccurrence(MRJob):
    
    def steps(self):
        """
        Define 3-stage pipeline
        """
        return [
            MRStep(mapper=self.mapper_basket,
                   reducer=self.reducer_pairs),
            MRStep(mapper=self.mapper_count,
                   reducer=self.reducer_count),
            MRStep(mapper=self.mapper_group,
                   reducer=self.reducer_top)
        ]
    
    # ============================================================
    # STAGE 1: GROUP BY BASKET AND GENERATE PAIRS
    # ============================================================
    
    def mapper_basket(self, _, line):
        """
        MAPPER 1: Map items to their basket
        
        A basket is uniquely identified by (user_id, date)
        
        Line-by-line explanation:
        """
        # Step 1: Skip CSV header
        if line.startswith('user_id'):
            return
        
        try:
            # Step 2: Parse CSV line
            # Example: "user001,2024-01-01,milk"
            reader = csv.reader([line])
            row = next(reader)
            
            # Step 3: Verify we have all columns
            if len(row) < 3:
                return
            
            # Step 4: Extract fields
            user_id = row[0]  # "user001"
            date = row[1]     # "2024-01-01"
            item = row[2]     # "milk"
            
            # Step 5: Create basket identifier
            # (user_id, date) uniquely identifies a shopping session
            basket_id = (user_id, date)
            
            # Step 6: Emit (basket_id, item)
            # This groups all items from same shopping session
            yield (basket_id, item)
            
        except Exception:
            # Step 7: Skip malformed lines
            pass
    
    def reducer_pairs(self, basket_id, items):
        """
        REDUCER 1: Generate all pairs within each basket
        
        Example:
        Input: (("user001", "2024-01-01"), ["milk", "bread", "eggs"])
        Output: (("bread", "eggs"), 1)
                (("bread", "milk"), 1)
                (("eggs", "milk"), 1)
        
        Line-by-line explanation:
        """
        # Step 1: Convert items iterator to list
        # We need to access items multiple times
        items_list = list(items)
        
        # Step 2: Generate all unique pairs
        # Use nested loops to get all combinations
        for i in range(len(items_list)):
            for j in range(i + 1, len(items_list)):
                # Step 3: Get the two items
                item1 = items_list[i]  # "milk"
                item2 = items_list[j]  # "bread"
                
                # Step 4: Create ordered pair (alphabetically)
                # This ensures ("milk", "bread") and ("bread", "milk")
                # are treated as the same pair
                pair = tuple(sorted([item1, item2]))
                
                # Step 5: Emit (pair, 1)
                # Means: these two items appeared together once
                yield (pair, 1)
    
    # ============================================================
    # STAGE 2: COUNT PAIR OCCURRENCES
    # ============================================================
    
    def mapper_count(self, pair, count):
        """
        MAPPER 2: Pass through pairs
        (Just forwards data to reducer)
        """
        yield (pair, count)
    
    def reducer_count(self, pair, counts):
        """
        REDUCER 2: Sum occurrences and emit from both perspectives
        
        Example:
        Input: (("bread", "milk"), [1, 1, 1, ...])
        Output: ("bread", ("milk", 13))
                ("milk", ("bread", 13))
        
        Line-by-line explanation:
        """
        # Step 1: Sum all counts for this pair
        # If ("bread", "milk") appeared in 13 baskets,
        # counts = [1, 1, 1, ...] (13 ones)
        total = sum(counts)
        
        # Step 2: Extract the two items
        item1, item2 = pair
        
        # Step 3: Emit from item1's perspective
        # ("bread", ("milk", 13)) means:
        # "bread appeared with milk 13 times"
        yield (item1, (item2, total))
        
        # Step 4: Emit from item2's perspective
        # ("milk", ("bread", 13)) means:
        # "milk appeared with bread 13 times"
        yield (item2, (item1, total))
    
    # ============================================================
    # STAGE 3: FIND MOST COMMON CO-OCCURRENCE
    # ============================================================
    
    def mapper_group(self, item, cooccur_data):
        """
        MAPPER 3: Group by primary item
        (Just forwards data to reducer)
        """
        yield (item, cooccur_data)
    
    def reducer_top(self, item, cooccurrences):
        """
        REDUCER 3: Find most frequent co-occurrence for each item
        
        Example:
        Input: ("milk", [("bread", 13), ("eggs", 8), ("butter", 5), ...])
        Output: ("milk", {"most_common_pair": "bread", "count": 13})
        
        Line-by-line explanation:
        """
        # Step 1: Find the co-occurrence with maximum count
        # max() with key=lambda finds the tuple with highest count
        # Example: max([("bread", 13), ("eggs", 8)], key=lambda x: x[1])
        # Returns: ("bread", 13)
        max_cooccur = max(cooccurrences, key=lambda x: x[1])
        
        # Step 2: Extract item and count from the maximum
        cooccur_item = max_cooccur[0]  # "bread"
        count = max_cooccur[1]          # 13
        
        # Step 3: Emit result
        yield (item, {
            'most_common_pair': cooccur_item,
            'cooccurrence_count': count
        })

if __name__ == '__main__':
    MRItemCooccurrence.run()
```

**Save and exit:** Ctrl+O, Enter, Ctrl+X

---

## Step 4.3: Test Locally

```bash
python3 mr_cooccurrence.py purchases.csv
```

**Expected output:**
```
"milk"    {"most_common_pair": "bread", "cooccurrence_count": 13}
"bread"   {"most_common_pair": "milk", "cooccurrence_count": 13}
"eggs"    {"most_common_pair": "bacon", "cooccurrence_count": 8}
"bacon"   {"most_common_pair": "eggs", "cooccurrence_count": 8}
```

**Save results:**
```bash
python3 mr_cooccurrence.py purchases.csv > basket_local.txt
head -20 basket_local.txt
```

---

## Step 4.4: Run on Hadoop

```bash
# Cleanup
hadoop fs -rm -f purchases.csv
hadoop fs -rm -r basket_output

# Upload
hadoop fs -put purchases.csv

# Run on Hadoop
python3 mr_cooccurrence.py \
    -r hadoop \
    hdfs:///user/$USER/purchases.csv \
    -o hdfs:///user/$USER/basket_output
```

---

## Step 4.5: Get Results

```bash
# Merge results
hadoop fs -getmerge basket_output basket_hadoop.txt

# View top results
head -20 basket_hadoop.txt
```

---

# Part 5: Running Locally with mrjob

## Overview
You can develop and test MapReduce jobs on your **local computer** (Mac or Windows) without connecting to HPC. This is great for:
- Faster development iteration
- Debugging without cluster overhead
- Testing with small data samples

---

## Step 5.1: Install Python (If Not Installed)

### macOS:
```bash
# Check if Python 3 is installed
python3 --version

# If not installed, install using Homebrew
brew install python3
```

### Windows:
```cmd
REM Check if Python 3 is installed
python --version

REM If not installed:
REM 1. Download from https://www.python.org/downloads/
REM 2. Run installer
REM 3. IMPORTANT: Check "Add Python to PATH"
REM 4. Restart Command Prompt
```

---

## Step 5.2: Install mrjob Locally

### macOS:
```bash
# Install mrjob
pip3 install mrjob

# Verify installation
python3 -c "import mrjob; print('mrjob installed')"
```

### Windows:
```cmd
REM Install mrjob
pip install mrjob

REM Verify installation
python -c "import mrjob; print('mrjob installed')"
```

---

## Step 5.3: Create Local Working Directory

### macOS:
```bash
# Create directory structure
mkdir -p ~/lab3/word_count
mkdir -p ~/lab3/sql_filter
mkdir -p ~/lab3/basket

# Navigate to lab3
cd ~/lab3
```

### Windows:
```cmd
REM Create directory structure
mkdir %USERPROFILE%\lab3\word_count
mkdir %USERPROFILE%\lab3\sql_filter
mkdir %USERPROFILE%\lab3\basket

REM Navigate to lab3
cd %USERPROFILE%\lab3
```

---

## Step 5.4: Download Input Files

**Download these files to your computer:**
1. book.txt
2. movies.csv
3. purchases.csv

**Place them in the appropriate directories:**

### macOS:
```bash
# Copy files (update paths as needed)
cp ~/Downloads/book.txt ~/lab3/word_count/
cp ~/Downloads/movies.csv ~/lab3/sql_filter/
cp ~/Downloads/purchases.csv ~/lab3/basket/
```

### Windows:
```cmd
REM Copy files (update paths as needed)
copy %USERPROFILE%\Downloads\book.txt %USERPROFILE%\lab3\word_count\
copy %USERPROFILE%\Downloads\movies.csv %USERPROFILE%\lab3\sql_filter\
copy %USERPROFILE%\Downloads\purchases.csv %USERPROFILE%\lab3\basket\
```

---

## Step 5.5: Create Python Programs Locally

### Option A: Using a Text Editor

**macOS:**
```bash
# Open with your preferred editor
nano ~/lab3/word_count/mr_wordcount.py
# OR
open -a TextEdit ~/lab3/word_count/mr_wordcount.py
# OR use VS Code, Sublime, etc.
```

**Windows:**
```cmd
REM Open with Notepad
notepad %USERPROFILE%\lab3\word_count\mr_wordcount.py

REM OR use VS Code, Notepad++, etc.
code %USERPROFILE%\lab3\word_count\mr_wordcount.py
```

### Option B: Copy from This Guide

Copy the code from Parts 2, 3, and 4 of this guide into three files:
1. `mr_wordcount.py` (from Step 2.2)
2. `mr_sql.py` (from Step 3.2)
3. `mr_cooccurrence.py` (from Step 4.2)

---

## Step 5.6: Run Locally - Word Count

### macOS:
```bash
# Navigate to word_count directory
cd ~/lab3/word_count

# Run MapReduce locally
python3 mr_wordcount.py book.txt

# Save output
python3 mr_wordcount.py book.txt > output.txt

# View top words
cat output.txt | sort -t$'\t' -k2 -nr | head -20
```

### Windows:
```cmd
REM Navigate to word_count directory
cd %USERPROFILE%\lab3\word_count

REM Run MapReduce locally
python mr_wordcount.py book.txt

REM Save output
python mr_wordcount.py book.txt > output.txt

REM View results
type output.txt
```

---

## Step 5.7: Run Locally - SQL Translation

### macOS:
```bash
cd ~/lab3/sql_filter
python3 mr_sql.py movies.csv
python3 mr_sql.py movies.csv > output.txt
cat output.txt
```

### Windows:
```cmd
cd %USERPROFILE%\lab3\sql_filter
python mr_sql.py movies.csv
python mr_sql.py movies.csv > output.txt
type output.txt
```

---

## Step 5.8: Run Locally - Basket Co-occurrence

### macOS:
```bash
cd ~/lab3/basket
python3 mr_cooccurrence.py purchases.csv
python3 mr_cooccurrence.py purchases.csv > output.txt
head -20 output.txt
```

### Windows:
```cmd
cd %USERPROFILE%\lab3\basket
python mr_cooccurrence.py purchases.csv
python mr_cooccurrence.py purchases.csv > output.txt
type output.txt
```

---

## Step 5.9: Debugging Locally

### View Detailed Output

### macOS:
```bash
# Run with verbose output
python3 mr_wordcount.py -v book.txt

# Test just the mapper
cat book.txt | python3 mr_wordcount.py --mapper

# Test just the reducer
echo -e "the\t1\nthe\t1\nthe\t1" | python3 mr_wordcount.py --reducer
```

### Windows:
```cmd
REM Run with verbose output
python mr_wordcount.py -v book.txt

REM Test mapper/reducer separately on Windows requires more setup
REM Easier to test by running full pipeline with small input
```

---

## Step 5.10: Test with Small Sample Data

**Create a tiny test file for faster debugging:**

### macOS:
```bash
# Create small test file
echo "the quick brown fox jumps over the lazy dog" > test_small.txt
echo "the lazy dog sleeps under the tree" >> test_small.txt

# Test
python3 mr_wordcount.py test_small.txt
```

### Windows:
```cmd
REM Create small test file
echo the quick brown fox jumps over the lazy dog > test_small.txt
echo the lazy dog sleeps under the tree >> test_small.txt

REM Test
python mr_wordcount.py test_small.txt
```

---

## Step 5.11: When to Use Local vs Hadoop

### Use Local (Your Computer) When:
✅ Developing and debugging code  
✅ Testing with small data (<100 MB)  
✅ Learning MapReduce concepts  
✅ Quick iterations  
✅ No cluster access needed  

### Use Hadoop (HPC Cluster) When:
✅ Processing large data (>1 GB)  
✅ Final submission/grading  
✅ Testing scalability  
✅ Parallel processing needed  
✅ Assignment requires it  

---

## Step 5.12: Development Workflow

**Best practice: Test locally first, then deploy to Hadoop**

```
1. Write code locally (Mac/Windows)
2. Test with small data locally
3. Debug and fix issues
4. Test with full data locally (if size permits)
5. Upload code and data to HPC
6. Run on Hadoop
7. Download and verify results
```

**This saves time because:**
- Local testing is instant (no cluster queue)
- Easier to debug (can use print statements)
- No network latency
- Free to experiment

---

# Summary of All Commands

## One-Time Setup
```bash
# Install gcloud
brew install google-cloud-sdk  # macOS
# OR download installer for Windows

# Authenticate
gcloud auth login
gcloud compute config-ssh

# Connect to cluster
gcloud compute ssh nyu-dataproc-m --zone=us-east1-b

# On cluster: setup
ssh-keygen -t ed25519 -C "netid@nyu.edu"
cat ~/.ssh/id_ed25519.pub  # Add to GitHub
pip install mrjob --break-system-packages
mkdir -p ~/lab3/{word_count,sql_filter,basket}
```

## Upload Files (Mac/Windows to Cluster)
```bash
# Mac/Windows → Cluster
gcloud compute scp file.txt nyu-dataproc-m:~/lab3/word_count/ --zone=us-east1-b
```

## Test Locally (On Cluster or Your Computer)
```bash
python3 mr_wordcount.py book.txt
python3 mr_sql.py movies.csv
python3 mr_cooccurrence.py purchases.csv
```

## Run on Hadoop (On Cluster)
```bash
# Cleanup
hadoop fs -rm -r output
hadoop fs -rm -f input.txt

# Upload
hadoop fs -put input.txt

# Run
python3 mr_script.py -r hadoop hdfs:///user/$USER/input.txt -o hdfs:///user/$USER/output

# Get results
hadoop fs -getmerge output result.txt
```

## Download Results (Cluster → Mac/Windows)
```bash
gcloud compute scp nyu-dataproc-m:~/lab3/word_count/result.txt ~/Downloads/ --zone=us-east1-b
```

---

# Troubleshooting

## Issue: "File exists" error
```bash
# Solution
hadoop fs -rm -f input.txt
hadoop fs -rm -r output
```

## Issue: "Permission denied" on GitHub
```bash
# Solution
ssh-keygen -t ed25519 -C "netid@nyu.edu"
cat ~/.ssh/id_ed25519.pub  # Add to GitHub
ssh -T git@github.com  # Test
```

## Issue: mrjob not found
```bash
# On cluster
pip install mrjob --break-system-packages

# On Mac
pip3 install mrjob

# On Windows
pip install mrjob
```

## Issue: gcloud not found
```bash
# Restart terminal after installation
# On Mac: brew install google-cloud-sdk
# On Windows: reinstall and check "Add to PATH"
```

---

**END OF GUIDE**

This guide covers everything you need to complete Lab 3!
- ✅ HPC setup for Mac and Windows
- ✅ All three exercises with complete code
- ✅ Line-by-line code explanations
- ✅ Local and Hadoop execution
- ✅ All commands and steps
