document.addEventListener('DOMContentLoaded', () => {
    // --- Welcome Overlay Logic ---
    const startBtn = document.getElementById('start-btn');
    const welcomeOverlay = document.getElementById('welcome-overlay');
    // The main container is initially hidden via inline style in the HTML
    const mainContainer = document.querySelector('.container');

    if (startBtn && welcomeOverlay && mainContainer) {
        startBtn.addEventListener('click', () => {
            welcomeOverlay.style.display = 'none';
            mainContainer.style.display = 'block'; // Or 'flex' if it uses flexbox
        });
    }

    // --- Dynamic Login Form Logic ---
    const loginForm = document.getElementById('login-form');
    const requestOtpBtn = document.getElementById('request-otp-btn');
    const otpSection = document.getElementById('otp-section');
    const errorMessage = document.getElementById('error-message');

    if (requestOtpBtn) {
        requestOtpBtn.addEventListener('click', async () => {
            const apiKey = document.getElementById('api-key').value;
            const phoneNumber = document.getElementById('phone-number').value;

            if (!apiKey || !phoneNumber) {
                showError('API Key and phone number are required.');
                return;
            }

            try {
                const response = await fetch('/request-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: apiKey, phone_number: phoneNumber })
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    otpSection.style.display = 'block';
                    requestOtpBtn.style.display = 'none'; // Hide OTP button
                    showError(''); // Clear previous errors
                } else {
                    showError(result.message || 'Failed to send OTP.');
                }
            } catch (error) {
                showError('An error occurred. Please try again.');
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Prevent default form submission

            const otpCode = document.getElementById('otp-code').value;

            if (!otpCode) {
                showError('OTP code is required.');
                return;
            }

            try {
                const response = await fetch('/verify-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ otp_code: otpCode })
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    // On successful login, redirect to the homepage
                    window.location.href = '/';
                } else {
                    showError(result.message || 'Login failed.');
                }
            } catch (error) {
                showError('An error occurred during login. Please try again.');
            }
        });
    }

    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = message ? 'block' : 'none';
        }
    }

    // --- Warning Pop-up Logic ---
    const body = document.body;
    const warningPopup = document.getElementById('warning-popup');
    const confirmBtn = document.getElementById('confirm-btn');

    // Check if the popup should be shown (based on the data attribute from the server)
    if (body.dataset.showWarning === 'true') {
        if (warningPopup) {
            warningPopup.style.display = 'flex';
        }
    }

    // Add event listener to the confirm button to hide the popup
    if (confirmBtn && warningPopup) {
        confirmBtn.addEventListener('click', () => {
            warningPopup.style.display = 'none';
        });
    }
});
