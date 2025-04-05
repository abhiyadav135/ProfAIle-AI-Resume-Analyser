// Dropdown functionality for mobile
document.querySelectorAll('.dropdown').forEach(dropdown => {
    dropdown.addEventListener('click', (e) => {
        if (window.innerWidth < 768) {
            const content = dropdown.querySelector('.dropdown-content');
            content.style.display = content.style.display === 'block' ? 'none' : 'block';
        }
    });
});

// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.matches('.dropbtn')) {
        document.querySelectorAll('.dropdown-content').forEach(content => {
            if (window.innerWidth >= 768) return;
            content.style.display = 'none';
        });
    }
});

// Sign In button handler
document.querySelector('.signin-btn').addEventListener('click', () => {
    // Add your sign in logic here
    alert('Sign In clicked!');
});
// File upload handling
const uploadBox = document.querySelector('.upload-box');
const fileInput = document.getElementById('resume-upload');

fileInput.addEventListener('change', function(e) {
    if (e.target.files.length) {
        const fileName = e.target.files[0].name;
        uploadBox.innerHTML = `
            <p>Selected file: <strong>${fileName}</strong></p>
            <button class="upload-btn" style="background: #10B981;">
                Analyze Now
            </button>
        `;
    }
});

// Drag and drop functionality
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadBox.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    uploadBox.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadBox.addEventListener(eventName, unhighlight, false);
});

function highlight() {
    uploadBox.style.background = 'rgba(255, 255, 255, 0.3)';
    uploadBox.style.borderColor = 'rgba(255, 255, 255, 0.8)';
}

function unhighlight() {
    uploadBox.style.background = 'rgba(255, 255, 255, 0.2)';
    uploadBox.style.borderColor = 'rgba(255, 255, 255, 0.4)';
}

uploadBox.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = files;
    const event = new Event('change');
    fileInput.dispatchEvent(event);
}
// Add this to handle the new button's file selection
document.getElementById('hidden-file-input').addEventListener('change', function(e) {
    if (e.target.files.length) {
        // You can add the same file handling logic as your upload box
        alert(`Resume selected: ${e.target.files[0].name}`);
        // Or redirect to analysis page:
        // window.location.href = '/analyze';
    }
});
// FAQ Dropdown Functionality
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const faqItem = question.parentElement;
        faqItem.classList.toggle('active');
        
        // Close other open items
        document.querySelectorAll('.faq-item').forEach(item => {
            if (item !== faqItem && item.classList.contains('active')) {
                item.classList.remove('active');
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('resume-upload');
    const fileNameDisplay = document.getElementById('file-name');
    const uploadButton = document.getElementById('upload-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
  
    // File selection handler
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      
      if (file) {
        // Validate file
        const isValid = validateFile(file);
        
        if (isValid) {
          fileNameDisplay.textContent = file.name;
          fileNameDisplay.style.color = '#333';
          uploadButton.disabled = false;
          errorMessage.textContent = '';
        } else {
          fileInput.value = ''; // Clear invalid file
          fileNameDisplay.textContent = 'No file selected';
          fileNameDisplay.style.color = '#666';
          uploadButton.disabled = true;
        }
      }
    });
  
    // Upload handler
    uploadButton.addEventListener('click', async () => {
      const file = fileInput.files[0];
      
      if (!file) return;
  
      try {
        // Show loading state
        uploadButton.disabled = true;
        loadingSpinner.classList.remove('hidden');
        errorMessage.textContent = '';
  
        // Prepare form data
        const formData = new FormData();
        formData.append('resume', file);
  
        // Send to backend
        const response = await fetch('https://your-backend-api.com/upload', {
          method: 'POST',
          body: formData
          // Add headers if needed (e.g., auth tokens)
        });
  
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }
  
        const result = await response.json();
        handleUploadSuccess(result);
        
      } catch (error) {
        errorMessage.textContent = `Upload failed: ${error.message}`;
        console.error('Upload error:', error);
      } finally {
        loadingSpinner.classList.add('hidden');
        uploadButton.disabled = false;
      }
    });
  
    // File validation
    function validateFile(file) {
      const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      const maxSize = 5 * 1024 * 1024; // 5MB
  
      if (!validTypes.includes(file.type)) {
        errorMessage.textContent = 'Invalid file type. Please upload PDF or Word documents.';
        return false;
      }
  
      if (file.size > maxSize) {
        errorMessage.textContent = 'File too large (max 5MB)';
        return false;
      }
  
      return true;
    }
  
    // Handle successful upload
    function handleUploadSuccess(response) {
      // Redirect or update UI with results
      console.log('Upload successful:', response);
      alert('Resume uploaded successfully!');
      // window.location.href = `/results?reportId=${response.reportId}`;
    }
  });