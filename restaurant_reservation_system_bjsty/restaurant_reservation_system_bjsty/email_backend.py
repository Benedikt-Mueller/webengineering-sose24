import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend

class MyCustomEmailBackend(SMTPEmailBackend):
    def open(self):
        """
        Stellt die Verbindung zum E-Mail-Server her, unter Nutzung eines SSL-Kontextes,
        der selbst signierte Zertifikate akzeptiert, falls dies notwendig ist.
        """
        if self.connection:
            # Verbindung existiert bereits, nichts weiter zu tun
            return False

        try:
            # Initialisiert eine Verbindungsinstanz ohne angegebene Authentifizierungsdetails
            self.connection = self.connection_class(self.host, self.port, timeout=self.timeout) 

            # Konfigurieren des SSL-Kontextes, sofern TLS genutzt wird
            if self.use_tls:
                context = ssl._create_unverified_context()
                self.connection.ehlo()
                self.connection.starttls(context=context)
                self.connection.ehlo()

            # Authentifizierung mit dem E-Mail-Server
            if self.username and self.password:
                self.connection.login(self.username, self.password)

        except:
            # Einfangen aller Ausnahmen, Loggen oder Weiterwerfen, falls fail_silently=False
            if not self.fail_silently:
                raise
            self.connection = None
            return False

        return True