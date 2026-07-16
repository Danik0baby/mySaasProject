import os
import time
import logging
import threading
import requests
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = os.getenv("SYMBOL")
ALERT_PERCENT = float(os.getenv("ALERT_PERCENT", 1.0))

class CryptoMonitor:
    def __init__(self):
        self.session = HTTP(testnet=False)   # от pybit, можно менять на тестовую версию
        self.base_price = None
        self.running = False
        
    def send_telegram_message(self, text): # Каким должен быть сообщение, напомню что надо в .env указать нужные данные
        """Отправка сообщения в Telegram"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text}
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                logging.error(f"Ошибка отправки в Telegram: {response.text}")
        except Exception as err:
            logging.error(f"Ошибка сети при отправке в Telegram: {err}")

    def get_current_price(self): # Получение текущей цены
        response = self.session.get_tickers(category="linear", symbol=SYMBOL)
        return float(response['result']['list'][0]['lastPrice'])

    def check_and_alert(self): # Проверка цены и отправка алерта
        try:
            current_price = self.get_current_price()
            percent_change = ((current_price - self.base_price) / self.base_price) * 100

            logging.info(f"Цена: {current_price} USD | Изменение: {percent_change:+.2f}% (База: {self.base_price})")

            if abs(percent_change) >= ALERT_PERCENT:
                message = (
                    f"Внимание! Мониторинг {SYMBOL}\n"
                    f"Изменение цены: {percent_change:+.2f}%\n"
                    f"Текущая цена: {current_price} USD\n"
                    f"Предыдущая база: {self.base_price} USD"
                )
                
                self.send_telegram_message(message)
                logging.info(f"Отправлено уведомление в Telegram. Изменение: {percent_change:+.2f}%")

                self.base_price = current_price
                logging.info(f"Базовая цена обновлена до: {self.base_price} USD")

        except Exception as e:
            logging.error(f"Произошла ошибка при выполнении: {e}")

    def start_monitoring(self): # Запуск
        try:
            self.base_price = self.get_current_price()
            logging.info(f"Начальная базовая цена {SYMBOL} зафиксирована: {self.base_price} USD")
            
            self.running = True
            while self.running:
                self.check_and_alert()
                time.sleep(10)
                
        except Exception as e:
            logging.critical(f"Не удалось получить начальную цену: {e}")
            raise

    def stop_monitoring(self): # Остановка мониторинга
        self.running = False
        logging.info("Мониторинг остановлен")

# Создаем экземпляр монитора
monitor = CryptoMonitor()