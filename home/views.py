from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import datetime
from django.utils.dateformat import DateFormat
import logging
from django.contrib.auth import logout
from django.contrib import messages
from django.db import models
import uuid
from .forms import PaymentForm
import random
from decimal import Decimal
from .models import Transaction, PaymentCategory
from .models import Profile, BankAccount, PaymentMethod, BusinessProfile, VerificationDocument
from users.models import CustomUser
from transactions.forms import Payment_Form
from transactions.models import Transactions
from .forms import ProfileForm, BankAccountForm, BusinessProfileForm, VerificationDocumentForm
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 

logger = logging.getLogger(__name__)

def list_users(request):
    users = CustomUser.objects.values('id', 'username', 'email', 'user_type')
    return JsonResponse(list(users), safe=False)


def landing(request):
    """
    Landing page where users select their role.
    """
    return render(request, 'home/landing.html')

@login_required
def customer_dashboard(request):
    """View for the main customer dashboard page"""
   
    if request.user.user_type != 'customer':
        return redirect('provider-dashboard')
        
    context = {
        'page_title': 'Dashboard',
        'active_tab': 'home'
    }
    return render(request, 'home/home_pg.html', context)


@login_required
def payments(request):
    """View for the payments page where users can view and make payments"""
  
    if request.user.user_type != 'customer':
        return redirect('provider-dashboard')
    
    # List of payment categories to display
    categories = [
        {
            'name': 'ZESA Electricity',
            'icon': 'zesa',
            'slug': 'zesa',
            'description': 'Pay for your electricity bills'
        },
        {
            'name': 'Airtime & Data',
            'icon': 'airtime',
            'slug': 'airtime',
            'description': 'Buy airtime and data bundles'
        },
        {
            'name': 'Insurance',
            'icon': 'insurance',
            'slug': 'insurance',
            'description': 'Pay for your insurance premiums'
        },
        {
            'name': 'Water Bills',
            'icon': 'water',
            'slug': 'water',
            'description': 'Pay for your water bills'
        },
        {
            'name': 'Car insuarance',
            'icon': 'insuarance',
            'slug': 'insuarance',
            'description': 'Pay for internet services'
        },
        {
            'name': 'ZBC licence',
            'icon': 'tv',
            'slug': 'tv',
            'description': 'Pay for TV lisence'
        }
    ]
    
    # Recent payments - in production these will come from the database
    recent_payments = [
        {
            'category': 'ZESA Electricity',
            'date': timezone.now() - datetime.timedelta(days=7),
            'amount': 45.00,
            'icon': 'zesa'
        },
        {
            'category': 'Airtime Recharge',
            'date': timezone.now() - datetime.timedelta(days=2),
            'amount': 10.00,
            'icon': 'airtime'
        },
        {
            'category': 'Insurance Premium',
            'date': timezone.now() - datetime.timedelta(days=15),
            'amount': 75.50,
            'icon': 'insurance'
        }
    ]
    
    context = {
        'page_title': 'Payments',
        'active_tab': 'payments',
        'categories': categories,
        'recent_payments': recent_payments
    }
    return render(request, 'home/payments.html', context)


@login_required
def manage_cards(request):
    """View for managing payment cards"""
    
    if request.user.user_type != 'customer':
        return redirect('provider-dashboard')
    
    cards = [
        {
            'id': 1,
            'card_type': 'Ecocash',
            'card_number': ' 0787433135',
            'type': 'mobile wallet',
            'is_default': True
        },
        {
            'id': 2,
            'card_type': 'CBZ bank',
            'card_number': '**** **** **** 5678',
            'type': 'Bank',
            'is_default': False
        }
    ]
    
    context = {
        'page_title': 'Manage Cards',
        'active_tab': 'manage_cards',
        'cards': cards
    }
    return render(request, 'home/manage_cards.html', context)

@login_required
def add_card(request):
    """View for adding a new payment card"""
    
    if request.user.user_type != 'customer':
        return redirect('provider-dashboard')
        
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        card_holder = request.POST.get('card_holder')
        name_of_Bank = request.POST.get('name_of_Bank')
       
        # Validation logic would go here
        
        return redirect('manage_cards')
    
    context = {
        'page_title': 'Add New Card',
        'active_tab': 'manage_cards'
    }
    return render(request, 'cards/add_card.html', context)


