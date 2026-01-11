# MiCasa

Welkom bij ons project genaamd MiCasa,










Gemaakt door Mohamed amin, Brian, Ersin, Mohamed-Amine, Jay en Adnan Van de klas ICT-V10


Micasa is een SmartHome-oplossing gericht op Airbnb-eigenaren die grip willen krijgen op hun energieverbruik en kosten. Door middel van een overzichtelijk dashboard krijgen gebruikers realtime inzicht in hun woning en ontvangen zij slimme voorspellingen over toekomstig energieverbruik.
Het doel van Micasa is kostenbesparing, verduurzaming en comfortverhoging voor zowel verhuurders als gasten.

De applicatie is ontwikkeld als onderdeel van het HBO-ICT project SmartHome, waarbij Business IT & Management, Artificial Intelligence, CSC, TI en Software Development samenkomen in één geïntegreerd eindproduct.




Technologiën:
Programmeertaal: Python
GUI: Tkinter
Database: PostgreSQL
Platform: Desktop & Raspberry Pi
Versiebeheer: GitHub (private repository)



"Functionaliteiten"
Inloggen

Bij het opstarten van de applicatie wordt een inlogscherm getoond. Alleen geautoriseerde gebruikers krijgen toegang tot het dashboard.

Dashboard

Na het inloggen ziet de gebruiker een centraal dashboard met:

Actuele buitentemperatuur

Dagelijks energieverbruik

Energiekosten van vandaag

Actieve slimme apparaten (zoals verwarming, verlichting)

Een AI-voorspelling van het verwachte energieverbruik en de bijbehorende kosten

Alle data wordt opgehaald uit de PostgreSQL-database



"Artificial Intelligence – Lineaire Regressie"
Doel van de AI-functionaliteit

Het doel van de AI is om dagelijks energieverbruik te voorspellen, zodat verhuurders vooraf inzicht krijgen in hun verwachte kosten en hierop kunnen anticiperen.

Keuze targetvariabele

Targetvariabele: Dagelijks energieverbruik (kWh)

Deze variabele is gekozen omdat dit direct gekoppeld is aan kosten en energiebesparing, wat de kernwaarde is voor de gebruiker.

Keuze featurevariabele

Featurevariabele: Buitentemperatuur (°C)

Uit de analyse bleek dat buitentemperatuur een sterk lineair verband heeft met energieverbruik, voornamelijk door het gebruik van verwarming en airco.

Onderbouwing

Pearson correlatie buitentemperatuur ↔ energieverbruik: r ≈ -0,99

Pearson correlatie dagnummer ↔ energieverbruik: r ≈ 0,83

De absolute correlatie met temperatuur is sterker, wat wijst op een betrouwbaardere voorspelling.

Implementatie

Lineaire regressie is zelf geïmplementeerd in Python

Gradient descent is gebruikt om de regressielijn te bepalen

Geen externe libraries gebruikt voor correlatie of regressie

De voorspelling wordt in de applicatie weergegeven als:

Verwacht energieverbruik

Verwachte kosten



"Database"

De applicatie maakt gebruik van PostgreSQL met de database micasadatabase.
Hierin wordt onder andere opgeslagen:

Dagelijks energieverbruik

Buitentemperatuur

Kosten

Historische data voor AI-analyse

De AI gebruikt deze data direct vanuit de database voor voorspellingen.



"Business IT & Management – Stakeholderanalyse"

Voor Micasa is een uitgebreide stakeholderanalyse uitgevoerd om de organisatorische context te begrijpen en waardevolle functionaliteiten te realiseren.

Belangrijkste stakeholders

Airbnb-eigenaren (direct): kostenbesparing en inzicht

Airbnb-gasten (indirect): comfort

Micasa (intern): productontwikkeling en innovatie

Leveranciers & IT-architect: technische haalbaarheid

Overheid & milieu: verduurzaming

Kwaadwillenden (hackers): beveiligingsrisico’s

De analyse is uitgewerkt volgens tien richtlijnvragen en geprioriteerd in directe, indirecte en kwaadwillende stakeholders.


"Installatie & Gebruik"
Applicatie starten

De applicatie kan worden gestart door:

Het Python-project te openen

Het hoofdscript te runnen via een Python IDE
OF

De applicatie te draaien op een Raspberry Pi

Er is geen extra configuratie nodig zolang de databaseverbinding correct is ingesteld



"Samenwerking & Versiebeheer"

Het project is ontwikkeld door een multidisciplinair team en beheerd via een gezamenlijke private GitHub-repository.
Hierin zijn:

Code

Documentatie

Versiebeheer

Samenwerking inzichtelijk vastgelegd



