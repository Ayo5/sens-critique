from fastapi import FastAPI
from pymongo import MongoClient
import re

app = FastAPI()


def connect_to_mongo():
    client = MongoClient("mongodb://localhost:27017/sens-critique")
    db = client["sens-critique"]
    return db


def get_key_words(review_content: str):
    mots = review_content.split()
    mots_unique = set(mots)
    mot_cle = []
    for mot in mots_unique:
        if len(mot) > 4:
            mot_cle.append(mot)
    return [mot.lower() for mot in mot_cle]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/collections") 
async def get_collections():
    try : 
        db = connect_to_mongo()
        collections = db.list_collection_names()
        return {"collections": collections}
    except Exception as e:
        return {"erreur": str(e)}


@app.get("/{collection_name}")
async def get_reviews(collection_name : str, limit = 100 )  : 
    try : 
        db = connect_to_mongo()
        collections = db.list_collection_names()
        if collection_name not in collections:
            return {"erreur": "Collection not found"}
        curseur = db[collection_name].find().limit(limit)
        docs = []
        for doc in curseur : 
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            docs.append(doc)
        return {"count": len(docs), "documents": docs}
    except Exception as e: 
        return {"erreur": str(e)} 


@app.get("/{collection_name}/{id_review}")
async def get_same_rating_reviews(collection_name: str, id_review: int, limit: int = 100):
    try:
        db = connect_to_mongo()
        collections = db.list_collection_names()
        if collection_name not in collections:
            return {"erreur": "Collection not found"}

        col = db[collection_name]
        review = col.find_one({"id": id_review})
        if not review:
            try:
                review = col.find_one({"id": id_review})
            except Exception:
                review = None
        if not review:
            return {"erreur": "Review not found"}

        review_rating = review.get("rating")
        stored_id = review.get("id")
        curseur = col.find({"rating": review_rating, "id": {"$ne": stored_id}}).limit(limit)

        result = []
        for doc in curseur:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            result.append({"id": doc.get("id"), "rating": doc.get("rating")})
        return {"rating": review_rating, "count": len(result), "documents": result}

    except Exception as e:
        return {"erreur": str(e)}
    
@app.get("/{collection_name}/{id_review}/review")
async def get_review_content(collection_name: str, id_review: int):
    try:
        db = connect_to_mongo()
        collections = db.list_collection_names()
        if collection_name not in collections:
            return {"erreur": "Collection not found"}

        col = db[collection_name]
        review = col.find_one({"id": id_review})
        if not review:
            try:
                review = col.find_one({"id": int(id_review)})
            except Exception:
                review = None
        if not review:
            return {"erreur": "Review not found"}
        return {"id": review.get("id"), "content": review.get("review_content")}

    except Exception as e:
        return {"erreur": str(e)}



@app.get("/{collection_name}/{id_review}/recommendations")
async def get_recommendations(collection_name: str, id_review: int, limit: int = 100, min_commum = 20):
    try:
        db = connect_to_mongo()
        collections = db.list_collection_names()
        if collection_name not in collections:
            return {"erreur": "Collection not found"}

        col = db[collection_name]
        review = col.find_one({"id": id_review})
        if not review:
            try:
                review = col.find_one({"id": int(id_review)})
            except Exception:
                review = None
        if not review:
            return {"erreur": "Review not found"}

        review_content = review.get("review_content", "")
        key_words = get_key_words(review_content)
        safe_keywords = [kw.strip() for kw in key_words if kw and kw.strip()]
        if len(safe_keywords) < min_commum:
            return {"erreur" : "Not enough common keywords","count": 0, "documents": []}

        max_kw = min(len(safe_keywords), 100)
        escaped = [re.escape(kw) for kw in safe_keywords[:max_kw]]
        regex_clauses = [{"review_content": {"$regex": kw, "$options": "i"}} for kw in escaped]

        rating = review.get("rating")
        rating_values = [rating]
        try:
            rnum = float(rating)
            if rnum.is_integer():
                rints = [int(rnum), int(rnum - 1), int(rnum + 1)]
                rating_values = list(dict.fromkeys([v for v in rints if v >= 0]))
            else:
                rating_values = list(dict.fromkeys([rnum, rnum - 1.0, rnum + 1.0]))
        except Exception:
            rating_values = [rating]

        query = {
            "$and": [
                {"id": {"$ne": review.get("id")}},
                {"$or": regex_clauses},
                {"rating": {"$in": rating_values}}
            ]
        }
        curseur = col.find(query).limit(limit)
        result = []
        for doc in curseur:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            result.append({"id": doc.get("id"), "rating": doc.get("rating"), "review_content": doc.get("review_content")})

        return {
            "keywords_used": safe_keywords[:max_kw],
            "rating_searched": rating,
            "rating_candidates": rating_values,
            "count": len(result),
            "documents": result
        }
    except Exception as e:
        return {"erreur": str(e)}
