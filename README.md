# Python YouTube Tools\n\nPython pipeline for querying the YouTube Data API to survey, filter, and analyze instrumental music content across global markets. Demonstrates API integration, data filtering, and visualization techniques applicable to any YouTube content analysis workflow.\n\n---\n\n## Overview\n\nBecause YouTube lacks a native non-vocal search filter, this pipeline combines targeted API queries with keyword-based filtering to isolate instrumental content (Lo-Fi, deep house, ambient, deep focus, study beats) across multiple regions. The approach and architecture are reusable for any genre or content category survey.\n\n---\n\n## Survey Methodologies\n\nThree primary approaches are supported for conducting a comprehensive content survey:

### Method 1: Curated API Data Scraping (Implemented Below)
Querying the official YouTube Data API v3 using Python is the most robust and precise method. It allows you to target specific video category IDs (e.g., Music), programmatically inject negative keywords (e.g., `-lyrics`), isolate geographic regions, and extract absolute view counts.

### Method 2: Manual Charts & Playlist Analysis
For qualitative validation or quick reference points, you can leverage YouTube's curated datasets:
* **YouTube Music Insights:** Access the public YouTube Charts portal to check trending instrumental tracks globally or by specific urban centers.
* **Manual Playlist Audits:** Document view counts and upload frequencies from massive user-curated directories like *Instrumental Popular Songs* or *Instrumental Pop Music* mixes.

### Method 3: Third-Party Music Analytics Platforms
For high-level industry tracking without dealing with raw code, enterprise platforms offer pre-aggregated dashboards:
* **Soundcharts & Apify Scrapers:** Tools like Soundcharts track daily view velocity, historic chart trajectories, and localized audience demographics for specific instrumental artists without requiring direct channel ownership.

---

## 🖥️ Execution Environments

You can run this project in three primary environments depending on your current workflow needs.

