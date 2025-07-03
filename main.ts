// TypeScript interfaces for type safety
interface SearchValues {
    websites: string[];
    searchTerms: string;
    limit: number;
    day: number;
    month: string;
    year: number;
    keywords: string;
}

interface ApiResponse {
    status: 'success' | 'error';
    message: string;
    data?: any;
    articles?: any[];
    html: string;
}

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Function to make API requests
async function makeApiRequest(endpoint: string, data: SearchValues): Promise<ApiResponse> {
    const url = `${API_BASE_URL}${endpoint}`;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    } catch (error) {
        return {
            status: 'error',
            message: 'Network error or server unavailable',
            html: 'no body'
        };
    }
}
// Function to display results in the activity log
function displayResults(searchType: string, response: ApiResponse): void {
    const activityLog = document.getElementById('activity-log');
    if (!activityLog) return;

    const timestamp = new Date().toLocaleString();
    const resultDiv = document.createElement('div');
    resultDiv.style.marginBottom = '10px';
    resultDiv.style.padding = '10px';
    resultDiv.style.border = '1px solid #ddd';
    resultDiv.style.borderRadius = '4px';
    
    if (response.status === 'success') {
        resultDiv.style.backgroundColor = '#d4edda';
        resultDiv.innerHTML = response.html;
    } else {
        resultDiv.style.backgroundColor = '#f8d7da';
        resultDiv.innerHTML = `
            <strong>${timestamp} - ${searchType} Error:</strong><br>
            ${response.message}
        `;
    }
    
    activityLog.prepend(resultDiv);
}

// Function to get values from "Search a site" form
function getSiteSearchValues(): SearchValues {
    // Get all checked website checkboxes
    const websiteCheckboxes = document.querySelectorAll('input[name="websites"]:checked') as NodeListOf<HTMLInputElement>;
    const websites = Array.from(websiteCheckboxes).map(checkbox => checkbox.value);

    return {
        websites: websites || ["0"],
        searchTerms: (document.getElementById('search') as HTMLInputElement)?.value || '',
        limit: Number((document.getElementById('amount') as HTMLInputElement)?.value) || 5,
        day: Number((document.getElementById('day') as HTMLSelectElement)?.value) || 0,
        month: (document.getElementById('month') as HTMLSelectElement)?.value || '',
        year: Number((document.getElementById('year') as HTMLSelectElement)?.value) || 0,
        keywords: (document.getElementById('keywords') as HTMLInputElement)?.value || ''
    };
}

// Function to get values from "Search database" form
function getDatabaseSearchValues(): SearchValues {
    // Get all checked website checkboxes from database form
    const websiteCheckboxes = document.querySelectorAll('input[name="database-websites"]:checked') as NodeListOf<HTMLInputElement>;
    const websites = Array.from(websiteCheckboxes).map(checkbox => checkbox.value);

    return {
        websites: websites,
        searchTerms: (document.getElementById('database-search') as HTMLInputElement)?.value || '',
        limit: Number((document.getElementById('database-amount') as HTMLInputElement)?.value) || 5,
        day: Number((document.getElementById('database-day') as HTMLSelectElement)?.value) || 0,
        month: (document.getElementById('database-month') as HTMLSelectElement)?.value || '',
        year: Number((document.getElementById('database-year') as HTMLSelectElement)?.value) || 0,
        keywords: (document.getElementById('database-keywords') as HTMLInputElement)?.value || ''
    };
}