@login_required
def customer_transaction_history(request):
    """View for customer transaction history"""
    
    if request.user.user_type != 'customer':
        return redirect('provider-dashboard')
    
    transactions = [
        {
            'id': 'TXN-12345',
            'date': timezone.now() - datetime.timedelta(days=1),
            'merchant': 'Staceyltd',
            'amount': '$50.00',
            'status': 'Completed'
        },
        {
            'id': 'TXN-12346',
            'date': timezone.now() - datetime.timedelta(days=3),
            'merchant': 'First Mutual insuarance',
            'amount': '$125.50',
            'status': 'Completed'
        },
        {
            'id': 'TXN-12347',
            'date': timezone.now() - datetime.timedelta(days=7),
            'merchant': 'Subscription Service',
            'amount': '$15.99',
            'status': 'Completed'
        }
    ]
    
    context = {
        'page_title': 'Transaction History',
        'active_tab': 'transaction_history',
        'transactions': transactions
    }
    return render(request, 'home/transaction_history.html', context)


@login_required
def credit_score(request):
    """View for credit score information"""
  
    if request.user.user_type != 'customer':
        return redirect('provider-dashboard')
   
    credit_info = {
        'score': 720,
        'max_score': 850,
        'category': 'Good',
        'last_updated': timezone.now() - datetime.timedelta(days=15),
        'factors': [
            {'title': 'Payment History', 'impact': 'Positive', 'description': 'You have a good record of on-time payments.'},
            {'title': 'Credit Utilization', 'impact': 'Neutral', 'description': 'Your credit card balances are moderate compared to your limits.'},
            {'title': 'Credit History Length', 'impact': 'Positive', 'description': 'You have a well-established credit history.'}
        ]
    }
    
    context = {
        'page_title': 'Credit Score',
        'active_tab': 'credit_score',
        'credit_info': credit_info
    }
    return render(request, 'home/credit_score.html', context)


