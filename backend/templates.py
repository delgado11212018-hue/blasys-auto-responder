
from config import Config

def pick_template(sentiment: str, personalized: bool, lang: str, is_influencer: bool, is_repeat: bool):
    brand = Config.BRAND_NAME
    if sentiment == "positive":
        if is_influencer:
            return {"es": f"¡Gracias por la vibra! Nos encantaría invitarte a probar nuestro menú nuevo en {brand}. Escríbenos por DM para coordinar.",
                    "en": f"Thanks for the love! We'd love to host you to try our new menu at {brand}. DM us to coordinate."}[lang]
        return {"es": f"¡Gracias por tu comentario! Nos alegra que te guste. ¡Te esperamos pronto en {brand}!",
                "en": f"Thanks for the kind words! Hope to see you soon at {brand}!"}[lang]
    if sentiment == "question":
        return {"es": f"¡Gracias por tu pregunta! Te escribimos por DM con los detalles. Mientras, aquí estamos para ayudarte en {brand}.",
                "en": f"Great question! We’ll DM you the details. Meanwhile, we’re here to help at {brand}."}[lang]
    if sentiment == "negative":
        return {"es": "Lamentamos lo ocurrido. Queremos solucionarlo: por favor envíanos un DM con tu número de contacto y detalles. Gracias por darnos la oportunidad de mejorar.",
                "en": "We’re sorry about your experience. Please DM us your contact and details so we can make it right. Thank you for the chance to improve."}[lang]
    return {"es": f"¡Gracias por escribirnos! {brand} está para servirte.",
            "en": f"Thanks for reaching out! {brand} is here for you."}[lang]
