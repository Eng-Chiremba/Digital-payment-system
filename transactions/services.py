import base64
import json
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import requests
from .models import Transactions, TransactionHistory, TransactionStatus

API_URL = 'http://localhost:3000'

def generate_payment_id(transaction):
    """
    Generate a unique, encoded payment ID for a transaction
    
    The payment ID encodes the transaction ID and other details, making it
    both unique and decodable.
    """
    # Generate a base transaction ID prefix
    prefix = "TXN"
    
    # Get current timestamp
    timestamp = int(datetime.now().timestamp())
    
    # Generate a random UUID part
    random_part = str(uuid.uuid4().hex)[:6]
    
    # Create a unique identifier 
    unique_id = f"{prefix}-{timestamp}-{random_part}"
    
    # Create a shorter version for customer convenience
    short_id = f"{prefix}-{random_part.upper()}"
    
    return short_id

def decode_payment_id(payment_id):
    """
    Decode a payment ID to extract the original transaction details
    
    This function retrieves the transaction from the database based on 
    the payment ID.
    """
    try:
        # Get transaction from database
        transaction = Transaction.objects.get(payment_id=payment_id)
        
        return {
            'transaction_id': str(transaction.id),
            'amount': float(transaction.amount),
            'currency': transaction.currency,
            'description': transaction.description,
            'service_provider_id': transaction.service_provider.id,
            'status': transaction.status,
        }
    except Transaction.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error decoding payment ID: {str(e)}")
        return None

def validate_payment_details(transaction):
    """
    Validate transaction details before processing
    """
    # Check if amount is valid
    if transaction.amount <= 0:
        return {
            'valid': False,
            'message': 'Amount must be greater than zero'
        }
    
    # Validate currency
    valid_currencies = ['USD', 'ZIG']
    if transaction.currency not in valid_currencies:
        return {
            'valid': False,
            'message': f'Currency must be one of {", ".join(valid_currencies)}'
        }
    
    # All validations passed
    return {
        'valid': True,
        'message': 'Transaction details are valid'
    }

def update_transaction_status(transaction_id, new_status, notes=None):
    """
    Update transaction status and create history entry
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Update transaction status
        old_status = transaction.status
        transaction.status = new_status
        
        # If transaction is completed, set completed_at timestamp
        if new_status == TransactionStatus.COMPLETED:
            transaction.completed_at = timezone.now()
        
        transaction.save()
        
        # Create transaction history entry
        TransactionHistory.objects.create(
            transaction=transaction,
            status=new_status,
            notes=notes or f"Status changed from {old_status} to {new_status}"
        )
        
        return transaction
    except Transaction.DoesNotExist:
        return None

# Payment Gateway Integration Services
def mock_payment_gateway_request(transaction, payment_method):
    """
    Mock payment gateway integration for testing purposes
    
    In a production environment, this would be replaced with actual
    payment gateway API calls.
    """
    # Simulate API request to payment gateway
    mock_api_url = settings.MOCK_PAYMENT_API_URL
    
    # Prepare request payload
    payload = {
        'transaction_id': str(transaction.id),
        'payment_id': transaction.payment_id,
        'amount': float(transaction.amount),
        'currency': transaction.currency,
        'payment_method': payment_method.code,
        'customer_email': transaction.customer_email,
        'customer_name': transaction.customer_name,
    }
    
    try:
        # In a real environment, this would be an actual API call
        # For testing, we'll simulate a successful response
        
        # Uncomment this for actual API call integration
        # response = requests.post(mock_api_url, json=payload)
        # return response.json()
        
        # Mock response for testing
        mock_response = {
            'success': True,
            'transaction_id': str(transaction.id),
            'payment_id': transaction.payment_id,
            'status': 'COMPLETED',
            'gateway_reference': f"MOCK-{uuid.uuid4().hex[:10].upper()}",
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulate processing delay (1-2 seconds)
        import time
        import random
        time.sleep(random.uniform(1, 2))
        
        return mock_response
    except Exception as e:
        # Log the error and return failure response
        print(f"Error in payment gateway request: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'transaction_id': str(transaction.id),
            'payment_id': transaction.payment_id,
            'status': 'FAILED'
        }

def process_payment(transaction_id, payment_method_id):
    """
    Process a payment through the payment gateway
    """
    from .models import PaymentMethod
    
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        payment_method = PaymentMethod.objects.get(id=payment_method_id)
        
        # Calculate processing fee
        transaction.payment_method = payment_method
        transaction.processing_fee = transaction.calculate_processing_fee()
        transaction.save()
        
        # Submit payment to gateway
        gateway_response = mock_payment_gateway_request(transaction, payment_method)
        
        # Update transaction with gateway response
        transaction.gateway_response = gateway_response
        
        # Update transaction status based on gateway response
        if gateway_response.get('success', False):
            new_status = TransactionStatus.COMPLETED
        else:
            new_status = TransactionStatus.FAILED
        
        # Update status with notes
        transaction = update_transaction_status(
            transaction_id=transaction_id,
            new_status=new_status,
            notes=f"Payment gateway response: {gateway_response.get('status')}"
        )
        
        return transaction, gateway_response
    except Exception as e:
        # Log the error and update transaction status
        print(f"Error processing payment: {str(e)}")
        
        try:
            update_transaction_status(
                transaction_id=transaction_id,
                new_status=TransactionStatus.FAILED,
                notes=f"Payment processing error: {str(e)}"
            )
        except:
            pass
        
        return None, {'success': False, 'error': str(e)}

def get_transaction_status(payment_id):
    """
    Get the current status of a transaction
    """
    try:
        transaction = Transaction.objects.get(payment_id=payment_id)
        
        return {
            'payment_id': transaction.payment_id,
            'status': transaction.status,
            'amount': float(transaction.amount),
            'processing_fee': float(transaction.processing_fee),
            'total_amount': float(transaction.total_amount),
            'currency': transaction.currency,
            'created_at': transaction.created_at.isoformat(),
            'updated_at': transaction.updated_at.isoformat(),
            'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
        }
    except Transaction.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error getting transaction status: {str(e)}")
        return None