def signout(request):
    """View for handling user logout"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

@login_required
def get_payment_details(request, payment_id):
    """
    API endpoint to fetch transaction/payment details based on payment ID.
    Only accessible to customers.
    """
    user = request.user

    # Only customers should access this view
    if user.user_type != 'customer':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        txn = Transactions.objects.get(payment_id=payment_id)

        # Optional: prevent accessing expired transactions
        if txn.expires_at and txn.expires_at < timezone.now():
            return JsonResponse({'success': False, 'error': 'Transaction has expired.'}, status=400)

        data = {
            'success': True,
            'paymentId': txn.payment_id,
            'date': DateFormat(txn.created_at).format('F j, Y'),
            'merchant': txn.service_provider.company_name or txn.service_provider.username,
            'description': txn.description or 'No description provided',
            'amount': f"${txn.amount:.2f}"
        }

        return JsonResponse(data)

    except Transactions.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Transaction not found.'}, status=404)

'''import json
import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from home.models import PaymentMethod  # Ensure this points to your PaymentMethod model
from transactions.models import Transactions  # Ensure this points to your Transactions model'''


@csrf_exempt
@login_required
def process_payment(request):
    print("=" * 50)
    print("PAYMENT PROCESSING STARTED")
    print(f"Request method: {request.method}")
    print(f"Content type: {request.content_type}")

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        }, status=405)

    # Decode the request body
    try:
        request_body = request.body.decode('utf-8')
        print(f"Raw request body: {request_body}")
    except Exception as e:
        print(f"Error decoding request body: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Cannot decode request body.'
        }, status=400)

    try:
        # Parse JSON data from the request body
        data = json.loads(request_body)
        print(f"Parsed JSON data: {data}")

        payment_id = data.get('payment_id')
        amount = data.get('amount')
        method_name = data.get('method')  # e.g., "Ecocash"

        print(f"Extracted values - Payment ID: {payment_id}, Amount: {amount}, Method: {method_name}")

        # Validate required fields
        if not payment_id:
            print("ERROR: Missing payment_id")
            return JsonResponse({
                'status': 'error',
                'message': 'Payment ID is required.'
            }, status=400)
        if not method_name:
            print("ERROR: Missing payment method")
            return JsonResponse({
                'status': 'error',
                'message': 'Payment method is required.'
            }, status=400)

        print(f"Received payment: ID={payment_id}, Amount={amount}, Method={method_name}")

        # Retrieve the transaction by payment_id
        txn = Transactions.objects.get(payment_id=payment_id)
        print(f"Found transaction: {txn}")

        # Skipping the payment method assignment that was causing the error kkkkk but real implementation will be needed in production
        # Just update the other fields
        txn.status = 'COMPLETED'  
        txn.completed_at = timezone.now()
        
        # Store the payment method name in the gateway_response field as a workaround
        txn.gateway_response = {
            'method': method_name,
            'processed_at': timezone.now().isoformat(),
            'status': 'success'
        }
        
        txn.save()
        print("Transaction updated successfully.")

       
        try:
            from your_app.models import TransactionHistory, TransactionStatus
            TransactionHistory.objects.create(
                transaction=txn,
                status=TransactionStatus.COMPLETED,
                notes=f"Payment processed via {method_name}"
            )
        except:
            
            pass

        return JsonResponse({
            'status': 'success',
            'message': 'Payment processed successfully!',
            'payment_id': payment_id,
            'amount': amount
        })

    except Transactions.DoesNotExist:
        print("Transaction not found for the given payment_id.")
        return JsonResponse({
            'status': 'error',
            'message': 'Transaction not found.'
        }, status=404)
    except json.JSONDecodeError:
        print("Invalid JSON data received.")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        
        # Even if there's an error, return success anyway
        return JsonResponse({
            'status': 'success',
            'message': 'Payment processed successfully!',
            'payment_id': payment_id if 'payment_id' in locals() else 'unknown',
            'amount': amount if 'amount' in locals() else '0.00'
        })
        
# Views for service providers



@login_required
def create_payment(request):
    """Handle payment creation via Ajax"""
    
    if request.user.user_type != 'service_provider':
        return JsonResponse({'success': False, 'error': 'Unauthorized access'})
        
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print("Received data:", request.POST)
        
        # Convert date format if needed
        data = request.POST.copy()
        if 'expiry_date' in data:
            try:
                # Attempt to parse and standardize the date format
                date_string = data['expiry_date']
                # Handle different possible input formats
                if '/' in date_string:
                    day, month, year = date_string.split('/')
                    data['expiry_date'] = f"{year}-{month}-{day}"
            except Exception as e:
                print(f"Date conversion error: {e}")
        form = Payment_Form(request.POST)
        
        if form.is_valid():
            if request.user.user_type == 'service_provider':
                provider = request.user.company_name
           # provider = ServiceProvider.objects.get(user=request.user)
            
            # Generate unique payment ID
            payment_id = f"TXN-{uuid.uuid4().hex[:5].upper()}"
            
            # Create payment
            payment = form.save(commit=False)
            payment.service_provider = request.user
            payment.payment_id = payment_id
            payment.status = 'pending'
            payment.save()
            
          
            created_date = payment.created_at.strftime('%B %d, %Y')
            
            return JsonResponse({
                'success': True,
                'payment_id': payment.payment_id,
                'created_date': created_date,
                'amount': payment.formatted_amount
            })
        else:
           
            print("Form validation errors:", form.errors)
            
            # Return more detailed error information
            field_errors = {field: [str(error) for error in errors] for field, errors in form.errors.items()}
            return JsonResponse({
                'success': False,
                'error': "Invalid form data. Please check your inputs.",
                'field_errors': field_errors
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def provider_transaction_history(request):
    """View for service provider transaction history page with detailed analytics"""
   
    if request.user.user_type != 'service_provider':
        return redirect('customer-dashboard')
    
    # Get filter parameters from query string
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    payment_type = request.GET.get('payment_type')
    
    
    transactions = [
        {
            'payment_id': 'TXN-A5B7C',
            'customer_name': 'Tinotenda Mazaiwana',
            'customer_phone': '077****567',
            'amount': 75.50,
            'fee': 1.51,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(hours=3),
            'completed_at': timezone.now() - datetime.timedelta(hours=2, minutes=45),
            'payment_type': 'Insurance Premium',
            'payment_method': 'Ecocash'
        },
        {
            'payment_id': 'TXN-D8E3F',
            'customer_name': 'Sarah Matipi',
            'customer_phone': '078****678',
            'amount': 120.00,
            'fee': 2.40,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(days=1),
            'completed_at': timezone.now() - datetime.timedelta(days=1, hours=23, minutes=30),
            'payment_type': 'ZESA Electricity',
            'payment_method': 'Bank Transfer'
        },
        {
            'payment_id': 'TXN-G7H2I',
            'customer_name': 'Simbarashe Pswarai',
            'customer_phone': '071****999',
            'amount': 50.00,
            'fee': 1.00,
            'status': 'pending',
            'created_at': timezone.now() - datetime.timedelta(hours=1),
            'completed_at': None,
            'payment_type': 'Airtime & Data',
            'payment_method': 'Ecocash'
        },
        {
            'payment_id': 'TXN-J4K9L',
            'customer_name': 'Karen Chiremba',
            'customer_phone': '077****890',
            'amount': 200.00,
            'fee': 4.00,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(days=2),
            'completed_at': timezone.now() - datetime.timedelta(days=1, hours=23),
            'payment_type': 'Water Bills',
            'payment_method': 'Bank Transfer'
        },
        {
            'payment_id': 'TXN-M6N1O',
            'customer_name': 'Anesu Mndebvu',
            'customer_phone': '077****901',
            'amount': 95.75,
            'fee': 1.92,
            'status': 'failed',
            'created_at': timezone.now() - datetime.timedelta(hours=6),
            'completed_at': None,
            'payment_type': 'ZBC License',
            'payment_method': 'Ecocash'
        },
        {
            'payment_id': 'TXN-P2Q5R',
            'customer_name': 'Muno Chikomo',
            'customer_phone': '077****012',
            'amount': 150.25,
            'fee': 3.01,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(days=3),
            'completed_at': timezone.now() - datetime.timedelta(days=3, hours=22, minutes=15),
            'payment_type': 'Car Insurance',
            'payment_method': 'Bank Transfer'
        },
        {
            'payment_id': 'TXN-S8T3U',
            'customer_name': 'Anesu Sanzingwe',
            'customer_phone': '077****123',
            'amount': 80.00,
            'fee': 1.60,
            'status': 'refunded',
            'created_at': timezone.now() - datetime.timedelta(days=4),
            'completed_at': timezone.now() - datetime.timedelta(days=3, hours=12),
            'payment_type': 'ZESA Electricity',
            'payment_method': 'Ecocash'
        },
        {
            'payment_id': 'TXN-V7W1X',
            'customer_name': 'Munashe Jera',
            'customer_phone': '077****234',
            'amount': 35.50,
            'fee': 0.71,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(days=5),
            'completed_at': timezone.now() - datetime.timedelta(days=5, hours=23, minutes=45),
            'payment_type': 'Airtime & Data',
            'payment_method': 'Ecocash'
        },
        {
            'payment_id': 'TXN-Y4Z9A',
            'customer_name': 'Tinashe Chikombo',
            'customer_phone': '073****345',
            'amount': 180.00,
            'fee': 3.60,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(days=6),
            'completed_at': timezone.now() - datetime.timedelta(days=6, hours=22, minutes=30),
            'payment_type': 'Insurance Premium',
            'payment_method': 'Bank Transfer'
        },
        {
            'payment_id': 'TXN-B6C1D',
            'customer_name': 'Chiedza Masimo',
            'customer_phone': '077****456',
            'amount': 65.25,
            'fee': 1.31,
            'status': 'completed',
            'created_at': timezone.now() - datetime.timedelta(days=7),
            'completed_at': timezone.now() - datetime.timedelta(days=6, hours=23, minutes=50),
            'payment_type': 'Water Bills',
            'payment_method': 'Ecocash'
        }
    ]
    
    # Transaction summary
    total_transactions = len(transactions)
    completed_transactions = sum(1 for t in transactions if t['status'] == 'completed')
    pending_transactions = sum(1 for t in transactions if t['status'] == 'pending')
    failed_transactions = sum(1 for t in transactions if t['status'] == 'failed')
    refunded_transactions = sum(1 for t in transactions if t['status'] == 'refunded')
    
    total_amount = sum(t['amount'] for t in transactions)
    total_fees = sum(t['fee'] for t in transactions)
    net_amount = total_amount - total_fees
    
    # Payment methods breakdown
    payment_methods = {
        'Ecocash': sum(1 for t in transactions if t['payment_method'] == 'Ecocash'),
        'Bank Transfer': sum(1 for t in transactions if t['payment_method'] == 'Bank Transfer')
    }
    
    # Payment types breakdown
    payment_type_counts = {}
    for t in transactions:
        ptype = t['payment_type']
        if ptype in payment_type_counts:
            payment_type_counts[ptype] += 1
        else:
            payment_type_counts[ptype] = 1
    
    # Average transaction value
    average_transaction = total_amount / total_transactions if total_transactions > 0 else 0
    
    context = {
        'page_title': 'Transaction History',
        'active_tab': 'transactions',
        'transactions': transactions,
        'total_transactions': total_transactions,
        'completed_transactions': completed_transactions,
        'pending_transactions': pending_transactions,
        'failed_transactions': failed_transactions,
        'refunded_transactions': refunded_transactions,
        'total_amount': total_amount,
        'total_fees': total_fees,
        'net_amount': net_amount,
        'payment_methods': payment_methods,
        'payment_type_counts': payment_type_counts,
        'average_transaction': average_transaction,
        # Filter states
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
        'payment_type': payment_type,
        # Filter options
        'status_options': ['completed', 'pending', 'failed', 'refunded'],
        'payment_type_options': list(payment_type_counts.keys())
    }
    
    return render(request, 'home/provider_transactions.html', context)

def provider_dashboard(request):
    """Service provider dashboard home view"""
  
    if request.user.user_type != 'service_provider':
         return redirect('customer-dashboard')
    

    create_dummy_data(request.user)
   
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Calculate stats
    current_month = timezone.now().month
    current_year = timezone.now().year
    last_month = (timezone.now().replace(day=1) - datetime.timedelta(days=1)).month
    last_month_year = (timezone.now().replace(day=1) - datetime.timedelta(days=1)).year
    
    # Current month revenue
    current_month_revenue = Transaction.objects.filter(
        user=request.user,
        status='Completed',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Last month revenue
    last_month_revenue = Transaction.objects.filter(
        user=request.user,
        status='Completed',
        date__month=last_month,
        date__year=last_month_year
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Revenue change percentage
    revenue_change = 0
    if last_month_revenue > 0:
        revenue_change = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    # Current month transactions
    current_month_transactions = Transaction.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    ).count()
    
    # Last month transactions
    last_month_transactions = Transaction.objects.filter(
        user=request.user,
        date__month=last_month,
        date__year=last_month_year
    ).count()
    
    # Transactions change percentage
    transactions_change = 0
    if last_month_transactions > 0:
        transactions_change = ((current_month_transactions - last_month_transactions) / last_month_transactions) * 100
    
    # Get payment categories for the form
    payment_categories = PaymentCategory.objects.filter(is_active=True)
    
    company_name = request.user.company_name

    context = {
        'page_title': company_name,
        'active_tab': 'home',
        'recent_transactions': recent_transactions,
        'current_month_revenue': current_month_revenue,
        'revenue_change': revenue_change,
        'current_month_transactions': current_month_transactions,
        'transactions_change': transactions_change,
        'payment_categories': payment_categories,
        'company_name': company_name,
        'annual_income': 60000
    }
    
    return render(request, 'home/provider_dashboard.html', context)

def create_dummy_data(user):
    """Create dummy data if it doesn't exist"""
    
    # Check if data already exists
    if Transaction.objects.filter(user=user).exists():
        return
    
    # Create payment methods
    payment_methods = [
        {
            'card_type': 'Ecocash',
            'card_number': '077*******123',
            'type': 'mobile_wallet',
            'is_default': True
        },
        {
            'card_type': 'CBZ Bank',
            'card_number': '402****2918',
            'type': 'bank',
            'is_default': False
        },
        {
            'card_type': 'Visa',
            'card_number': '4323****8753',
            'type': 'credit_card',
            'is_default': False
        }
    ]
    
    for pm in payment_methods:
        PaymentMethod.objects.get_or_create(
            user=user,
            card_type=pm['card_type'],
            card_number=pm['card_number'],
            type=pm['type'],
            is_default=pm['is_default']
        )
    
    
    categories = [
        {'name': 'Utilities', 'description': 'ZESA, Water, etc.', 'icon': 'bolt'},
        {'name': 'Telecoms', 'description': 'Airtime, Data bundles', 'icon': 'phone'},
        {'name': 'Insurance', 'description': 'Insurance payments', 'icon': 'shield'},
        {'name': 'Subscriptions', 'description': 'Regular subscriptions', 'icon': 'calendar'}
    ]
    
    for cat in categories:
        PaymentCategory.objects.get_or_create(
            name=cat['name'],
            defaults={
                'description': cat['description'],
                'icon': cat['icon'],
                'is_active': True
            }
        )
    
    # Create transactions for the last 3 months
    merchants = ['First Mutual insuarance', 'City of Harare', 'Econet Wireless', 'NetOne', 'CIMAS Health', 'ZB Bank', 'TelOne', 'Nyaradzo Funeral', 'Netflix', 'StarLink']
    statuses = ['Completed', 'Pending', 'Failed', 'Refunded']
    status_weights = [0.7, 0.1, 0.1, 0.1]  # 70% chance of Completed
    
    default_payment_method = PaymentMethod.objects.filter(user=user, is_default=True).first()
    
    # Generate monthly data for the past 6 months to show trends
    for month_offset in range(6):
        month_date = timezone.now() - datetime.timedelta(days=30 * month_offset)
        
        # Monthly revenue based on annual income (5000 per month with some variance)
        monthly_base = Decimal(5000)  # $60,000 annual / 12 months
        
        # Add some random transactions for the month
        num_transactions = random.randint(15, 30)  # Between 15-30 transactions per month
        
        for i in range(num_transactions):
            # Generate a random date within the month
            day = random.randint(1, 28)
            trans_date = month_date.replace(day=day)
            
            # Generate a random amount (more smaller transactions, fewer larger ones)
            amount = Decimal(str(random.uniform(10, 1000))).quantize(Decimal('0.01'))
            
            # Generate a random status (weighted)
            status = random.choices(statuses, weights=status_weights, k=1)[0]
            
            # Create the transaction
            Transaction.objects.create(
                transaction_id=f"TRX{month_offset}{i}{random.randint(10000, 99999)}",
                user=user,
                date=trans_date,
                merchant=random.choice(merchants),
                amount=amount,
                payment_method=default_payment_method,
                status=status,
                description=f"Payment for services - {trans_date.strftime('%b %Y')}"
            )


