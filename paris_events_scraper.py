from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import time

# --- CONFIGURATION ---
BOT_TOKEN = "TON_TOKEN_BOT"  # Remplace par le token de ton bot Telegram
CHAT_ID = "TON_CHAT_ID"  # Remplace par ton chat_id

# --- FONCTIONS ---
def scrape_weezevent():
    """Scrape les événements sur my.weezevent.com pour Paris avec Selenium."""
    url = "https://my.weezevent.com/recherche?query=Paris"
    options = Options()
    options.headless = True  # Exécute en arrière-plan
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)  # Attendre que la page charge

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    events = []
    # Exemple de sélection (à adapter selon la structure réelle de la page)
    for event in soup.select('.event-list-item, .card, .item'):
        title = event.select_one('h3, .event-title, .title').text.strip() if event.select_one('h3, .event-title, .title') else "Sans titre"
        link = event.select_one('a[href*="/event/"]')['href'] if event.select_one('a[href*="/event/"]') else "#"
        date_text = event.select_one('time, .event-date, .date').text.strip() if event.select_one('time, .event-date, .date') else ""
        events.append({
            "title": title,
            "link": f"https://my.weezevent.com{link}" if not link.startswith('http') else link,
            "date": date_text
        })
    return events

def scrape_billetweb():
    """Scrape les événements sur billetweb.fr pour Paris avec Selenium."""
    url = "https://www.billetweb.fr/recherche?query=Paris"
    options = Options()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)  # Attendre que la page charge

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    events = []
    # Exemple de sélection (à adapter selon la structure réelle de la page)
    for event in soup.select('.event-card, .card, .item'):
        title = event.select_one('h2, .event-name, .title').text.strip() if event.select_one('h2, .event-name, .title') else "Sans titre"
        link = event.select_one('a[href*="/event/"]')['href'] if event.select_one('a[href*="/event/"]') else "#"
        date_text = event.select_one('time, .event-date, .date').text.strip() if event.select_one('time, .event-date, .date') else ""
        events.append({
            "title": title,
            "link": f"https://www.billetweb.fr{link}" if not link.startswith('http') else link,
            "date": date_text
        })
    return events

def filter_upcoming_events(events):
    """Filtre les événements à venir en fonction de leur date."""
    upcoming_events = []
    today = datetime.now().date()

    for event in events:
        date_str = event.get("date", "")
        try:
            # Essaye plusieurs formats de date
            for fmt in ('%d %B %Y', '%d/%m/%Y', '%Y-%m-%d'):
                try:
                    event_date = datetime.strptime(date_str, fmt).date()
                    if event_date >= today:
                        upcoming_events.append(event)
                        break
                except:
                    continue
        except:
            upcoming_events.append(event)
    return upcoming_events

def send_telegram_notification(events, bot_token, chat_id):
    """Envoie une notification Telegram avec la liste des événements."""
    if not events:
        message = "❌ Aucun événement trouvé pour Paris aujourd'hui."
    else:
        message = "📅 **Événements à Paris aujourd'hui** :\n\n"
        for event in events:
            message += f"- [{event['title']}]({event['link']}) (Date: {event.get('date', 'Inconnue')})\n"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    requests.post(url, params=params)

# --- EXÉCUTION ---
if __name__ == "__main__":
    weezevent_events = scrape_weezevent()
    billetweb_events = scrape_billetweb()

    all_events = weezevent_events + billetweb_events
    upcoming_events = filter_upcoming_events(all_events)

    send_telegram_notification(upcoming_events, BOT_TOKEN, CHAT_ID)
    print(f"Notification envoyée avec {len(upcoming_events)} événements.")
