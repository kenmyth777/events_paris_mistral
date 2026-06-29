import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# --- CONFIGURATION ---
BOT_TOKEN = "TON_TOKEN_BOT"  # Remplace par le token de ton bot Telegram
CHAT_ID = "TON_CHAT_ID"  # Remplace par ton chat_id

# --- FONCTIONS ---
def scrape_weezevent():
    """Scrape les événements sur my.weezevent.com pour Paris."""
    url = "https://my.weezevent.com/recherche?query=Paris"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        events = []
        # Exemple de sélection (à adapter selon la structure réelle de la page)
        for event in soup.select('.event-item'):
            title = event.select_one('.event-title').text.strip() if event.select_one('.event-title') else "Sans titre"
            link = event.select_one('a')['href'] if event.select_one('a') else "#"
            date_text = event.select_one('.event-date').text.strip() if event.select_one('.event-date') else ""
            events.append({"title": title, "link": f"https://my.weezevent.com{link}", "date": date_text})
        return events
    except Exception as e:
        print(f"Erreur lors du scraping de Weezevent : {e}")
        return []

def scrape_billetweb():
    """Scrape les événements sur billetweb.fr pour Paris."""
    url = "https://www.billetweb.fr/recherche?query=Paris"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        events = []
        # Exemple de sélection (à adapter selon la structure réelle de la page)
        for event in soup.select('.event-card'):
            title = event.select_one('.event-name').text.strip() if event.select_one('.event-name') else "Sans titre"
            link = event.select_one('a')['href'] if event.select_one('a') else "#"
            date_text = event.select_one('.event-date').text.strip() if event.select_one('.event-date') else ""
            events.append({"title": title, "link": f"https://www.billetweb.fr{link}", "date": date_text})
        return events
    except Exception as e:
        print(f"Erreur lors du scraping de BilletWeb : {e}")
        return []

def filter_upcoming_events(events):
    """Filtre les événements à venir en fonction de leur date."""
    upcoming_events = []
    today = datetime.now().date()

    for event in events:
        date_str = event.get("date", "")
        # Extraire la date depuis le texte (ex: "30 juin 2026")
        try:
            # Utiliser une expression régulière pour extraire la date
            date_match = re.search(r'\d{1,2}\s\w+\s\d{4}', date_str)
            if date_match:
                date_str = date_match.group()
                event_date = datetime.strptime(date_str, '%d %B %Y').date()
                if event_date >= today:
                    upcoming_events.append(event)
        except:
            # Si la date n'est pas au format attendu, on garde l'événement
            upcoming_events.append(event)

    return upcoming_events

def send_telegram_notification(events, bot_token, chat_id):
    """Envoie une notification Telegram avec la liste des événements."""
    if not events:
        message = "❌ Aucun événement trouvé pour Paris aujourd'hui."
    else:
        message = "📅 **Événements à Paris aujourd'hui** :\n\n"
        for event in events:
            message += f"- [{event['title']}]({event['link']}) (Date: {event.get('date', 'Inconnue')})\\n"

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
