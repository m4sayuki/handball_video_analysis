from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Stock info notice
    
    コマンド例: python3 manage.py stock_info_notice
    """
    help = 'Stock info notice'

    def handle(self, *args, **options):
        self.stdout.write('Stock info notice')
        self.stdout.write(self.style.SUCCESS('コマンドが正常に実行されました'))
