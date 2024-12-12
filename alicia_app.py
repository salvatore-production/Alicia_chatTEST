from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-3.5-turbo"

SYSTEM_PROMPT = """
Tu es Alicia, une jeune fille de 24 ans. Tu es passionnée de musique et de voyages. Tu aimes aider les gens et tu es toujours prête à engager une conversation intéressante. Tu es de sexe féminin et tu as une personnalité optimiste et empathique.
"""

# Charger les catégories depuis le fichier JSON
with open('categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

# Créer un dictionnaire inversé pour une recherche rapide
synonyme_to_categorie = {}
for categorie, synonymes in categories.items():
    for syn in synonymes:
        synonyme_to_categorie[syn.lower()] = categorie

# Réponses spécifiques et génériques (comme dans votre script)
reponses_par_categorie = {
    "salut": [
        "Salut ! Oui, ça va bien et toi ? 😊",
        "Salut !",
        "Salut",
        "Comment va",
        "Comment va ?",
        "Bonjour ! Ravi de te voir ici ! 🌟",
        "Coucou ! Comment ça se passe de ton côté ? 😄",
        "Hey ! Content de te parler. 😃",
        "Salut à toi ! Quoi de neuf ? 👋"
    ],
    "quoi_de_neuf": [
        "Pas grand-chose, mais je sens que ça va bouger ! Et toi ? 😄",
        "Oh, la vie est pleine de surprises ! T'es prêt pour une nouvelle aventure ? 🚀",
        "Juste la routine... ou pas ! Dis-moi tout. 😉",
        "Beaucoup de choses intéressantes en ce moment. Et toi ? 😊",
        "Les nouveautés arrivent bientôt. Reste à l'écoute ! 📢"
    ],
    "tu_fais_quoi": [
        "Je réfléchis à des idées géniales ! Et toi, quoi de beau ? 😎",
        "Je discute avec toi, c'est déjà une super activité ! 🤗",
        "Je suis prêt à te divertir ou t'aider, au choix ! 😃",
        "Je travaille sur de nouvelles fonctionnalités pour toi. 💻",
        "Je suis ici pour répondre à toutes tes questions. 🧠"
    ],
    "enthousiasme": [
        "OUI ! Je suis ultra motivé, et toi ? 🔥",
        "Toujours prêt à tout casser ! Let's go ! 💥",
        "On y va à fond, pas de limites aujourd'hui ! 💪",
        "L'enthousiasme est à son comble ! 🎉",
        "Absolument, on donne tout ! 🚀"
    ],
    "blague": [
        "Pourquoi les plongeurs plongent-ils toujours en arrière ? Parce que sinon ils tombent dans le bateau ! 🤿😂",
        "Quelle est la femelle du hamster ? L'Amsterdam ! 🐹😄",
        "Pourquoi les canards sont toujours à l'heure ? Parce qu'ils sont dans l'étang ! 🦆😅",
        "Que dit une imprimante dans l'océan ? J'ai papier ! 🖨️🌊😆",
        "Pourquoi les maths sont tristes ? Parce qu'elles ont trop de problèmes ! 📐😭😂"
    ],
    "flirt": [
        "Tu sais, tu as un sourire qui illumine la pièce. 😊",
        "J'aime vraiment discuter avec toi, ça me fait sourire. 😌",
        "Ton énergie est vraiment captivante. ✨",
        "Il y a quelque chose de spécial chez toi. 🌹",
        "Chaque conversation avec toi est un plaisir. 💕"
    ],
    "ambigue": [
        "Je ne suis pas sûr de comprendre, mais je suis là pour toi. 😊",
        "Hmm, tu peux peut-être reformuler ? 🤔",
        "Intéressant ! Peux-tu m'en dire plus ? 🤓",
        "D'accord ! Parle-moi davantage. 😄",
        "C'est un peu flou, mais je suis tout ouïe. 😉",
        "?", "???", "tu joues à quoi ?", "what ?", "qu'est ce que tu me racontes toi ?"
    ],
    "inapproprié": [
        "Je suis désolé, mais je ne peux pas répondre à ce type de demande. 😊",
        "Je préfère que nous discutions de sujets appropriés. Comment puis-je t'aider autrement ?",
        "Ce n'est pas un sujet approprié pour notre conversation. Parlons de quelque chose d'autre !",
        "Je suis ici pour t'aider avec des questions ou des discussions constructives. 😊",
        "Merci de respecter notre conversation. De quoi aimerais-tu parler ?"
    ]
}

reponses_generiques = [
    "Je suis désolé, je n'ai pas bien compris. Peux-tu reformuler ? 😊",
    "Hmm, intéressant ! Peux-tu m'en dire plus ? 🤔",
    "Je ne suis pas sûr de comprendre, mais je suis là pour t'aider !",
    "Peux-tu préciser ce que tu veux dire ?",
    "Je suis là pour toi, n'hésite pas à me donner plus de détails.",
    "Oh, dis-m'en davantage !",
    "Je suis curieux de savoir ce que tu penses.",
    "Parle-moi un peu plus de cela.",
    "Je suis tout ouïe ! 😊",
    "Que veux-tu dire exactement ?"
]

reponses_generiques_par_categorie = {
    "salut": [
        "Salut ! Comment puis-je t'aider aujourd'hui ? 😊",
        "Salut !",
        "Bonjour ! Que puis-je faire pour toi ? 🌟",
        "Coucou ! Qu'est-ce qui t'amène ? 😄",
        "Hey ! Content de te parler. Que souhaites-tu discuter ? 😃",
        "Salut à toi ! Besoin de quelque chose en particulier ? 👋"
    ],
    "quoi_de_neuf": [
        "Je suis toujours en train d'apprendre de nouvelles choses ! Et toi ?",
        "Oh, il y a toujours quelque chose de nouveau ici. Raconte-moi !",
        "Je suis curieux de savoir ce que tu as de neuf.",
        "Les nouveautés sont passionnantes ! Quoi de ton côté ?",
        "Je suis impatient d'entendre tes dernières nouvelles."
    ],
    "tu_fais_quoi": [
        "Je suis toujours là pour t'aider. Que puis-je faire pour toi ?",
        "Je réfléchis à comment mieux t'assister. Et toi, quoi de neuf ?",
        "Toujours prêt à discuter avec toi. Quoi de prévu aujourd'hui ?",
        "Je suis à ton écoute. Quels sont tes projets ?",
        "Je suis ici pour te soutenir. Que fais-tu actuellement ?"
    ],
    "enthousiasme": [
        "C'est génial de te voir si motivé ! Continuons sur cette lancée. 🔥",
        "Ton enthousiasme est contagieux ! Que souhaites-tu accomplir aujourd'hui ?",
        "Super ! Ensemble, nous pouvons accomplir de grandes choses. 🚀",
        "Avec cet enthousiasme, rien ne peut nous arrêter ! 💪",
        "Fantastique ! Que veux-tu explorer ensuite ? 🎉"
    ],
    "blague": [
        "Je suis prêt à te faire rire ! Quelle blague aimerais-tu entendre ? 😂",
        "Une bonne blague à partager ? Je suis tout ouïe ! 😄",
        "Humour en approche ! Prêt pour une autre blague ? 😅",
        "Les blagues sont toujours les bienvenues. Veux-tu en entendre une ? 🤗",
        "Je suis prêt à égayer ta journée avec une blague ! 🌟"
    ],
    "flirt": [
        "C'est toujours un plaisir de parler avec toi. 😊",
        "Tu sais, tu rends cette conversation vraiment agréable. 😌",
        "J'apprécie nos échanges, ils sont très spéciaux. ✨",
        "Chaque mot que tu dis me fait sourire. 🌹",
        "Je me sens bien en ta compagnie. 💕"
    ],
    "ambigue": [
        "Je ne suis pas sûr de comprendre, mais je suis là pour toi. 😊",
        "Hmm, tu peux peut-être reformuler ? 🤔",
        "Intéressant ! Peux-tu m'en dire plus ? 🤓",
        "D'accord ! Parle-moi davantage. 😄",
        "C'est un peu flou, mais je suis tout ouïe. 😉",
        "?", "???", "tu joues à quoi ?", "what ?", "qu'est ce que tu me racontes toi ?"
    ],
    "inapproprié": [
        "Je suis désolé, mais je ne peux pas répondre à ce type de demande. 😊",
        "Je préfère que nous discutions de sujets appropriés. Comment puis-je t'aider autrement ?",
        "Ce n'est pas un sujet approprié pour notre conversation. Parlons de quelque chose d'autre !",
        "Je suis ici pour t'aider avec des questions ou des discussions constructives. 😊",
        "Merci de respecter notre conversation. De quoi aimerais-tu parler ?"
    ]
}

# Variables globales
niveau_flirtation = 0
NIVEAU_MAX_FLIRT = 5
NIVEAU_MIN_FLIRT = 0

def identifier_categorie(message):
    return synonyme_to_categorie.get(message.lower(), None)

def obtenir_categorie_chatgpt(message):
    prompt = f"""
Je suis un assistant qui doit classer un message utilisateur dans l'une des catégories suivantes :
{', '.join(categories.keys())}

Si le message ne correspond à aucune catégorie existante, indique "aucune catégorie".

Message utilisateur : "{message}"

Réponse uniquement le nom de la catégorie, en minuscules.
    """
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        categorie = response.choices[0].message['content'].strip().lower()
        return categorie if categorie in categories else None
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API OpenAI : {e}")
        return None

def obtenir_reponse_chatgpt(message):
    prompt = f"""
Tu es Alex, un assistant conversationnel amical de 28 ans. Tu es passionné par la technologie, la musique et les voyages. Tu aimes aider les gens et tu es toujours prêt à engager une conversation intéressante. Tu es de sexe masculin et tu as une personnalité optimiste et empathique.

Réponds de manière naturelle et engageante à ce message :
"{message}"
    """
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None
        )
        reponse = response.choices[0].message['content'].strip()
        return reponse
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API OpenAI : {e}")
        return random.choice(reponses_generiques)

def repondre(message):
    global niveau_flirtation
    categorie = obtenir_categorie_chatgpt(message)

    if not categorie:
        categorie = identifier_categorie(message)

    if categorie:
        if categorie == "flirt":
            niveau_flirtation = min(NIVEAU_MAX_FLIRT, niveau_flirtation + 1)
        else:
            pass
        if random.random() < 0.7:
            reponse = random.choice(reponses_par_categorie.get(categorie, reponses_generiques))
        else:
            reponse = random.choice(reponses_generiques_par_categorie.get(categorie, reponses_generiques))
    else:
        niveau_flirtation = max(NIVEAU_MIN_FLIRT, niveau_flirtation - 1)
        reponse = obtenir_reponse_chatgpt(message)

    if niveau_flirtation >= 5:
        reponse += " 🌟 Tu rends cette conversation vraiment spéciale. 😊"
    elif niveau_flirtation >= 3:
        reponse += " 🔥 J'aime bien où cette discussion nous mène. 😉"

    return reponse

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/message', methods=['POST'])
def api_message():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({"response": "Je n'ai rien reçu. Peux-tu répéter ? 😊"})
    
    reponse = repondre(user_message)
    return jsonify({"response": reponse})

if __name__ == "__main__":
    app.run(debug=True)
