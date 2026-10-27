from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("job", "transaction_type", "amount", "status", "gateway_reference", "created_at")
    list_filter = ("transaction_type", "status")
