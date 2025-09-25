// AI Knowledge Base Search & Enrichment - Frontend JavaScript

class KnowledgeBaseApp {
    constructor() {
        this.currentAnswer = null;
        this.initializeEventListeners();
        this.loadDocuments();
    }

    initializeEventListeners() {
        // File upload
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Search form
        document.getElementById('search-form').addEventListener('submit', this.handleSearch.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        const files = e.dataTransfer.files;
        this.uploadFiles(files);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        if (files.length === 0) return;

        const uploadResults = document.getElementById('upload-results');
        const uploadProgress = document.getElementById('upload-progress');
        const progressBar = uploadProgress.querySelector('.progress-bar');

        uploadResults.innerHTML = '';
        uploadProgress.style.display = 'block';
        progressBar.style.width = '0%';

        let completed = 0;
        const total = files.length;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    this.showUploadSuccess(file.name, result);
                } else {
                    this.showUploadError(file.name, result.detail);
                }
            } catch (error) {
                this.showUploadError(file.name, error.message);
            }

            completed++;
            progressBar.style.width = `${(completed / total) * 100}%`;
        }

        setTimeout(() => {
            uploadProgress.style.display = 'none';
            this.loadDocuments();
        }, 1000);
    }

    showUploadSuccess(filename, metadata) {
        const uploadResults = document.getElementById('upload-results');
        const alert = document.createElement('div');
        alert.className = 'alert alert-success';
        alert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>${filename}</strong> uploaded successfully! 
            (${metadata.chunk_count} chunks processed)
        `;
        uploadResults.appendChild(alert);
    }

    showUploadError(filename, error) {
        const uploadResults = document.getElementById('upload-results');
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            <strong>${filename}</strong> upload failed: ${error}
        `;
        uploadResults.appendChild(alert);
    }

    async handleSearch(e) {
        e.preventDefault();
        
        const query = document.getElementById('search-query').value.trim();
        if (!query) return;

        const includeConfidence = document.getElementById('include-confidence').checked;
        const includeEnrichment = document.getElementById('include-enrichment').checked;

        this.showLoadingModal();

        try {
            const formData = new FormData();
            formData.append('query', query);
            formData.append('include_confidence', includeConfidence);
            formData.append('include_enrichment', includeEnrichment);

            const response = await fetch('/search', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.displaySearchResults(result);
            } else {
                this.showError('Search failed: ' + result.detail);
            }
        } catch (error) {
            this.showError('Search failed: ' + error.message);
        } finally {
            this.hideLoadingModal();
        }
    }

    displaySearchResults(result) {
        this.currentAnswer = result;
        
        // Show results section
        document.getElementById('results-section').style.display = 'block';
        
        // Display confidence badge
        this.displayConfidenceBadge(result.confidence, result.confidence_level);
        
        // Display answer
        this.displayAnswer(result.answer);
        
        // Display sources
        this.displaySources(result.sources);
        
        // Display missing info
        this.displayMissingInfo(result.missing_info);
        
        // Display enrichment suggestions
        this.displayEnrichmentSuggestions(result.enrichment_suggestions);
        
        // Display rating section
        this.displayRatingSection(result);
        
        // Scroll to results
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
    }

    displayConfidenceBadge(confidence, level) {
        const badge = document.getElementById('confidence-badge');
        const percentage = Math.round(confidence * 100);
        
        badge.innerHTML = `
            <span class="confidence-badge confidence-${level}">
                <i class="fas fa-chart-line me-1"></i>
                ${percentage}% Confidence (${level.toUpperCase()})
            </span>
        `;
    }

    displayAnswer(answer) {
        const answerContent = document.getElementById('answer-content');
        answerContent.innerHTML = `
            <div class="answer-content">${answer}</div>
        `;
    }

    displaySources(sources) {
        const sourcesSection = document.getElementById('sources-section');
        
        if (sources.length === 0) {
            sourcesSection.innerHTML = '';
            return;
        }

        let sourcesHtml = '<h6><i class="fas fa-file-alt me-2"></i>Sources</h6>';
        
        sources.forEach((source, index) => {
            sourcesHtml += `
                <div class="source-item">
                    <div class="source-filename">
                        <i class="fas fa-file me-2"></i>
                        ${source.filename} (Chunk ${source.chunk_index + 1})
                        <span class="source-similarity ms-2">
                            ${Math.round(source.similarity_score * 100)}% match
                        </span>
                    </div>
                    <div class="source-preview">${source.content_preview}</div>
                </div>
            `;
        });

        sourcesSection.innerHTML = sourcesHtml;
    }

    displayMissingInfo(missingInfo) {
        const missingInfoSection = document.getElementById('missing-info-section');
        
        if (missingInfo.length === 0) {
            missingInfoSection.innerHTML = '';
            return;
        }

        let missingHtml = '<h6><i class="fas fa-exclamation-triangle me-2"></i>Missing Information</h6>';
        
        missingInfo.forEach((info, index) => {
            const priorityStars = '★'.repeat(info.priority) + '☆'.repeat(5 - info.priority);
            missingHtml += `
                <div class="missing-info-item">
                    <div class="missing-info-type">
                        <i class="fas fa-${this.getMissingInfoIcon(info.type)} me-2"></i>
                        ${info.type.replace('_', ' ').toUpperCase()}
                        <span class="ms-2">${priorityStars}</span>
                    </div>
                    <div class="missing-info-description">${info.description}</div>
                    <div class="missing-info-action">
                        <i class="fas fa-lightbulb me-1"></i>
                        ${info.suggested_action}
                    </div>
                </div>
            `;
        });

        missingInfoSection.innerHTML = missingHtml;
    }

    displayEnrichmentSuggestions(suggestions) {
        const enrichmentSection = document.getElementById('enrichment-section');
        
        if (suggestions.length === 0) {
            enrichmentSection.innerHTML = '';
            return;
        }

        let enrichmentHtml = '<h6><i class="fas fa-magic me-2"></i>Enrichment Suggestions</h6>';
        
        suggestions.forEach((suggestion, index) => {
            const effortColor = this.getEffortColor(suggestion.estimated_effort);
            enrichmentHtml += `
                <div class="enrichment-item">
                    <div class="enrichment-type">
                        <i class="fas fa-${this.getEnrichmentIcon(suggestion.type)} me-2"></i>
                        ${suggestion.type.replace('_', ' ').toUpperCase()}
                        <span class="enrichment-confidence ms-2">
                            ${Math.round(suggestion.confidence * 100)}% confidence
                        </span>
                    </div>
                    <div class="enrichment-description">${suggestion.description}</div>
                    <div class="enrichment-action">
                        <i class="fas fa-cog me-1"></i>
                        ${suggestion.action}
                        <span class="ms-2 badge ${effortColor}">${suggestion.estimated_effort} effort</span>
                    </div>
                </div>
            `;
        });

        enrichmentSection.innerHTML = enrichmentHtml;
    }

    displayRatingSection(result) {
        const ratingSection = document.getElementById('rating-section');
        
        ratingSection.innerHTML = `
            <div class="border-top pt-3">
                <h6><i class="fas fa-star me-2"></i>Rate This Answer</h6>
                <p class="text-muted mb-3">Help us improve by rating the quality of this answer</p>
                <div class="rating-stars" id="rating-stars">
                    <span class="star" data-rating="1">★</span>
                    <span class="star" data-rating="2">★</span>
                    <span class="star" data-rating="3">★</span>
                    <span class="star" data-rating="4">★</span>
                    <span class="star" data-rating="5">★</span>
                </div>
                <div class="mt-3">
                    <textarea class="form-control" id="rating-feedback" placeholder="Optional feedback..." rows="2"></textarea>
                </div>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="app.submitRating()">
                        <i class="fas fa-paper-plane me-2"></i>Submit Rating
                    </button>
                </div>
                <div class="processing-time mt-2">
                    <i class="fas fa-clock me-1"></i>
                    Processed in ${result.processing_time.toFixed(2)} seconds
                </div>
            </div>
        `;

        // Add star rating functionality
        this.initializeStarRating();
    }

    initializeStarRating() {
        const stars = document.querySelectorAll('.star');
        let currentRating = 0;

        stars.forEach((star, index) => {
            star.addEventListener('mouseenter', () => {
                this.highlightStars(index + 1);
            });

            star.addEventListener('click', () => {
                currentRating = index + 1;
                this.highlightStars(currentRating);
            });
        });

        document.getElementById('rating-stars').addEventListener('mouseleave', () => {
            this.highlightStars(currentRating);
        });
    }

    highlightStars(rating) {
        const stars = document.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    async submitRating() {
        const stars = document.querySelectorAll('.star.active');
        const rating = stars.length;
        const feedback = document.getElementById('rating-feedback').value;

        if (rating === 0) {
            this.showError('Please select a rating');
            return;
        }

        try {
            const response = await fetch('/rate-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: this.currentAnswer.query || document.getElementById('search-query').value,
                    rating: rating,
                    feedback: feedback
                })
            });

            if (response.ok) {
                this.showSuccess('Thank you for your feedback!');
                document.getElementById('rating-feedback').value = '';
                this.highlightStars(0);
            } else {
                this.showError('Failed to submit rating');
            }
        } catch (error) {
            this.showError('Failed to submit rating: ' + error.message);
        }
    }

    async loadDocuments() {
        const documentsList = document.getElementById('documents-list');
        
        try {
            const response = await fetch('/documents');
            const documents = await response.json();

            if (documents.length === 0) {
                documentsList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-folder-open"></i>
                        <h6>No documents uploaded yet</h6>
                        <p>Upload some documents to start building your knowledge base</p>
                    </div>
                `;
            } else {
                let documentsHtml = '';
                documents.forEach(doc => {
                    const statusClass = doc.processing_status === 'completed' ? 'status-completed' : 'status-error';
                    documentsHtml += `
                        <div class="document-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <div class="document-filename">
                                        <i class="fas fa-file me-2"></i>
                                        ${doc.filename}
                                    </div>
                                    <div class="document-meta">
                                        Uploaded: ${new Date(doc.upload_date).toLocaleDateString()} | 
                                        Chunks: ${doc.chunk_count} | 
                                        Size: ${(doc.file_size / 1024).toFixed(1)} KB
                                    </div>
                                </div>
                                <div>
                                    <span class="document-status ${statusClass}">
                                        ${doc.processing_status}
                                    </span>
                                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="app.deleteDocument('${doc.filename}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                documentsList.innerHTML = documentsHtml;
            }

            // Update document count
            document.getElementById('document-count').textContent = `${documents.length} documents`;
        } catch (error) {
            documentsList.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Failed to load documents: ${error.message}
                </div>
            `;
        }
    }

    async deleteDocument(filename) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/documents/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccess(`Document "${filename}" deleted successfully`);
                this.loadDocuments();
            } else {
                const result = await response.json();
                this.showError('Failed to delete document: ' + result.detail);
            }
        } catch (error) {
            this.showError('Failed to delete document: ' + error.message);
        }
    }

    showLoadingModal() {
        const modal = new bootstrap.Modal(document.getElementById('loading-modal'));
        modal.show();
    }

    hideLoadingModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loading-modal'));
        if (modal) {
            modal.hide();
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    getMissingInfoIcon(type) {
        const icons = {
            'document': 'file',
            'data': 'database',
            'context': 'info-circle',
            'specific_fact': 'lightbulb'
        };
        return icons[type] || 'question-circle';
    }

    getEnrichmentIcon(type) {
        const icons = {
            'procedure_document': 'list-ol',
            'reference_document': 'book',
            'temporal_document': 'calendar',
            'factual_document': 'file-alt',
            'document_upload': 'upload'
        };
        return icons[type] || 'plus-circle';
    }

    getEffortColor(effort) {
        const colors = {
            'low': 'bg-success',
            'medium': 'bg-warning',
            'high': 'bg-danger'
        };
        return colors[effort] || 'bg-secondary';
    }
}

// Initialize the application
const app = new KnowledgeBaseApp();
