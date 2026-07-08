from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'

    def ready(self):
        # Python 3.14 compatibility monkeypatch for django template context copy
        from django.template.context import Context

        def patched_copy(self):
            class Dummy:
                pass
            duplicate = Dummy()
            duplicate.__class__ = self.__class__
            duplicate.dicts = self.dicts[:]
            for k, v in self.__dict__.items():
                if k != 'dicts':
                    setattr(duplicate, k, v)
            return duplicate

        Context.__copy__ = patched_copy

