"""
Script to fix token_blacklist foreign key constraint
Drops the tables and recreates them with correct FK to administrator_administrator
"""
import os
import django
import subprocess

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rightOnTime.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def fix_token_blacklist():
    print("Step 1: Dropping token_blacklist tables...")
    with connection.cursor() as cursor:
        # Drop the blacklisted token table first (it has FK to outstanding)
        cursor.execute("DROP TABLE IF EXISTS token_blacklist_blacklistedtoken CASCADE;")
        print("✓ Dropped token_blacklist_blacklistedtoken")
        
        # Drop the outstanding token table
        cursor.execute("DROP TABLE IF EXISTS token_blacklist_outstandingtoken CASCADE;")
        print("✓ Dropped token_blacklist_outstandingtoken")
        
        # Delete migration records for token_blacklist
        cursor.execute("DELETE FROM django_migrations WHERE app = 'token_blacklist';")
        print("✓ Cleared token_blacklist migration records")
        
    print("\nStep 2: Recreating tables with correct FK...")
    call_command('migrate', 'token_blacklist', verbosity=1)
    
    print("\n✅ Token blacklist tables fixed successfully!")
    print("Now you can login with your admin credentials.")

if __name__ == '__main__':
    fix_token_blacklist()
