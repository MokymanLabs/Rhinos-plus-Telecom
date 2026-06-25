from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from extensions import db, migrate, mail
from models import Subscriber, ContactMessage
from flask_mail import Message


app = Flask(__name__)

#===============================================
# CONFIGURATION
#===============================================
app.config.from_object(Config)

#================================
# INITIALISATION EXTENSIONS
#================================
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)


@app.route('/')

def index():
    return render_template('index.html', titre="Accueil")


@app.route('/about')
def about():
    return render_template('about.html',titre="À propos")


@app.route('/services')
def services():
    return render_template('services.html', titre="Services")


@app.route('/services/deploiement')
def deploiement():
    return render_template('services/deploiement.html', titre="Déploiement")


@app.route('/services/inst_reseau')
def inst_reseau():
    return render_template('services/installation_reseau.html', titre="Installation Réseau")

@app.route('/services/inst_electrique')
def inst_electrique():
    return render_template('services/installation_electrique.html', titre="Installation Électrique")

@app.route('/services/maintenance')
def maintenance():
    return render_template('services/maintenance.html', titre="Maintenance")

@app.route('/services/trav_hauteur')
def trav_hauteur():
    return render_template('services/travaux_hauteur.html', titre="Travaux en Hauteur")

@app.route('/services/fibre_optique')
def fibre_optique():
    return render_template('services/fibre_optique.html', titre="Fibre Optique")

@app.route('/services/optimisation')
def optimisation():
    return render_template('services/optimisation.html', titre="Optimisation")

@app.route('/services/audit')
def audit():
    return render_template('services/audit.html', titre="Audit")

@app.route('/services/electrogene')
def electrogene():
    return render_template('services/electrogene.html', titre="Électrogène")

@app.route('/services/aviation')
def aviation():
    return render_template('services/aviation.html', titre="Aviation")

@app.route('/services/panneau')
def panneau():
    return render_template('services/panneau_solaire.html', titre="Panneau Solaire")

@app.route('/services/power_room')
def power_room():
    return render_template('services/power_room.html', titre="Power Room")


@app.route('/newsletter', methods=["POST"])
def newsletter():
    email = request.form.get("email")
    if not email:
        flash("Veuillez entrer un email", "danger")
        return redirect ( url_for('index') )
        
    existing_user = Subscriber.query.filter_by(email=email).first()
    
    if existing_user:
        flash("Email déjà enregistré", "warning")
        return redirect (url_for('index') )
        
    new_subscriber = Subscriber(email=email)
    
    db.session.add(new_subscriber)
    db.session.commit()
    
    # -----------------------------
    # SEND EMAIL
    # -----------------------------
    msg = Message(
        subject="Merci pour votre inscription",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.html = """
        <h2>Bienvenue 🎉</h2>

        <p>
            Merci de vous être inscrit à notre newsletter.
        </p>

        <p>
           Nous sommes ravis de vous compter parmi nos abonnés.
           Vous recevrez desormais les dernières nouvelles, 
           offres et mises à jour directement dans votre boîte de réception.
        </p>
        
        <p>
            Merci pour votre confiance.
        </p>
        
        <br>

        <p>
            Cordialement,<br>
            Rhinos Plus Telecom
        </p>
    """

    try:
        mail.send(msg)
        flash("Inscription réussie ! Vérifiez votre email.", "success")
    except Exception as e:
        db.session.rollback()
        print("MAIL ERROR (newsletter):", e)
        flash("Inscription enregistrée, mais email non envoyé.", "warning")        
    
    return redirect ( url_for('index') )


# -----------------------------
# CONTACT
# -----------------------------
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        service = request.form.get("service")
        message_text = request.form.get("message")

        # -----------------------------
        # SAVE DATABASE
        # -----------------------------
        new_message = ContactMessage(
            full_name=full_name,
            email=email,
            phone=phone,
            service=service,
            message=message_text
        )

        db.session.add(new_message)
        db.session.commit()

        # -----------------------------
        # EMAILS
        # -----------------------------
        company_email = Message(
            subject="Nouveau message client",
            sender=app.config["MAIL_USERNAME"],
            recipients=[app.config["MAIL_USERNAME"]]
        )

        company_email.html = f"""
            <h2>Nouveau message reçu</h2>
            <p><strong>Nom :</strong> {full_name}</p>
            <p><strong>Email :</strong> {email}</p>
            <p><strong>Téléphone :</strong> {phone}</p>
            <p><strong>Service :</strong> {service}</p>
            <p><strong>Message :</strong></p>
            <p>{message_text}</p>
        """

        user_email = Message(
            subject="Nous avons bien reçu votre message",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )

        user_email.html = f"""
            <h2>Bonjour {full_name} 👋</h2>

            <p>Merci de nous avoir contactés.</p>

            <p>
                Notre équipe analysera votre demande
                et vous répondra rapidement.
            </p>

            <br>

            <p>
                Cordialement,<br>
                RHINOS PLUS
            </p>
        """

        # -----------------------------
        # SAFE EMAIL SENDING
        # -----------------------------
        try:
            mail.send(company_email)
            mail.send(user_email)

            flash("Votre message a été envoyé avec succès.", "success")

        except Exception as e:
            print("MAIL ERROR (contact):", e)
            flash("Message enregistré, mais email non envoyé.", "warning")

        return redirect(url_for("contact"))

    return render_template("contact.html", titre="Contact")




#@app.route('/contact')
#def contact():
    #return render_template('contact.html')


if __name__ == '__main__':
    ##app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    