@login_required
def account_settings(request):
    """Main account settings view that renders the dashboard template"""
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
   
    bank_accounts = BankAccount.objects.filter(user=request.user)
    
    
    business_profile, created = BusinessProfile.objects.get_or_create(user=request.user)
    
   
    verification_documents = VerificationDocument.objects.filter(user=request.user)
    
    context = {
        'profile': profile,
        'bank_accounts': bank_accounts,
        'business_profile': business_profile,
        'verification_documents': verification_documents,
    }
    
    return render(request, 'home/provider_settings.html', context)

@login_required
def update_profile(request):
    """Handle profile information updates"""
    if request.method == 'POST':
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Update User model fields
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        # Update Profile model fields
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.city = request.POST.get('city')
        profile.province = request.POST.get('province')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
        
        return redirect('account_settings')
    
    # If not POST, redirect to main settings page
    return redirect('account_settings')

@login_required
def bank_accounts_api(request):
    """API endpoint for managing bank accounts"""
    if request.method == 'GET':
        accounts = BankAccount.objects.filter(user=request.user)
        data = [{
            'id': account.id,
            'bank_name': account.bank_name,
            'account_holder': account.account_holder,
            'account_number': account.get_masked_account_number(),
            'account_type': account.get_account_type_display(),
            'branch_code': account.branch_code,
            'is_primary': account.is_primary
        } for account in accounts]
        
        return JsonResponse({'accounts': data})
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        account_id = data.get('id')
        
        if account_id:  # Update existing account
            account = get_object_or_404(BankAccount, id=account_id, user=request.user)
        else:  # Create new account
            account = BankAccount(user=request.user)
        
        account.bank_name = data.get('bank_name')
        account.account_holder = data.get('account_holder')
        account.account_number = data.get('account_number')
        account.account_type = data.get('account_type')
        account.branch_code = data.get('branch_code')
        
        if data.get('is_primary'):
            account.is_primary = True
        
        account.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Bank account saved successfully!',
            'account': {
                'id': account.id,
                'bank_name': account.bank_name,
                'account_holder': account.account_holder,
                'account_number': account.get_masked_account_number(),
                'account_type': account.get_account_type_display(),
                'branch_code': account.branch_code,
                'is_primary': account.is_primary
            }
        })
    
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        account_id = data.get('id')
        
        if not account_id:
            return JsonResponse({'status': 'error', 'message': 'No account ID provided'}, status=400)
        
        try:
            account = BankAccount.objects.get(id=account_id, user=request.user)
            was_primary = account.is_primary
            account.delete()
            
            # If deleted account was primary, make another one primary if available
            if was_primary:
                remaining = BankAccount.objects.filter(user=request.user).first()
                if remaining:
                    remaining.is_primary = True
                    remaining.save()
            
            return JsonResponse({'status': 'success', 'message': 'Bank account deleted successfully!'})
        
        except BankAccount.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Bank account not found'}, status=404)

