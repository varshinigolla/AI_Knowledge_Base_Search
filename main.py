from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import List, Optional
import json
from datetime import datetime

from config import settings
from models import SearchResponse, DocumentMetadata, SearchQuery, AnswerRating
from document_processor import DocumentProcessor
from rag_pipeline import RAGPipeline

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Knowledge Base Search & Enrichment",
    description="Upload documents, search with natural language, and get AI-powered answers with enrichment suggestions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
rag_pipeline = RAGPipeline()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store for answer ratings (in production, use a proper database)
answer_ratings = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Validate file size
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Save file temporarily
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        metadata = document_processor.process_document(
            file_path, 
            file.filename, 
            file.content_type
        )
        
        # Clean up temporary file
        os.remove(file_path)
        
        return metadata
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_documents(
    query: str = Form(...),
    include_confidence: bool = Form(True),
    include_enrichment: bool = Form(True)
):
    """Search documents and get AI-powered answer"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        response = rag_pipeline.search_and_answer(
            query=query,
            include_confidence=include_confidence,
            include_enrichment=include_enrichment
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-json", response_model=SearchResponse)
async def search_documents_json(search_query: SearchQuery):
    """Search documents using JSON input"""
    try:
        if not search_query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        response = rag_pipeline.search_and_answer(
            query=search_query.query,
            include_confidence=search_query.include_confidence,
            include_enrichment=search_query.include_enrichment
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentMetadata])
async def list_documents():
    """Get list of all uploaded documents"""
    try:
        documents = document_processor.get_document_list()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the knowledge base"""
    try:
        # URL decode the filename
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename)
        
        success = document_processor.delete_document(decoded_filename)
        if success:
            return {"message": f"Document '{decoded_filename}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rate-answer")
async def rate_answer(rating: AnswerRating):
    """Rate the quality of an answer for improvement"""
    try:
        rating_data = {
            "query": rating.query,
            "rating": rating.rating,
            "feedback": rating.feedback,
            "improvement_suggestions": rating.improvement_suggestions,
            "timestamp": datetime.now().isoformat()
        }
        answer_ratings.append(rating_data)
        
        return {"message": "Rating recorded successfully", "rating_id": len(answer_ratings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ratings")
async def get_ratings():
    """Get all answer ratings (for analytics)"""
    return {"ratings": answer_ratings, "total": len(answer_ratings)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        documents = document_processor.get_document_list()
        total_documents = len(documents)
        total_chunks = sum(doc.chunk_count for doc in documents)
        total_ratings = len(answer_ratings)
        
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "total_ratings": total_ratings,
            "average_rating": sum(r["rating"] for r in answer_ratings) / total_ratings if total_ratings > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