### Option A: Google Colab (Zero-Setup Cloud Notebook)
Google Colab requires no local installation and handles environment configuration on Google's cloud servers.
1. Navigate to Google Colab (https://google.com).
2. Select **File > New Notebook**.
3. In the first code cell, paste the following install string and run it:
   ```bash
   !pip install google-api-python-client pandas matplotlib seaborn
   ```
4. Paste the complete Python script (from the separate code block) into a second cell, insert your `API_KEY`, and press run.

### Option B: Local Jupyter Notebook
Ideal for an interactive workspace where you want to keep data caches and visual plots saved locally on your machine.
1. Open your terminal or command prompt and install the dependencies:
   ```bash
   pip install google-api-python-client pandas matplotlib seaborn
   ```
2. Launch the notebook web server:
   ```bash
   jupyter notebook
   ```
3. Create a blank `.ipynb` workspace, paste the script blocks, and execute.

### Option C: Standalone Local Script (VS Code / Terminal)
Best for production deployments, automated cron tasks, or running inside a standard terminal window. Save the code into a file named `survey_pipeline.py` and run it via:
```bash
python survey_pipeline.py
```

---

## 🔑 YouTube API Key Acquisition Setup

To connect to Google's endpoints, you need a free access credential token:
1. Navigate to the Google Cloud Console (https://google.com).
2. Create a new project (e.g., `Youtube-Music-Survey`).
3. Navigate to **API & Services > Library**, search for **YouTube Data API v3**, and click **Enable**.
4. Go to **Credentials**, click **Create Credentials**, choose **API Key**, and copy the string.
5. Paste this key into the `API_KEY` configuration string at the top of the script.

*Note: Free Google Cloud accounts receive 10,000 quota units per day. A complete multi-region run of this script consumes roughly ~2,500 units, giving you plenty of testing overhead.*

---

## 🧹 Data-Cleaning Logic: Filtering out Vocal Slip-Throughs

Even with strict API querying, vocal tracks (like karaoke versions, lyrical instrumentals, or cover song covers) can sometimes bypass search boundaries. The pipeline handles this through a multi-tiered data-cleaning workflow:

1. **API-Level Negative Keywords:** The search query injects a hardcoded negative filter (`-lyrics -vocal -singing -karaoke -cover`) to eliminate bad matches at the source.
2. **Title-Based String Scrubbing:** During processing, the script scans the video title for user-defined forbidden substrings (e.g., "feat.", "vocal mix", "official video"). If detected, the video is instantly skipped.
3. **Channel Blacklisting:** If specific channels consistently output vocal music despite matching instrumental queries, their unique channel names can be added to an array to exclude them from the final dataframe.

---

## 🔄 Automated Tracking: GitHub Actions Introduction

If you do not want to run this script manually every week, you can automate it using **GitHub Actions**.

### What is a GitHub Actions Workflow?
GitHub Actions is a cloud automation tool built directly into GitHub. It can launch a temporary virtual machine (runner), install Python, run your scraping script on a set schedule (e.g., every Monday morning), and automatically commit the fresh data file back into your repository.

### Setup Instructions
1. In the root directory of your repository, create a folder structure named `.github/workflows/`.
2. Inside that directory, create a text file named `run_scraper.yml`.
3. Paste the following configuration block into that file and push it to GitHub:

```yaml
name: Scheduled YouTube Survey Scraper

on:
  schedule:
    # Runs automatically at 00:00 UTC every Monday morning
    - cron: '0 0 * * 1'
  workflow_dispatch: # Allows you to trigger the job manually from the GitHub website

jobs:
  execute-scrape:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository Code
      uses: actions/checkout@v4

    - name: Set up Python Environment
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install Project Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install google-api-python-client pandas matplotlib seaborn

    - name: Run Scraping Pipeline Script
      run: python survey_pipeline.py
      env:
        # Safely feeds your API Key to the runner environment without exposing it in the code
        YOUTUBE_API_KEY: \${{ secrets.YOUTUBE_API_KEY }}

    - name: Commit and Save Fresh Data Assets
      run: |
        git config --global user.name "Automated Architecture Bot"
        git config --global user.email "bot@github.com"
        git add youtube_instrumental_metrics.csv plots/
        git commit -m "Automated Weekly Scraper Update [Skip CI]" || exit 0
        git push
```

### Important Security Step for Automation
Never paste your raw API key directly into a public file like `run_scraper.yml`. Instead, do this:
1. Go to your repository on GitHub.
2. Click **Settings > Secrets and variables > Actions**.
3. Click **New repository secret**.
4. Name the secret exactly `YOUTUBE_API_KEY` and paste your Google API key as the value. 
5. Modify the script to use `os.environ.get("YOUTUBE_API_KEY")` instead of a hardcoded string.

---

## TO DO

1. Dynamically pull the key from environment variables so it is immediately prepared for GitHub Actions
2. Add a configuration option to filter by channel name, allowing whitelist or blacklist of specific music labels
3. Adjusting the graph dimensions or fonts
4. Build out automated script template to add more country codes
5. Additional media and API scraping metrics (e.g. channel subscriber growth, likes) to incorporate into data views.



## Related Projects

- [python-sysadmin-tools](https://github.com/sjamal/python-sysadmin-tools) — Infrastructure auditing and VM sizing utilities
- [python-data-processing](https://github.com/sjamal/python-data-processing) — ETL and data transformation pipelines
- [python-machine-learning](https://github.com/sjamal/python-machine-learning) — Model training and evaluation scripts
- [python-utilities](https://github.com/sjamal/python-utilities) — Shared helper functions and utilities
- [python-visualization](https://github.com/sjamal/python-visualization) — Data visualization scripts
- [python-youtube-tools](https://github.com/sjamal/python-youtube-tools) — YouTube API data collection and analysis
- [r-data-analysis](https://github.com/sjamal/r-data-analysis) — R statistical analysis and visualization