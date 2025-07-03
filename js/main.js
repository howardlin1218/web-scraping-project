"use strict";
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';
// Function to make API requests
async function makeApiRequest(endpoint, data) {
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
    }
    catch (error) {
        return {
            status: 'error',
            message: 'Network error or server unavailable',
            html: 'no body'
        };
    }
}
// Function to display results in the activity log
function displayResults(searchType, response) {
    var _a;
    const activityLog = document.getElementById('activity-log');
    const articlesCard = document.getElementById('articles-card');
    if (!activityLog || !articlesCard)
        return;
    console.log('displayResults called with:', { searchType, responseStatus: response.status, hasHtml: !!response.html });
    // Show the articles card
    articlesCard.style.display = 'block';
    const timestamp = new Date().toLocaleString();
    const resultDiv = document.createElement('div');
    resultDiv.style.marginBottom = '10px';
    resultDiv.style.padding = '10px';
    resultDiv.style.border = '1px solid #ddd';
    resultDiv.style.borderRadius = '4px';
    if (response.status === 'success') {
        resultDiv.style.backgroundColor = '#d4edda';
        if (response.html && response.html !== 'no body') {
            resultDiv.innerHTML = `<div style="border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 10px;"><strong>${timestamp} - ${searchType}:</strong></div>${response.html}`;
            console.log('Adding successful result with HTML content');
        }
        else {
            resultDiv.innerHTML = `<strong>${timestamp} - ${searchType}:</strong><br>No articles found.`;
            console.log('Adding result with no articles found');
        }
    }
    else {
        resultDiv.style.backgroundColor = '#f8d7da';
        resultDiv.innerHTML = `
            <strong>${timestamp} - ${searchType} Error:</strong><br>
            ${response.message}
        `;
        console.log('Adding error result');
    }
    // Check if this is the first result - if so, clear the default "No articles found" message
    const isFirstResult = activityLog.children.length === 1 && ((_a = activityLog.firstElementChild) === null || _a === void 0 ? void 0 : _a.textContent) === 'No articles found.';
    if (isFirstResult) {
        console.log('Clearing default message for first result');
        activityLog.innerHTML = '';
    }
    // Append new result (don't clear existing content)
    console.log('Appending result. Total children before:', activityLog.children.length);
    activityLog.appendChild(resultDiv);
    console.log('Total children after:', activityLog.children.length);
}
// Function to get values from "Search a site" form
function getSiteSearchValues() {
    var _a, _b, _c, _d, _e, _f;
    // Get all checked website checkboxes
    const websiteCheckboxes = document.querySelectorAll('input[name="websites"]:checked');
    const websites = Array.from(websiteCheckboxes).map(checkbox => checkbox.value);
    return {
        websites: websites || ["0"],
        searchTerms: ((_a = document.getElementById('search')) === null || _a === void 0 ? void 0 : _a.value) || "MSI Gaming",
        limit: Number((_b = document.getElementById('amount')) === null || _b === void 0 ? void 0 : _b.value) || 1,
        day: Number((_c = document.getElementById('day')) === null || _c === void 0 ? void 0 : _c.value) || 15,
        month: Number((_d = document.getElementById('month')) === null || _d === void 0 ? void 0 : _d.value) || 6,
        year: Number((_e = document.getElementById('year')) === null || _e === void 0 ? void 0 : _e.value) || 2025,
        keywords: ((_f = document.getElementById('keywords')) === null || _f === void 0 ? void 0 : _f.value) || ""
    };
}
// Function to get values from "Search database" form
function getDatabaseSearchValues() {
    var _a, _b, _c, _d, _e, _f;
    // Get all checked website checkboxes from database form
    const websiteCheckboxes = document.querySelectorAll('input[name="database-websites"]:checked');
    const websites = Array.from(websiteCheckboxes).map(checkbox => checkbox.value);
    return {
        websites: websites,
        searchTerms: ((_a = document.getElementById('database-search')) === null || _a === void 0 ? void 0 : _a.value) || '',
        limit: Number((_b = document.getElementById('database-amount')) === null || _b === void 0 ? void 0 : _b.value) || 5,
        day: Number((_c = document.getElementById('database-day')) === null || _c === void 0 ? void 0 : _c.value) || 15,
        month: Number((_d = document.getElementById('database-month')) === null || _d === void 0 ? void 0 : _d.value) || 6,
        year: Number((_e = document.getElementById('database-year')) === null || _e === void 0 ? void 0 : _e.value) || 2025,
        keywords: ((_f = document.getElementById('database-keywords')) === null || _f === void 0 ? void 0 : _f.value) || ''
    };
}
// DOM Content Loaded event handler
document.addEventListener('DOMContentLoaded', function () {
    // Dropdown functionality for site search
    const websiteDropdownButton = document.getElementById('websiteDropdownButton');
    const websiteDropdownContent = document.getElementById('websiteDropdownContent');
    const websiteDropdownText = document.getElementById('websiteDropdownText');
    const websiteDropdownArrow = websiteDropdownButton === null || websiteDropdownButton === void 0 ? void 0 : websiteDropdownButton.querySelector('.dropdown-arrow');
    if (websiteDropdownButton && websiteDropdownContent) {
        websiteDropdownButton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            websiteDropdownContent.classList.toggle('show');
            websiteDropdownArrow === null || websiteDropdownArrow === void 0 ? void 0 : websiteDropdownArrow.classList.toggle('open');
        });
        // Update dropdown text when selections change
        const updateWebsiteDropdownText = () => {
            var _a, _b;
            const checkedBoxes = websiteDropdownContent.querySelectorAll('input[name="websites"]:checked');
            const count = checkedBoxes.length;
            if (websiteDropdownText) {
                if (count === 0) {
                    websiteDropdownText.textContent = 'Select websites...';
                }
                else if (count === 1) {
                    const label = ((_b = (_a = checkedBoxes[0].parentElement) === null || _a === void 0 ? void 0 : _a.querySelector('label')) === null || _b === void 0 ? void 0 : _b.textContent) || '';
                    websiteDropdownText.textContent = label;
                }
                else {
                    websiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        };
        // Add change listeners to checkboxes
        websiteDropdownContent.querySelectorAll('input[name="websites"]').forEach(checkbox => {
            checkbox.addEventListener('change', updateWebsiteDropdownText);
        });
        // Prevent dropdown from closing when clicking inside
        websiteDropdownContent.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }
    // Dropdown functionality for database search
    const databaseWebsiteDropdownButton = document.getElementById('databaseWebsiteDropdownButton');
    const databaseWebsiteDropdownContent = document.getElementById('databaseWebsiteDropdownContent');
    const databaseWebsiteDropdownText = document.getElementById('databaseWebsiteDropdownText');
    const databaseWebsiteDropdownArrow = databaseWebsiteDropdownButton === null || databaseWebsiteDropdownButton === void 0 ? void 0 : databaseWebsiteDropdownButton.querySelector('.dropdown-arrow');
    if (databaseWebsiteDropdownButton && databaseWebsiteDropdownContent) {
        databaseWebsiteDropdownButton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            databaseWebsiteDropdownContent.classList.toggle('show');
            databaseWebsiteDropdownArrow === null || databaseWebsiteDropdownArrow === void 0 ? void 0 : databaseWebsiteDropdownArrow.classList.toggle('open');
        });
        // Update dropdown text when selections change
        const updateDatabaseWebsiteDropdownText = () => {
            var _a, _b;
            const checkedBoxes = databaseWebsiteDropdownContent.querySelectorAll('input[name="database-websites"]:checked');
            const count = checkedBoxes.length;
            if (databaseWebsiteDropdownText) {
                if (count === 0) {
                    databaseWebsiteDropdownText.textContent = 'Select websites...';
                }
                else if (count === 1) {
                    const label = ((_b = (_a = checkedBoxes[0].parentElement) === null || _a === void 0 ? void 0 : _a.querySelector('label')) === null || _b === void 0 ? void 0 : _b.textContent) || '';
                    databaseWebsiteDropdownText.textContent = label;
                }
                else {
                    databaseWebsiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        };
        // Add change listeners to checkboxes
        databaseWebsiteDropdownContent.querySelectorAll('input[name="database-websites"]').forEach(checkbox => {
            checkbox.addEventListener('change', updateDatabaseWebsiteDropdownText);
        });
        // Prevent dropdown from closing when clicking inside
        databaseWebsiteDropdownContent.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }
    // Close dropdowns when clicking outside
    document.addEventListener('click', function (event) {
        if (websiteDropdownButton && websiteDropdownContent && !websiteDropdownButton.contains(event.target)) {
            websiteDropdownContent.classList.remove('show');
            websiteDropdownArrow === null || websiteDropdownArrow === void 0 ? void 0 : websiteDropdownArrow.classList.remove('open');
        }
        if (databaseWebsiteDropdownButton && databaseWebsiteDropdownContent && !databaseWebsiteDropdownButton.contains(event.target)) {
            databaseWebsiteDropdownContent.classList.remove('show');
            databaseWebsiteDropdownArrow === null || databaseWebsiteDropdownArrow === void 0 ? void 0 : databaseWebsiteDropdownArrow.classList.remove('open');
        }
    });
    // Select All functionality for site search
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const websiteCheckboxes = document.querySelectorAll('input[name="websites"]');
            websiteCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            // Update dropdown text
            if (websiteDropdownText) {
                const count = this.checked ? websiteCheckboxes.length : 0;
                if (count === 0) {
                    websiteDropdownText.textContent = 'Select websites...';
                }
                else {
                    websiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        });
    }
    // Select All functionality for database search
    const databaseSelectAllCheckbox = document.getElementById('databaseSelectAll');
    if (databaseSelectAllCheckbox) {
        databaseSelectAllCheckbox.addEventListener('change', function () {
            const websiteCheckboxes = document.querySelectorAll('input[name="database-websites"]');
            websiteCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            // Update dropdown text
            if (databaseWebsiteDropdownText) {
                const count = this.checked ? websiteCheckboxes.length : 0;
                if (count === 0) {
                    databaseWebsiteDropdownText.textContent = 'Select websites...';
                }
                else {
                    databaseWebsiteDropdownText.textContent = `${count} websites selected`;
                }
            }
        });
    }
    // Clear Articles button functionality
    const clearArticlesBtn = document.getElementById('clearArticlesBtn');
    if (clearArticlesBtn) {
        clearArticlesBtn.addEventListener('click', function () {
            const activityLog = document.getElementById('activity-log');
            const articlesCard = document.getElementById('articles-card');
            if (activityLog && articlesCard) {
                activityLog.innerHTML = '<p>No articles found.</p>';
                articlesCard.style.display = 'none';
            }
        });
    }
    // Form submission handler for site search
    const quickActionsForm = document.getElementById('quickActionsForm');
    if (quickActionsForm) {
        quickActionsForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const values = getSiteSearchValues();
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
            const submitButton = quickActionsForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Searching...';
            submitButton.disabled = true;
            try {
                // Make API request to backend
                console.log('Making API request with values:', values);
                const response = await makeApiRequest('/search-site', values);
                console.log('Received response:', response);
                displayResults('Site Search', response);
                if (response.status === 'success') {
                    alert(`Success! ${response.message}`);
                }
                else {
                    alert(`Error: ${response.message}`);
                }
            }
            catch (error) {
                console.error('Search failed:', error);
                alert('Search failed. Please try again.');
            }
            finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
    // Form submission handler for database search
    const databaseSearchForm = document.getElementById('databaseSearchForm');
    if (databaseSearchForm) {
        databaseSearchForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const values = getDatabaseSearchValues();
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
            const submitButton = databaseSearchForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Searching...';
            submitButton.disabled = true;
            try {
                // Make API request to backend
                console.log('Making database API request with values:', values);
                const response = await makeApiRequest('/search-database', values);
                console.log('Received database response:', response);
                displayResults('Database Search', response);
                if (response.status === 'success') {
                    console.log("response success");
                    alert(`Success! ${response.message}`);
                }
                else {
                    alert(`Error: ${response.message}`);
                }
            }
            catch (error) {
                console.error('Database search failed:', error);
                alert('Database search failed. Please try again.');
            }
            finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
});
