function selectPackage(packageId) {
    const packages = document.querySelectorAll('.package-card');
    packages.forEach(pkg => pkg.classList.remove('selected'));
    
    const selectedPackage = document.querySelector(`.package-card[data-package="${packageId}"]`);
    if (selectedPackage) {
        selectedPackage.classList.add('selected');
    }
    
    document.getElementById('selected-package').value = packageId;
}

async function initializePayment(method) {
    const paymentMethods = document.querySelectorAll('.payment-method-card');
    paymentMethods.forEach(card => card.classList.remove('selected'));
    
    const selectedCard = document.querySelector(`.payment-method-card[data-method="${method}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    document.getElementById('payment-method').value = method;
    
    const packageId = document.getElementById('selected-package').value;
    if (!packageId) {
        showError('Please select a package first.');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/initialize-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                package_id: packageId,
                payment_method: method
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            handlePaymentInitialization(data.payment_data, method);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
    } finally {
        hideLoading();
    }
}

function handlePaymentInitialization(paymentData, method) {
    const paymentDetails = document.getElementById('payment-details');
    paymentDetails.innerHTML = '';
    paymentDetails.classList.remove('d-none');
    
    if (method === 'orange' || method === 'afrimoney') {
        const iframe = document.createElement('iframe');
        iframe.src = paymentData.payment_url;
        iframe.width = '100%';
        iframe.height = '600px';
        iframe.frameBorder = '0';
        paymentDetails.appendChild(iframe);
    } else if (method === 'crypto') {
        const qrCode = document.createElement('img');
        qrCode.src = `https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=${paymentData.address}`;
        qrCode.alt = 'Payment QR Code';
        paymentDetails.appendChild(qrCode);
        
        const addressInfo = document.createElement('p');
        addressInfo.textContent = `Send ${paymentData.amount} ${paymentData.currency} to: ${paymentData.address}`;
        paymentDetails.appendChild(addressInfo);
    }
}

document.getElementById('payment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    showLoading();
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
    } finally {
        hideLoading();
    }
});