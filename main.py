import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Project, Testimonial, ContactMessage

app = FastAPI(title="Graphic Designer Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Graphic Designer Portfolio API"}

@app.get("/schema")
def get_schema():
    """Expose schemas so the visual DB tool can read them"""
    return {
        "collections": ["project", "testimonial", "contactmessage"],
    }

# Public endpoints

@app.get("/projects")
def list_projects(limit: Optional[int] = 20):
    try:
        items = get_documents("project", {}, limit)
        # Convert ObjectId to string if present
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/testimonials")
def list_testimonials(limit: Optional[int] = 20):
    try:
        items = get_documents("testimonial", {}, limit)
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ContactIn(ContactMessage):
    pass

@app.post("/contact")
def submit_contact(payload: ContactIn):
    try:
        inserted_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
