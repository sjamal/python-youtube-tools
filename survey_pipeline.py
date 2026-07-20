import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==============================================================================
# 1. CORE PIPELINE CONFIGURATION
# ==============================================================================
# Insert your official Google Developer YouTube API key string here
API_KEY = "YOUR_ACTUAL_API_KEY_HERE"  

# Highly targeted search phrases matching target ambient/chill niches
GENRE_QUERIES = [
    "lofi hip hop study focus",
    "deep house mix chill chillout",
    "ambient background sleep beats",
    "deep focus instrumental study beats"
]

# Negative terms appended to the API query string to drop lyrical music at the source
NEGATIVE_KEYWORDS = " -lyrics -vocal -singing -karaoke -cover"

# Case-insensitive sub-strings used to clean out vocal items that bypassed the search filter
FORBIDDEN_TITLE_KEYWORDS = ["feat.", "ft.", "vocal version", "lyrics", "sing-along", "song"]

# Geographic regions mapped to ISO 3166-1 alpha-2 country codes (None tracks broad global data)
REGIONS = {
    "Global": None,
    "Canada": "CA",
    "United States": "US",
    "Germany": "DE",
    "India": "IN",
    "China": "CN"
}

# ==============================================================================
# 2. DATA ACQUISITION & SCRUBBING ENGINE
# ==============================================================================
def get_youtube_client():
    """Initializes and returns an authorized Google API client connection."""
    return build("youtube", "v3", developerKey=API_KEY)

def fetch_instrumental_data(youtube, query, region_code=None, stream_type="video", max_results=15):
    """
    Queries YouTube API for music videos matching conditions and filters out vocal elements.
    stream_type choices:
       - "video": Traditional uploaded video on-demand (VOD) formats only
       - "live": 24/7 active streaming broadcasts only (e.g., Lofi Girl Live)
       - "any": Merges both active live streams and classic VOD items
    """
    full_query = query + NEGATIVE_KEYWORDS
    video_list = []
    
    try:
        # Step A: Perform search query limited to the official YouTube Music Category (ID 10)
        search_kwargs = {
            "q": full_query,
            "part": "id,snippet",
            "type": "video",
            "videoCategoryId": "10",  
            "order": "viewCount",
            "maxResults": max_results
        }
        
        # Apply specialized broadcast state filters if toggled by user
        if stream_type in ["video", "live"]:
            search_kwargs["videoEventType"] = stream_type
        
        if region_code:
            search_kwargs["regionCode"] = region_code
            
        search_response = youtube.search().list(**search_kwargs).execute()
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        
        if not video_ids:
            return []

        # Step B: Execute a secondary batched query to get concrete analytics statistics
        stats_response = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids)
        ).execute()

        # Step C: Parse metadata, evaluate cleanliness rules, and extract metrics
        for item in stats_response.get("items", []):
            title = item["snippet"]["title"]
            
            # --- TIER 2: POST-API DATA CLEANING RULES ---
            # Automatically skip track if any forbidden vocal phrases match the title string
            if any(forbidden in title.lower() for forbidden in FORBIDDEN_TITLE_KEYWORDS):
                continue  # Drops the record from compilation
                
            is_live = item["snippet"].get("liveBroadcastContent") == "live"
            
            # Active streams display 'concurrentViewers'; VOD uses absolute lifetime 'viewCount'
            metric_val = item["statistics"].get("concurrentViewers" if is_live else "viewCount", 0)

            video_list.append({
                "Title": title,
                "Channel": item["snippet"]["channelTitle"],
                "Metric Count": int(metric_val),
                "Format": "Live Stream" if is_live else "VOD (Video)",
                "Published At": item["snippet"]["publishedAt"],
                "Video URL": f"https://youtube.com{item['id']}"
            })
            
    except HttpError as e:
        print(f"[⚠️ API Error]: {e}")
    return video_list