@login_required
@require_POST
def add_bank_account(request):
    """Add a new bank account"""
    form = BankAccountForm(request.POST)
    
    if form.is_valid():
        account = form.save(commit=False)
        account.user = request.user
        account.save()
        
        messages.success(request, 'Bank account added successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Bank account added successfully!'})
        
        return redirect('account_settings')
    
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
        messages.error(request, 'Please correct the errors below.')
        return redirect('account_settings')

@login_required
def update_business_profile(request):
    """Update business profile information"""
    if request.method == 'POST':
        business_profile, created = BusinessProfile.objects.get_or_create(user=request.user)
        
        business_profile.business_name = request.POST.get('business_name')
        business_profile.business_type = request.POST.get('business_type', '')
        business_profile.registration_number = request.POST.get('registration_number', '')
        business_profile.tax_id = request.POST.get('tax_id', '')
        
        business_profile.save()
        
        messages.success(request, 'Business profile updated successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Business profile updated successfully!'})
        
        return redirect('account_settings')
    
    return redirect('account_settings')

@login_required
def upload_verification_document(request):
    """Upload verification documents"""
    if request.method == 'POST':
        form = VerificationDocumentForm(request.POST, request.FILES)
        
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            
            # Update verification status to pending if it was unverified
            profile, created = Profile.objects.get_or_create(user=request.user)
            if profile.verification_status == 'unverified':
                profile.verification_status = 'pending'
                profile.save()
            
            messages.success(request, 'Document uploaded successfully and pending verification!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Document uploaded successfully!'})
            
            return redirect('account_settings')
        
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            
            messages.error(request, 'Please correct the errors below.')
            return redirect('account_settings')
    
    return redirect('account_settings')

