import time
import requests
from web3 import Web3
from flask import Flask

# Configuration
start_wallet = "0x440Ea720B03A8785cfF8E98bd4d689F37be513B8"
end_wallet = "0xbf06Cf71d41fd60AA82E4E9327D635Ffd39306b2"
api_key = "MGDY7WG2C8PT2691IBKA11DI7UAH9N4NBV"
minimum_amount = 0.00001  # BNB
private_key = "0x8154cf6b9e798493ec5b7ef8ca2aaec6383c896ace7f0316e07cc40928d88f29"  # Assure-toi que ta clé privée est sécurisée.

# Connexion à la blockchain Binance Smart Chain (BSC)
bsc_url = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc_url))

# Vérification de la connexion
if not web3.is_connected():
    print("Erreur de connexion à la BSC.")
    exit()

# Fonction pour vérifier les transactions entrantes
def check_transactions():
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={start_wallet}&startblock=0&endblock=latest&sort=desc&apikey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 429:  # Trop de requêtes
        print("Trop de requêtes détectées. Pause de 10 secondes...")
        time.sleep(10)  # Pause pour éviter un bannissement
        return
    elif response.status_code != 200:
        print(f"Erreur de l'API BscScan: {response.status_code}")
        return

    data = response.json()
    if data['status'] == '1':
        for tx in data['result']:
            # Vérifier si la transaction est un virement de BNB
            if tx['to'].lower() == start_wallet.lower() and float(tx['value']) / 10**18 >= minimum_amount:
                amount_in_bnb = float(tx['value']) / 10**18
                print(f"Transaction trouvée: {amount_in_bnb} BNB")
                if amount_in_bnb >= minimum_amount:
                    send_bnb(amount_in_bnb)
                    break

# Fonction pour envoyer les BNB vers un autre portefeuille
def send_bnb(amount):
    nonce = web3.eth.get_transaction_count(start_wallet)
    
    # Préparer la transaction
    transaction = {
        'to': end_wallet,
        'value': web3.to_wei(amount, 'ether'),
        'gas': 200000,
        'gasPrice': web3.to_wei('5', 'gwei'),
        'nonce': nonce,
        'chainId': 56  # BSC Mainnet
    }
    
    # Signer la transaction
    signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
    
    # Envoyer la transaction
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    print(f"Transaction envoyée, hash: {web3.toHex(tx_hash)}")

# Boucle pour surveiller les transactions toutes les 3 secondes
def monitor_transactions():
    while True:
        check_transactions()
        time.sleep(3)  # Vérifie toutes les 3 secondes

# Serveur Flask pour Render
app = Flask(__name__)

@app.route("/")  # Page par défaut
def home():
    return "Le bot fonctionne ! 🎉"

# Lancer le bot et le serveur Flask
if __name__ == "__main__":
    import os
    from threading import Thread

    # Lancer la surveillance des transactions dans un thread séparé
    thread = Thread(target=monitor_transactions)
    thread.start()

    # Démarrer le serveur Flask pour Render
    port = int(os.environ.get("PORT", 5000))  # Render choisit un port automatiquement
    app.run(host="0.0.0.0", port=port)
