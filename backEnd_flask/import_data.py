import os
import pandas as pd
from database import movies_collection
import asyncio

DATA_PATH = "./data/dataset_limpo.xlsx"

async def import_data():
    try:
        # Ler o Excel
        df = pd.read_excel(DATA_PATH)
        
        # Limpeza e formatação dos dados
        df["Genre"] = df["Genre"].apply(lambda x: x.split(", "))
        df["cast"] = df[["Star1", "Star2", "Star3", "Star4"]].values.tolist()

        # Selecionar apenas as colunas necessárias
        df = df[["Series_Title", "Released_Year", "Certificate", "Runtime", "Genre", "IMDB_Rating", 
                 "Meta_score", "Director", "cast", "No_of_Votes", "Gross"]]

        # Renomear colunas
        df.columns = ["title", "year", "certificate", "runtime", "genres", "imdb_rating", 
                      "meta_score", "director", "cast", "votes", "gross"]

        # Converter para dicionários
        records = df.to_dict(orient="records")

        # Inserir os dados no MongoDB
        await movies_collection.insert_many(records)
        print(f"{len(records)} filmes inseridos com sucesso!")
    
    except Exception as e:
        print(f"Erro ao importar dados: {e}")

if __name__ == "__main__":
    asyncio.run(import_data())
