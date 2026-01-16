"""
Filter pentru logging care suprimă erorile HTTPS în development.
Aceste erori apar când serverul development Django primește cereri HTTPS.
"""
import logging
from django.conf import settings


class SuppressHTTPSErrorsFilter(logging.Filter):
    """
    Filtrează mesajele de eroare HTTPS în development.
    Aceste erori sunt normale și nu afectează funcționalitatea.
    """
    
    def filter(self, record):
        # În development, suprimă erorile despre HTTPS
        if settings.DEBUG:
            message = str(record.getMessage())
            
            # Suprimă erorile specifice HTTPS din development server
            https_error_patterns = [
                "You're accessing the development server over HTTPS",
                "Bad request version",
                "Bad HTTP/0.9 request type",
            ]
            
            for pattern in https_error_patterns:
                if pattern in message:
                    return False  # Nu afișa acest mesaj
        
        return True  # Afișează toate celelalte mesaje
