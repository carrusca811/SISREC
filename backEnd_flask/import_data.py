import os
import pandas as pd
from database import movies_collection
import asyncio
import aiohttp
FALLBACK_IMAGE_URL = "N/A"
DATA_PATH = "./data/dataset_limpo.xlsx"
OMDB_API_KEY = "7048d9e5" 

async def fetch_poster(session, title, year):
    try:
        url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("Poster") if data.get("Response") == "True" else None
            return None
    except Exception as e:
        print(f"Erro ao obter poster para {title} ({year}): {e}")
        return None

async def import_data():
    try:
        df = pd.read_excel(DATA_PATH)
        df["Genre"] = df["Genre"].apply(lambda x: x.split(", "))
        df["cast"] = df[["Star1", "Star2", "Star3", "Star4"]].values.tolist()
        df = df[["Series_Title", "Released_Year", "Certificate", "Runtime", "Genre", "IMDB_Rating", 
                 "Meta_score", "Director", "cast", "No_of_Votes", "Gross"]]
        df.columns = ["title", "year", "certificate", "runtime", "genres", "imdb_rating", 
                      "meta_score", "director", "cast", "votes", "gross"]
        records = df.to_dict(orient="records")

        async with aiohttp.ClientSession() as session:
            for record in records:
                title = record["title"]
                year = record["year"]
                poster = await fetch_poster(session, title, year)
                record["image_url"] = poster if poster and poster != "N/A" else FALLBACK_IMAGE_URL


        await movies_collection.insert_many(records)
        print(f"{len(records)} filmes inseridos com sucesso com posters!")
    
    except Exception as e:
        print(f"Erro ao importar dados: {e}")

if __name__ == "__main__":
    asyncio.run(import_data())
