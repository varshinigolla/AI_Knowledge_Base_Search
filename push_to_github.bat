@echo off
echo ========================================
echo AI Knowledge Base - GitHub Push Script
echo ========================================
echo.

echo Step 1: Checking Git installation...
git --version
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo Git is installed successfully!
echo.

echo Step 2: Initializing Git repository...
git init
echo.

echo Step 3: Creating .gitignore file...
echo # Python > .gitignore
echo __pycache__/ >> .gitignore
echo *.py[cod] >> .gitignore
echo *$py.class >> .gitignore
echo *.so >> .gitignore
echo .Python >> .gitignore
echo build/ >> .gitignore
echo develop-eggs/ >> .gitignore
echo dist/ >> .gitignore
echo downloads/ >> .gitignore
echo eggs/ >> .gitignore
echo .eggs/ >> .gitignore
echo lib/ >> .gitignore
echo lib64/ >> .gitignore
echo parts/ >> .gitignore
echo sdist/ >> .gitignore
echo var/ >> .gitignore
echo wheels/ >> .gitignore
echo *.egg-info/ >> .gitignore
echo .installed.cfg >> .gitignore
echo *.egg >> .gitignore
echo. >> .gitignore
echo # Virtual Environment >> .gitignore
echo ai_knowledge_env/ >> .gitignore
echo venv/ >> .gitignore
echo env/ >> .gitignore
echo. >> .gitignore
echo # Environment Variables >> .gitignore
echo .env >> .gitignore
echo .env.local >> .gitignore
echo .env.production >> .gitignore
echo. >> .gitignore
echo # Database >> .gitignore
echo chroma_db/ >> .gitignore
echo uploads/ >> .gitignore
echo. >> .gitignore
echo # IDE >> .gitignore
echo .vscode/ >> .gitignore
echo .idea/ >> .gitignore
echo *.swp >> .gitignore
echo *.swo >> .gitignore
echo. >> .gitignore
echo # OS >> .gitignore
echo .DS_Store >> .gitignore
echo Thumbs.db >> .gitignore
echo. >> .gitignore
echo # Logs >> .gitignore
echo *.log >> .gitignore
echo. >> .gitignore
echo # Temporary files >> .gitignore
echo *.tmp >> .gitignore
echo *.temp >> .gitignore
echo .gitignore file created!
echo.

echo Step 4: Configuring Git...
git config --global user.name "Varshini"
git config --global user.email "varshinigolla@example.com"
echo Git configured!
echo.

echo Step 5: Adding GitHub remote...
git remote add origin git@github.com:varshinigolla/AI-Knowledge-Base-Search.git
echo Remote added!
echo.

echo Step 6: Adding all files...
git add .
echo Files added!
echo.

echo Step 7: Making initial commit...
git commit -m "Initial commit: AI-Powered Knowledge Base Search & Enrichment System

Features:
- Document upload and processing (PDF, TXT, DOCX, XLSX, CSV)
- Natural language search with AI-powered answers
- Confidence scoring and completeness checking
- Enrichment suggestions for knowledge gaps
- Modern web interface with real-time processing
- Answer quality rating system
- Vector database with ChromaDB
- RAG pipeline with OpenAI GPT integration"
echo Commit created!
echo.

echo Step 8: Pushing to GitHub...
git branch -M main
git push -u origin main
echo.

echo ========================================
echo SUCCESS: Project pushed to GitHub!
echo ========================================
echo Your AI Knowledge Base is now available at:
echo https://github.com/varshinigolla/AI-Knowledge-Base-Search
echo ========================================
pause
