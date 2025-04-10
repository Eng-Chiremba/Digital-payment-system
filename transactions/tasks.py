from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
import time
from datetime import timedelta

logger = get_task_logger(__name__)

@shared_task
def process_payment_async(transaction_id, payment_method_id):
    """
    Process a payment asynchronously using Celery
    
    This task handles the payment processing in the background to avoid
    blocking the web request.
    """
    from .services import process_payment, update_transaction_status
    from .models import TransactionStatus
    
    logger.info(f"Processing payment for transaction {transaction_id}")
    
    try:
        # Process the payment
        transaction, response = process_payment(transaction_id, payment_method_id)
        
        if not transaction:
            logger.error(f"Failed to process payment for transaction {transaction_id}")
            return False
        
        logger.info(f"Payment processed for transaction {transaction_id} with status {transaction.status}")
        return True
    except Exception as e:
        logger.error(f"Error processing payment for transaction {transaction_id}: {str(e)}")
        
        # Update transaction status to FAILED
        try:
            update_transaction_status(
                transaction_id=transaction_id,
                new_status=TransactionStatus.FAILED,
                notes=f"Payment processing error: {str(e)}"
            )
        except Exception as update_error:
            logger.error(f"Error updating transaction status: {str(update_error)}")
        
        return False

@shared_task
def check_expired_transactions():
    """
    Check for expired transactions and update their status
    
    This task runs periodically to identify and update transactions that have expired.
    """
    from .models import Transaction, TransactionStatus
    from .services import update_transaction_status
    
    logger.info("Checking for expired transactions")
    
    # Get current time
    now = timezone.now()
    
    # Find pending transactions that have expired
    expired_transactions = Transaction.objects.filter(
        status=TransactionStatus.PENDING,
        expires_at__lt=now
    )
    
    count = 0
    for transaction in expired_transactions:
        update_transaction_status(
            transaction_id=transaction.id,
            new_status=TransactionStatus.CANCELLED,
            notes="Transaction expired automatically"
        )
        count += 1
    
    logger.info(f"Updated {count} expired transactions")
    return count

@shared_task
def retry_failed_transactions():
    """
    Retry transactions that failed due to temporary issues
    
    This task attempts to reprocess transactions that failed due to
    temporary issues like network errors or gateway timeouts.
    """
    from .models import Transaction, TransactionStatus
    from .services import update_transaction_status, process_payment
    
    logger.info("Checking for failed transactions to retry")
    
    # Get transactions that failed within the last 24 hours
    retry_before = timezone.now() - timedelta(hours=24)
    
    # Find failed transactions that can be retried
    failed_transactions = Transaction.objects.filter(
        status=TransactionStatus.FAILED,
        updated_at__gt=retry_before
    ).exclude(
        gateway_response__contains='"permanent_failure": true'
    )
    
    count = 0
    success_count = 0
    
    for transaction in failed_transactions:
        # Only retry if we have a payment method
        if not transaction.payment_method:
            continue
        
        # Update status to processing
        update_transaction_status(
            transaction_id=transaction.id,
            new_status=TransactionStatus.PROCESSING,
            notes="Retrying failed transaction"
        )
        
        # Process payment
        _, response = process_payment(transaction.id, transaction.payment_method.id)
        
        count += 1
        if response.get('success', False):
            success_count += 1
    
    logger.info(f"Retried {count} failed transactions, {success_count} succeeded")
    return success_count