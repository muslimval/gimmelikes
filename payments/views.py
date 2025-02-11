from django.shortcuts import render

# Create your views here.
# payments/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Payment, PointPackage
from .gateways import OrangeMoneyGateway, AfrimoneyGateway, CryptoGateway
import uuid

@login_required
def buy_points(request):
    packages = PointPackage.objects.all().order_by('price')
    return render(request, 'payments/buy_points.html', {
        'point_packages': packages
    })

@login_required
@require_POST
def initialize_payment(request):
    try:
        package_id = request.POST.get('package_id')
        payment_method = request.POST.get('payment_method')
        
        package = PointPackage.objects.get(id=package_id)
        reference = str(uuid.uuid4())
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=package.price,
            payment_method=payment_method,
            transaction_id=reference,
            points_purchased=package.points
        )
        
        # Initialize payment based on selected method
        if payment_method == 'orange':
            gateway = OrangeMoneyGateway()
        elif payment_method == 'afrimoney':
            gateway = AfrimoneyGateway()
        elif payment_method == 'crypto':
            gateway = CryptoGateway()
        else:
            raise ValueError('Invalid payment method')
        
        # Initialize payment with gateway
        payment_data = gateway.initialize_payment(
            amount=package.price,
            currency='USD',
            reference=reference
        )
        
        return JsonResponse({
            'success': True,
            'payment_data': payment_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def payment_callback(request):
    reference = request.GET.get('reference')
    
    try:
        payment = Payment.objects.get(transaction_id=reference)
        
        # Verify payment based on method
        if payment.payment_method == 'orange':
            gateway = OrangeMoneyGateway()
        elif payment.payment_method == 'afrimoney':
            gateway = AfrimoneyGateway()
        elif payment.payment_method == 'crypto':
            gateway = CryptoGateway()
            
        if gateway.verify_payment(reference):
            # Update payment status
            payment.status = 'completed'
            payment.save()
            
            # Add points to user's account
            profile = request.user.profile
            profile.points += payment.points_purchased
            profile.save()
            
            return redirect('payment_success')
        else:
            payment.status = 'failed'
            payment.save()
            return redirect('payment_failed')
            
    except Payment.DoesNotExist:
        return redirect('payment_failed')