from django.core.management.base import BaseCommand
from cryptoMonitoring.services import monitor
import threading

class Command(BaseCommand):
    help = 'Запуск мониторинга криптовалют' #На всякий случьи

    def add_arguments(self, parser):
        parser.add_argument(
            '--stop',
            action='store_true',
            help='Остановить мониторинг',
        )

    def handle(self, *args, **options):
        if options['stop']:
            monitor.stop_monitoring()
            self.stdout.write(self.style.SUCCESS('Мониторинг остановлен'))
            return
        
        
        # Запуск мониторинга отдельно
        thread = threading.Thread(target=monitor.start_monitoring, daemon=True)  
        thread.start()
        
        self.stdout.write(self.style.SUCCESS('Мониторинг запущен!'))
        self.stdout.write('Нажмите Ctrl+C для остановки')
        
        # Держим процесс активным
        try:
            thread.join()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            self.stdout.write(self.style.SUCCESS('Мониторинг остановлен'))