document.addEventListener('DOMContentLoaded', () => {
    // Modal elements
    const modal = document.getElementById('file-view-modal');
    const modalContent = document.getElementById('modal-content');
    const modalTitle = document.getElementById('modal-title');
    const closeModalButton = document.getElementById('close-modal');

    // Upload elements
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const uploadForm = document.getElementById('upload-form');
    const statusMessage = document.getElementById('status-message');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const uploadBox = document.getElementById('upload-box');

    // Elements for upload box state
    const uploadPrompt = document.getElementById('upload-prompt');
    const fileSelectedState = document.getElementById('file-selected-state');
    const selectedFileName = document.getElementById('selected-file-name');

    // Search elements
    const searchBar = document.getElementById('search-bar');
    const resultsContainer = document.getElementById('results-container');
    
    // Make the entire upload box clickable
    uploadBox.addEventListener('click', () => fileInput.click());

    // Enable upload button and update UI when a file is selected
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) {
            uploadPrompt.classList.add('hidden');
            fileSelectedState.classList.remove('hidden');
            selectedFileName.textContent = file.name;
            uploadButton.disabled = false;
        } else {
            uploadPrompt.classList.remove('hidden');
            fileSelectedState.classList.add('hidden');
            selectedFileName.textContent = '';
            uploadButton.disabled = true;
        }
    });

    // Handle file upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        progressContainer.classList.remove('hidden');
        progressBar.style.width = '0%';
        setTimeout(() => { progressBar.style.width = '100%'; }, 100);

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const result = await response.json();
            
            statusMessage.textContent = result.message || result.error;
            statusMessage.classList.toggle('text-green-500', response.ok);
            statusMessage.classList.toggle('text-red-500', !response.ok);

        } catch (error) {
            statusMessage.textContent = `Upload failed: ${error.message}`;
            statusMessage.classList.add('text-red-500');
        } finally {
            setTimeout(() => {
                progressContainer.classList.add('hidden');
                uploadForm.reset();
                fileInput.dispatchEvent(new Event('change'));
                setTimeout(() => { statusMessage.textContent = ''; }, 3000);
            }, 1000);
        }
    });

    // Handle search input
    searchBar.addEventListener('input', async () => {
        const query = searchBar.value.trim();
        if (query.length === 0) {
            resultsContainer.innerHTML = '';
            return;
        }
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            displayResults(results);
            // Always scroll to results container after a search
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (error) {
            console.error('Search error:', error);
            resultsContainer.innerHTML = '<p class="text-red-500">Error fetching results.</p>';
        }
    });
    
    // Function to display search results
    function displayResults(results) {
        if (results.length === 0) {
            resultsContainer.innerHTML = '<p class="text-gray-500">No documents found.</p>';
            return;
        }
        resultsContainer.innerHTML = results.map(result => `
            <div class="bg-white p-5 rounded-lg shadow mb-4 border border-gray-200 hover:shadow-md transition-shadow cursor-pointer result-card" data-filename="${result.filename}" data-title="${result.title}">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-semibold text-blue-800">${result.title}</h3>
                        <div class="text-sm text-gray-600 mt-2 snippet">${result.snippet}</div>
                    </div>
                    <a href="/download/${result.filename}" class="text-gray-400 hover:text-blue-600 download-link" title="Download file">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="pointer-events: none;">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                    </a>
                </div>
                <div class="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                    <div>
                        <span class="font-semibold">By:</span>
                        <span class="ml-1">${result.uploaded_by}</span>
                        <span class="mx-2 text-gray-300">|</span>
                        <span class="font-semibold">File:</span>
                        <span class="ml-1">${result.filename}</span>
                    </div>
                    <div class="text-right">
                         <div class="font-medium">${result.uploaded_at || ''}</div>
                         <span class="mt-1 inline-block bg-gray-200 text-gray-800 px-2 py-1 rounded-full">${result.category}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // --- MODAL LOGIC ---
    async function openFileModal(filename, title) {
        try {
            const response = await fetch(`/view/${filename}`);
            if (!response.ok) throw new Error('Could not fetch file content.');
            const data = await response.json();
            modalTitle.textContent = title;
            modalContent.textContent = data.content;
            modal.classList.remove('hidden');
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    function closeModal() {
        modal.classList.add('hidden');
        modalTitle.textContent = '';
        modalContent.textContent = '';
    }

    // Event listener for opening the modal
    resultsContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.result-card');
        const downloadLink = e.target.closest('.download-link');
        if (downloadLink) return; // Don't open modal if download icon is clicked
        if (card) {
            openFileModal(card.dataset.filename, card.dataset.title);
        }
    });
    
    // Event listeners for closing the modal
    closeModalButton.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape" && !modal.classList.contains('hidden')) closeModal();
    });
});

