class CityHallAssistant {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.focusSearchInput();
    }

    bindEvents() {
        // Form submission
        document.getElementById('questionForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleQuestionSubmit();
        });

        // New question button
        document.getElementById('newQuestionBtn').addEventListener('click', () => {
            this.showNewQuestionForm();
        });

        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.hideError();
            this.focusSearchInput();
        });

        // Enter key handling
        document.getElementById('questionInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleQuestionSubmit();
            }
        });
    }

    focusSearchInput() {
        const input = document.getElementById('questionInput');
        input.focus();
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    async handleQuestionSubmit() {
        const questionInput = document.getElementById('questionInput');
        const question = questionInput.value.trim();

        if (!question) {
            this.showError('Please enter a question.');
            return;
        }

        // Show loading state
        this.showLoading();
        this.hideResults();
        this.hideError();

        // Disable form during request
        this.setFormEnabled(false);

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });

            const data = await response.json();

            if (data.success) {
                this.showResults(data);
            } else {
                this.showError(data.error || 'An unexpected error occurred.');
            }
        } catch (error) {
            console.error('Request failed:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoading();
            this.setFormEnabled(true);
        }
    }

    showLoading() {
        const loadingSection = document.getElementById('loadingSection');
        loadingSection.style.display = 'block';
        loadingSection.classList.add('fade-in');
        
        // Scroll to loading section
        loadingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    hideLoading() {
        const loadingSection = document.getElementById('loadingSection');
        loadingSection.style.display = 'none';
        loadingSection.classList.remove('fade-in');
    }

    showResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const questionDisplay = document.getElementById('questionDisplay');
        const answerText = document.getElementById('answerText');
        const sourcesSection = document.getElementById('sourcesSection');
        const sourcesList = document.getElementById('sourcesList');

        // Display question
        questionDisplay.textContent = data.question;

        // Display answer
        answerText.innerHTML = this.formatAnswer(data.answer);

        // Display sources if available
        if (data.sources && data.sources.length > 0) {
            sourcesList.innerHTML = this.formatSources(data.sources);
            sourcesSection.style.display = 'block';
        } else {
            sourcesSection.style.display = 'none';
        }

        // Show results section with animation
        resultsSection.style.display = 'block';
        resultsSection.classList.add('slide-up');
        
        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'none';
        resultsSection.classList.remove('slide-up');
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        errorSection.classList.add('fade-in');
        
        // Scroll to error
        setTimeout(() => {
            errorSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    }

    hideError() {
        const errorSection = document.getElementById('errorSection');
        errorSection.style.display = 'none';
        errorSection.classList.remove('fade-in');
    }

    formatAnswer(answer) {
        if (!answer) {
            return '<p class="text-muted">No answer provided.</p>';
        }

        // Convert line breaks to paragraphs
        const paragraphs = answer.split('\n\n').filter(p => p.trim());
        
        if (paragraphs.length > 1) {
            return paragraphs.map(p => `<p>${this.escapeHtml(p.trim())}</p>`).join('');
        } else {
            return `<p>${this.escapeHtml(answer)}</p>`;
        }
    }

    formatSources(sources) {
        if (!sources || sources.length === 0) {
            return '<p class="text-muted">No sources available.</p>';
        }

        return sources.map((source, index) => {
            const title = source.title || source.filename || `Source ${index + 1}`;
            const snippet = source.text || source.snippet || source.content || 'No preview available';
            const url = source.url || source.link || '#';
            const score = source.score || 0;
            const pageNumber = source.page || source.pageNumber || 'p. 1';
            
            // Extract document type and set appropriate icon
            let docIcon = 'fas fa-file-alt';
            let docType = 'DOCUMENT';
            
            if (title.toLowerCase().includes('.pdf')) {
                docIcon = 'fas fa-file-pdf';
                docType = 'DOCUMENT';
            } else if (title.toLowerCase().includes('.docx') || title.toLowerCase().includes('.doc')) {
                docIcon = 'fas fa-file-word';
                docType = 'DOCUMENT';
            } else if (title.toLowerCase().includes('faq')) {
                docIcon = 'fas fa-question-circle';
                docType = 'TEXT';
            }
            
            return `
                <div class="source-reference">
                    <div class="source-header">
                        <div class="source-document-info">
                            <div class="source-doc-icon">
                                <i class="${docIcon}"></i>
                            </div>
                            <div class="source-doc-details">
                                <div class="source-doc-title">${this.escapeHtml(title)}</div>
                                <div class="source-reference-number">
                                    <span class="reference-index">${index + 1}</span>
                                    <i class="fas fa-chevron-right mx-2"></i>
                                    <span class="page-number">${pageNumber}</span>
                                    <span class="section-number">${index + 1}. ${this.escapeHtml(this.truncateText(snippet, 50))}</span>
                                </div>
                            </div>
                        </div>
                        <div class="source-preview">
                            <div class="doc-type-badge">${docType}</div>
                            <div class="source-thumbnail">
                                <i class="${docIcon}" style="font-size: 2rem; color: #6c757d;"></i>
                            </div>
                        </div>
                    </div>
                    <div class="source-content">
                        <div class="source-snippet-full">
                            ${this.escapeHtml(this.truncateText(snippet, 300))}
                        </div>
                        ${score > 0 ? `<div class="source-score">Relevance: ${Math.round(score * 100)}%</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    showNewQuestionForm() {
        // Clear the input
        document.getElementById('questionInput').value = '';
        
        // Hide results and errors
        this.hideResults();
        this.hideError();
        
        // Focus and scroll to input
        this.focusSearchInput();
    }

    setFormEnabled(enabled) {
        const questionInput = document.getElementById('questionInput');
        const askBtn = document.getElementById('askBtn');
        
        questionInput.disabled = !enabled;
        askBtn.disabled = !enabled;
        
        if (enabled) {
            askBtn.innerHTML = '<i class="fas fa-search me-2"></i>Ask';
        } else {
            askBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Asking...';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength).replace(/\s+\S*$/, '') + '...';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CityHallAssistant();
});

// Handle page visibility to refocus input when user returns to tab
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        const questionInput = document.getElementById('questionInput');
        if (questionInput && !questionInput.disabled) {
            setTimeout(() => questionInput.focus(), 100);
        }
    }
});

// Add some utility functions for enhanced UX
window.addEventListener('beforeunload', (e) => {
    // Warn user if they're leaving while a request is in progress
    const askBtn = document.getElementById('askBtn');
    if (askBtn && askBtn.disabled) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? Your request is still processing.';
        return e.returnValue;
    }
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const questionInput = document.getElementById('questionInput');
        if (questionInput) {
            questionInput.focus();
            questionInput.select();
        }
    }
    
    // Escape to clear or hide results
    if (e.key === 'Escape') {
        const resultsSection = document.getElementById('resultsSection');
        const errorSection = document.getElementById('errorSection');
        
        if (resultsSection.style.display !== 'none') {
            // If results are showing, clear them
            const assistant = new CityHallAssistant();
            assistant.showNewQuestionForm();
        } else if (errorSection.style.display !== 'none') {
            // If error is showing, hide it
            const assistant = new CityHallAssistant();
            assistant.hideError();
            assistant.focusSearchInput();
        }
    }
});