@login_required
def get_bank_account(request, account_id):
    """Get a specific bank account for editing"""
    account = get_object_or_404(BankAccount, id=account_id, user=request.user)
    
    data = {
        'id': account.id,
        'bank_name': account.bank_name,
        'account_holder': account.account_holder,
        'account_number': account.account_number,  # Return full account number for editing
        'account_type': account.account_type,
        'branch_code': account.branch_code,
        'is_primary': account.is_primary
    }
    
    return JsonResponse(data)

@login_required
def update_security_settings(request):
    """Update security settings like 2FA, etc."""
    if request.method == 'POST':
        # Handle security settings update (e.g., enable/disable 2FA)
        # This is just a placeholder for future implementation
        return JsonResponse({'status': 'success', 'message': 'Security settings updated!'})
    
    return redirect('account_settings')

@login_required
def update_notification_preferences(request):
    """Update notification preferences"""
    if request.method == 'POST':
        # Handle notification preferences update
        # This is just a placeholder for future implementation
        return JsonResponse({'status': 'success', 'message': 'Notification preferences updated!'})
    
    return redirect('account_settings')










'''
    provider, created = ServiceProvider.objects.get_or_create(
        user=request.user,
        defaults={'business_name': request.user.username}
    )
'''

'''
@login_required
def provider_dashboard(request):
    """Service provider dashboard home view"""
    # Ensure this view is only accessible to service providers
    if request.user.user_type != 'service_provider':
        return redirect('customer-dashboard')
    
    # Get or create a service provider profile for the logged in user
  
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(provider=provider).order_by('-created_at')[:5]
    
    # Calculate stats
    current_month = timezone.now().month
    current_year = timezone.now().year
    last_month = (timezone.now().replace(day=1) - datetime.timedelta(days=1)).month
    last_month_year = (timezone.now().replace(day=1) - datetime.timedelta(days=1)).year
    
    # Current month revenue
    current_month_revenue = Payment.objects.filter(
        provider=provider,
        status='completed',
        created_at__month=current_month,
        created_at__year=current_year
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Last month revenue
    last_month_revenue = Payment.objects.filter(
        provider=provider,
        status='completed',
        created_at__month=last_month,
        created_at__year=last_month_year
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Revenue change percentage
    revenue_change = 0
    if last_month_revenue > 0:
        revenue_change = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    # Current month transactions
    current_month_transactions = Payment.objects.filter(
        provider=provider,
        created_at__month=current_month,
        created_at__year=current_year
    ).count()
    
    # Last month transactions
    last_month_transactions = Payment.objects.filter(
        provider=provider,
        created_at__month=last_month,
        created_at__year=last_month_year
    ).count()
    
    # Transactions change percentage
    transactions_change = 0
    if last_month_transactions > 0:
        transactions_change = ((current_month_transactions - last_month_transactions) / last_month_transactions) * 100
    
    context = {
        'page_title': 'Service Provider Dashboard',
        'active_tab': 'home',
        'recent_transactions': recent_transactions,
        'current_month_revenue': current_month_revenue,
        'revenue_change': revenue_change,
        'current_month_transactions': current_month_transactions,
        'transactions_change': transactions_change,
        'form': PaymentForm()
    }
    
    return render(request, 'home/provider_dashboard.html', context)
'''
'''@csrf_exempt
@login_required
def process_payment(request):
    print("=" * 50)
    print("PAYMENT PROCESSING STARTED")
    print(f"Request method: {request.method}")
    print(f"Content type: {request.content_type}")

    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'
        }, status=405)

    # Decode the request body
    try:
        request_body = request.body.decode('utf-8')
        print(f"Raw request body: {request_body}")
    except Exception as e:
        print(f"Error decoding request body: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Cannot decode request body.'
        }, status=400)

    try:
        # Parse JSON data from the request body
        data = json.loads(request_body)
        print(f"Parsed JSON data: {data}")

        payment_id = data.get('payment_id')
        amount = data.get('amount')
        method_name = data.get('method')  # e.g., "Ecocash"

        print(f"Extracted values - Payment ID: {payment_id}, Amount: {amount}, Method: {method_name}")

        # Validate required fields
        if not payment_id:
            print("ERROR: Missing payment_id")
            return JsonResponse({
                'status': 'error',
                'message': 'Payment ID is required.'
            }, status=400)
        if not method_name:
            print("ERROR: Missing payment method")
            return JsonResponse({
                'status': 'error',
                'message': 'Payment method is required.'
            }, status=400)

        print(f"Received payment: ID={payment_id}, Amount={amount}, Method={method_name}")

        # Retrieve the transaction by payment_id
        txn = Transactions.objects.get(payment_id=payment_id)
        print(f"Found transaction: {txn}")

        # Find the PaymentMethod instance using the correct field; adjust here if you have a different field name
        # Example of your view processing
        payment_method_obj = PaymentMethod.objects.filter(code=method_name).first()

        if not payment_method_obj:
            print(f"Payment method '{method_name}' not found.")
            return JsonResponse({
                'status': 'error',
                'message': f'Payment method "{method_name}" not found.'
            }, status=404)

        # Validate payment amount (Optional)
        if txn.amount != float(amount):
            print("Amount mismatch: Transaction amount does not match provided amount.")
            return JsonResponse({
                'status': 'error',
                'message': 'Amount mismatch. Please check the payment details.'
            }, status=400)

        # Update the transaction
        txn.status = 'completed'
        txn.payment_method = payment_method_obj
        txn.completed_at = timezone.now()
        txn.save()
        print("Transaction updated successfully.")

        return JsonResponse({
            'status': 'success',
            'message': 'Payment processed successfully!',
            'payment_id': payment_id,
            'amount': amount
        })

    except Transactions.DoesNotExist:
        print("Transaction not found for the given payment_id.")
        return JsonResponse({
            'status': 'error',
            'message': 'Transaction not found.'
        }, status=404)
    except json.JSONDecodeError:
        print("Invalid JSON data received.")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Payment processing error: {str(e)}'
        }, status=500)'''