// DOM Content Loaded event handler
document.addEventListener('DOMContentLoaded', function(): void {
    // Dropdown functionality for site search
    const websiteDropdownButton = document.getElementById('websiteDropdownButton');
    const websiteDropdownContent = document.getElementById('websiteDropdownContent');
    const websiteDropdownText = document.getElementById('websiteDropdownText');
    const websiteDropdownArrow = websiteDropdownButton?.querySelector('.dropdown-arrow');

    if (websiteDropdownButton && websiteDropdownContent) {
        websiteDropdownButton.addEventListener('click', function(e: Event): void {
            e.preventDefault();
            e.stopPropagation();
            websiteDropdownContent.classList.toggle('show');
            websiteDropdownArrow?.classList.toggle('open');
        });

        // Update dropdown text when selections change
        const updateWebsiteDropdownText = () => {
            const checkedBoxes = websiteDropdownContent.querySelectorAll('input[name="websites"]:checked');
            const count = checkedBoxes.length;
            if (websiteDropdownText) {
                if (count === 0) {
                    websiteDropdownText.textContent = 'Select websites...';
                } else if (count === 1) {
                    const label = checkedBoxes[0].parentElement?.querySelector('label')?.textContent || '';
                    websiteDropdownText.textContent = label;
                } else {
                    websiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        };

        // Add change listeners to checkboxes
        websiteDropdownContent.querySelectorAll('input[name="websites"]').forEach(checkbox => {
            checkbox.addEventListener('change', updateWebsiteDropdownText);
        });

        // Prevent dropdown from closing when clicking inside
        websiteDropdownContent.addEventListener('click', function(e: Event): void {
            e.stopPropagation();
        });
    }

    // Dropdown functionality for database search
    const databaseWebsiteDropdownButton = document.getElementById('databaseWebsiteDropdownButton');
    const databaseWebsiteDropdownContent = document.getElementById('databaseWebsiteDropdownContent');
    const databaseWebsiteDropdownText = document.getElementById('databaseWebsiteDropdownText');
    const databaseWebsiteDropdownArrow = databaseWebsiteDropdownButton?.querySelector('.dropdown-arrow');

    if (databaseWebsiteDropdownButton && databaseWebsiteDropdownContent) {
        databaseWebsiteDropdownButton.addEventListener('click', function(e: Event): void {
            e.preventDefault();
            e.stopPropagation();
            databaseWebsiteDropdownContent.classList.toggle('show');
            databaseWebsiteDropdownArrow?.classList.toggle('open');
        });

        // Update dropdown text when selections change
        const updateDatabaseWebsiteDropdownText = () => {
            const checkedBoxes = databaseWebsiteDropdownContent.querySelectorAll('input[name="database-websites"]:checked');
            const count = checkedBoxes.length;
            if (databaseWebsiteDropdownText) {
                if (count === 0) {
                    databaseWebsiteDropdownText.textContent = 'Select websites...';
                } else if (count === 1) {
                    const label = checkedBoxes[0].parentElement?.querySelector('label')?.textContent || '';
                    databaseWebsiteDropdownText.textContent = label;
                } else {
                    databaseWebsiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        };

        // Add change listeners to checkboxes
        databaseWebsiteDropdownContent.querySelectorAll('input[name="database-websites"]').forEach(checkbox => {
            checkbox.addEventListener('change', updateDatabaseWebsiteDropdownText);
        });

        // Prevent dropdown from closing when clicking inside
        databaseWebsiteDropdownContent.addEventListener('click', function(e: Event): void {
            e.stopPropagation();
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event): void {
        if (websiteDropdownButton && websiteDropdownContent && !websiteDropdownButton.contains(event.target as Node)) {
            websiteDropdownContent.classList.remove('show');
            websiteDropdownArrow?.classList.remove('open');
        }
        if (databaseWebsiteDropdownButton && databaseWebsiteDropdownContent && !databaseWebsiteDropdownButton.contains(event.target as Node)) {
            databaseWebsiteDropdownContent.classList.remove('show');
            databaseWebsiteDropdownArrow?.classList.remove('open');
        }
    });

    // Select All functionality for site search
    const selectAllCheckbox = document.getElementById('selectAll') as HTMLInputElement;
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function(): void {
            const websiteCheckboxes = document.querySelectorAll('input[name="websites"]') as NodeListOf<HTMLInputElement>;
            websiteCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            // Update dropdown text
            if (websiteDropdownText) {
                const count = this.checked ? websiteCheckboxes.length : 0;
                if (count === 0) {
                    websiteDropdownText.textContent = 'Select websites...';
                } else {
                    websiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        });
    }

    // Select All functionality for database search
    const databaseSelectAllCheckbox = document.getElementById('databaseSelectAll') as HTMLInputElement;
    if (databaseSelectAllCheckbox) {
        databaseSelectAllCheckbox.addEventListener('change', function(): void {
            const websiteCheckboxes = document.querySelectorAll('input[name="database-websites"]') as NodeListOf<HTMLInputElement>;
            websiteCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            // Update dropdown text
            if (databaseWebsiteDropdownText) {
                const count = this.checked ? websiteCheckboxes.length : 0;
                if (count === 0) {
                    databaseWebsiteDropdownText.textContent = 'Select websites...';
                } else {
                    databaseWebsiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        });
    }
    // Form submission handler for site search
    const quickActionsForm = document.getElementById('quickActionsForm') as HTMLFormElement;
    if (quickActionsForm) {
        quickActionsForm.addEventListener('submit', async function(e: Event): Promise<void> {
            e.preventDefault();
            const values: SearchValues = getSiteSearchValues();
            
            console.log('Site search values:', values);
            
            // Validation
            if (!values.searchTerms.trim()) {
                alert('Please enter search terms');
                return;
            }

            if (values.websites.length === 0) {
                alert('Please select at least one website');
                return;
            }

            // Show loading state
            const submitButton = quickActionsForm.querySelector('button[type="submit"]') as HTMLButtonElement;
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Searching...';
            submitButton.disabled = true;

            try {
                // Make API request to backend
                const response = await makeApiRequest('/search-site', values);
                displayResults('Site Search', response);
                
                if (response.status === 'success') {
                    alert(`Success! ${response.message}`);
                } else {
                    alert(`Error: ${response.message}`);
                }
            } catch (error) {
                console.error('Search failed:', error);
                alert('Search failed. Please try again.');
            } finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }

    // Form submission handler for database search
    const databaseSearchForm = document.getElementById('databaseSearchForm') as HTMLFormElement;
    if (databaseSearchForm) {
        databaseSearchForm.addEventListener('submit', async function(e: Event): Promise<void> {
            e.preventDefault();
            const values: SearchValues = getDatabaseSearchValues();
            
            console.log('Database search values:', values);
            
            // Validation
            if (!values.searchTerms.trim()) {
                alert('Please enter search terms');
                return;
            }

            if (values.websites.length === 0) {
                alert('Please select at least one website');
                return;
            }

            // Show loading state
            const submitButton = databaseSearchForm.querySelector('button[type="submit"]') as HTMLButtonElement;
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Searching...';
            submitButton.disabled = true;

            try {
                // Make API request to backend
                const response = await makeApiRequest('/search-database', values);
                displayResults('Database Search', response);
                
                if (response.status === 'success') {
                    alert(`Success! ${response.message}`);
                } else {
                    alert(`Error: ${response.message}`);
                }
            } catch (error) {
                console.error('Database search failed:', error);
                alert('Database search failed. Please try again.');
            } finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
});