# ==============================================================================
# 3. STATISTICAL DATA VISUALIZATION ENGINE
# ==============================================================================
def generate_plots(df, individual_charts=True):
    """
    Generates analytical visual representations of the collected datasets.
    Can export a single comparative graph or unique localized performance charts.
    """
    if df.empty:
        print("⚠️ Visualization skipped: Empty Dataframe.")
        return
        
    sns.set_theme(style="whitegrid")
    
    # --- CHART OPTION 1: AGGREGATED COMPARATIVE OVERVIEW ---
    plt.figure(figsize=(12, 6))
    country_totals = df.groupby("Region/Country")["Metric Count"].sum().reset_index()
    country_totals = country_totals.sort_values(by="Metric Count", ascending=False)
    
    sns.barplot(data=country_totals, x="Region/Country", y="Metric Count", palette="viridis")
    plt.title("Total Instrumental Music Consumption Volume Breakdown by Region", fontsize=14, pad=15)
    plt.xlabel("Region / Country Market", fontsize=12)
    plt.ylabel("Cumulative Engagement Volume (Log Scale)", fontsize=12)
    plt.yscale("log")  # Using log scale to handle the disparity between Global and local markets safely
    
    plt.tight_layout()
    plt.savefig("plots/aggregated_regional_breakdown.png", dpi=300)
    plt.close()
    print("📈 Aggregated visual generated: 'plots/aggregated_regional_breakdown.png'")
    
    # --- CHART OPTION 2: INDIVIDUAL ISOLATED COUNTRY BREAKDOWNS ---
    if individual_charts:
        for country in df["Region/Country"].unique():
            country_df = df[df["Region/Country"] == country].head(7)  # Isolate top 7 songs per country
            
            if country_df.empty:
                continue
                
            plt.figure(figsize=(10, 5))
            
            # Clean up titles slightly for plot labels so text does not clip
            country_df["Short Title"] = country_df["Title"].apply(lambda x: x[:35] + "..." if len(x) > 35 else x)
            
            sns.barplot(data=country_df, x="Metric Count", y="Short Title", palette="plasma")
            plt.title(f"Top Instrumental Tracks Performance Scale - Market: {country}", fontsize=13, pad=12)
            plt.xlabel("Engagement Metric Count", fontsize=11)
            plt.ylabel("Song Track Title", fontsize=11)
            
            plt.tight_layout()
            safe_name = country.lower().replace(" ", "_")
            plt.savefig(f"plots/market_breakdown_{safe_name}.png", dpi=300)
            plt.close()
            print(f"📊 Country breakdown chart generated: 'plots/market_breakdown_{safe_name}.png'")

# ==============================================================================
# 4. ENVIRONMENT RUN EXECUTION CONTROLLER
# ==============================================================================
def main():
    """Orchestrates sequence steps for scraping data, sorting data, and visual outputs."""
    youtube = get_youtube_client()
    all_data = []

    # USER CONFIGURATION MODE INTERCHANGE:
    # Set to "video" (Only standard uploads), "live" (Only 24/7 channels), or "any" (Combines both)
    RUN_MODE = "any" 
    
    # Create an output directory for visual image exports if not present
    os.makedirs("plots", exist_ok=True)
    
    print(f"🚀 Starting YouTube Scraping Engine [Mode: {RUN_MODE.upper()}]...")
    
    # Loop sequentially across geographic target parameters
    for region_name, region_code in REGIONS.items():
        print(f"📡 Processing market sector: {region_name}...")
        
        for genre in GENRE_QUERIES:
            records = fetch_instrumental_data(
                youtube, 
                query=genre, 
                region_code=region_code, 
                stream_type=RUN_MODE, 
                max_results=10
            )
            
            for item in records:
                # Extends keyword context tag
                item["Niche Category"] = genre.upper() 
                item["Region/Country"] = region_name
                all_data.append(item)

    df = pd.DataFrame(all_data)
    
    if not df.empty:
        # Remove duplicate data records flagged by intersecting keyword matrix scopes
        df = df.drop_duplicates(subset=["Video URL", "Region/Country"])
        
        # --- FLEXIBLE DATA SORTING ENGINE ---
        # Sorts explicitly by alphabetical Country labels, then orders descending by view/stream metric numbers
        df = df.sort_values(by=["Region/Country", "Metric Count"], ascending=[True, False])
        
        # Persist data down to structured file asset
        df.to_csv("youtube_instrumental_metrics.csv", index=False)
        print("\n✅ Dataset compilation successful! File saved as 'youtube_instrumental_metrics.csv'")
        
        # Fire visualization execution sequence
        generate_plots(df, individual_charts=True)
    else:
        print("❌ Scraper completed but returned zero records. Check API configurations or Quota limits.")

if __name__ == "__main__":
    main()

