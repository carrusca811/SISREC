import os
import pandas as pd
from database import movies_collection
import asyncio
import aiohttp

FALLBACK_IMAGE_URL = "N/A"
DATA_PATH = "./data/dataset_limpo.xlsx"

OMDB_API_KEY = "7048d9e5"
GOOGLE_API_KEY = "AIzaSyC8SP2aYHGhq3br3fozV4TUBcN8iEmCxmo"
GOOGLE_CX = "c69027dd0adaf4273"


async def fetch_poster_omdb(session, title, year):
    try:
        url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("Poster") if data.get("Response") == "True" else None
            return None
    except Exception as e:
        print(f"❌ Erro OMDB: {title} ({year}) → {e}")
        return None


async def fetch_google_image(session, title, year):
    try:
        query = f"{title} {year} movie poster"
        url = (
            f"https://www.googleapis.com/customsearch/v1?q={query}"
            f"&cx={GOOGLE_CX}&searchType=image&num=1&key={GOOGLE_API_KEY}"
        )
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if "items" in data:
                    return data["items"][0]["link"]
        return None
    except Exception as e:
        print(f"❌ Erro Google Search: {title} ({year}) → {e}")
        return None


async def import_data():
    try:
        df = pd.read_excel(DATA_PATH)
        df["Genre"] = df["Genre"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])
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

                poster = await fetch_poster_omdb(session, title, year)

                if not poster or poster == "N/A":
                    poster = await fetch_google_image(session, title, year)

                record["image_url"] = poster if poster else FALLBACK_IMAGE_URL
                record["users_review"] = 0.0  # inicializa o campo


        await movies_collection.insert_many(records)
        print(f"✅ {len(records)} filmes inseridos com sucesso com posters!")
    
    except Exception as e:
        print(f"❌ Erro ao importar dados: {e}")


if __name__ == "__main__":
    asyncio.run(import_data())
