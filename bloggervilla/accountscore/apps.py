from django.apps import AppConfig


class AccountscoreConfig(AppConfig):
    name = 'accountscore'
    
    def ready(self):
        import accountscore.signals