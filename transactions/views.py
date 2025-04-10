
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import json
import uuid
from datetime import datetime

from .models import Transactions, PaymentMethod
from .forms import TransactionForm
from .tasks import process_payment_async
from .services import generate_payment_id, decode_payment_id, validate_payment_details
from django.contrib import messages

# Service Provider Views
@login_required
def service_provider_dashboard(request):
    # Get recent transactions for this service provider
    recent_transactions = Transaction.objects.filter(
        service_provider=request.user,
    ).order_by('-created_at')[:10]
    
    # Get payment methods available
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Transaction form for creating new transactions
    form = TransactionForm()
    
    context = {
        'recent_transactions': recent_transactions,
        'payment_methods': payment_methods,
        'form': form,
    }
    
    return render(request, 'transactions/service_provider_dashboard.html', context)
'''
@login_required
def initiate_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        
        if form.is_valid():
            # Create transaction object but don't save to DB yet
            transaction = form.save(commit=False)
            transaction.service_provider = request.user
            transaction.status = 'PENDING'
            
            # Validate transaction details
            validation_result = validate_payment_details(transaction)
            if not validation_result['valid']:
                messages.error(request, f"Invalid transaction details: {validation_result['message']}")
                return redirect('service_provider_dashboard')
            
            # Generate unique payment ID
            payment_id = generate_payment_id(transaction)
            transaction.payment_id = payment_id
            
            # Save transaction to DB
            transaction.save()
            
            messages.success(request, f"Transaction initiated successfully. Payment ID: {payment_id}")
            return redirect('transaction_detail', payment_id=payment_id)
        else:
            messages.error(request, "Invalid form data. Please check and try again.")
    
    return redirect('provider_dashboard')'''

@login_required
def transaction_detail(request, payment_id):
    transaction = get_object_or_404(Transaction, payment_id=payment_id)
    
    # Ensure service provider can only access their own transactions
    if transaction.service_provider != request.user:
        messages.error(request, "You don't have permission to view this transaction.")
        return redirect('service_provider_dashboard')
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'transactions/transaction_detail.html', context)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(
        service_provider=request.user
    ).order_by('-created_at')
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'transactions/transaction_list.html', context)

# Customer Views
def verify_payment(request, payment_id=None):
    if request.method == 'POST' and not payment_id:
        # Customer entered payment ID in form
        payment_id = request.POST.get('payment_id', '').strip()
        return redirect('verify_payment', payment_id=payment_id)
    
    if not payment_id:
        return render(request, 'transactions/enter_payment_id.html')
    
    # Decode payment ID to get transaction details
    transaction_details = decode_payment_id(payment_id)
    
    if not transaction_details:
        messages.error(request, "Invalid payment ID. Please check and try again.")
        return redirect('verify_payment')
    
    # Get transaction from database
    transaction = get_object_or_404(Transaction, payment_id=payment_id)
    
    # Check if transaction is still valid (not expired, cancelled, etc.)
    if transaction.status not in ['PENDING', 'PROCESSING']:
        messages.error(request, f"This transaction is {transaction.status.lower()} and cannot be processed.")
        return redirect('verify_payment')
    
    # Get payment methods
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'transaction': transaction,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'transactions/payment_confirmation.html', context)

@csrf_exempt
def process_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        payment_id = data.get('payment_id')
        payment_method_id = data.get('payment_method_id')
        
        if not payment_id or not payment_method_id:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Get transaction
        transaction = get_object_or_404(Transaction, payment_id=payment_id)
        
        # Check transaction status
        if transaction.status != 'PENDING':
            return JsonResponse({'error': f'Transaction is {transaction.status.lower()}'}, status=400)
        
        # Get payment method
        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
        
        # Update transaction status and payment method
        transaction.status = 'PROCESSING'
        transaction.payment_method = payment_method
        transaction.save()
        
        # Process payment asynchronously with Celery
        process_payment_async.delay(transaction.id, payment_method_id)
        
        return JsonResponse({
            'success': True,
            'message': 'Payment is being processed',
            'redirect_url': reverse('payment_status', kwargs={'payment_id': payment_id})
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def payment_status(request, payment_id):
    transaction = get_object_or_404(Transaction, payment_id=payment_id)
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'transactions/payment_status.html', context)

# API for checking transaction status
@csrf_exempt
def check_transaction_status(request, payment_id):
    transaction = get_object_or_404(Transaction, payment_id=payment_id)
    
    return JsonResponse({
        'status': transaction.status,
        'updated_at': transaction.updated_at.isoformat(),
    })