"""
Django settings for nltosql project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-5e10f6uq_fzbpz&%*e*kuvk!cpe2z$t(*6k=!zd%xa#+5evu7t"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nltosql.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ['C:/Users/Anas/OneDrive/Desktop/QueryGenerator/nltosql/myapp/templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "nltosql.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

from langchain import OpenAI, LLMChain
import os
from datetime import datetime
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
import re
import sqlparse

def extract_schema(s):
    
  # extract table names from the create table statements
  table_names = re.findall(r"(TABLE +\w+ *\()", s,flags=re.IGNORECASE)
  table_names = [re.sub("table","",table_name[:-1],flags=re.IGNORECASE).strip() for table_name in table_names]
  
  # Extract column names
 
  column_pattern = re.compile(r'(\w+)\s+([\w()]+)(?:\s+PRIMARY KEY)?(?:,)?')
  columns = column_pattern.findall(s)

  columns=[c for c in columns if 'TABLE' not in c]
  table_name= ''
  columns_names=[]
  for col in columns:
      if '(' in col:
          table_name=col[0]
          continue
      else:
            columns_names.append(table_name+'.'+col[0]+' '+col[1])

 # result = []
  #for table_name, columns in table_names:
    
    
   # for column, col_type in columns_list:
    #    result.append(f'{table_name}.{column} {col_type}')
        
     
  columns_names=",".join(columns_names)
  table_names = ",".join(table_names)
  
  
  print(columns_names)
  print(table_names)  
  
  return table_names, columns_names


EXTRACT_SCHEMA = extract_schema
examples = [
    {
        "question": "Select all possible country name pairs (e.g. France-USA, FranceChina, etc.). Make sure that there are no duplicates of the type (France, USA) and (USA,France)",
        "table_name": "athletes,records,sports,nationalites",
        "description": "",
        "columns": "athletes.idAthlete, athletes.nom,athletes.prenom,athletes.dateNaissance,athletes.sexe,records.idRecords,records.idAthlete,records.idSport,records.idNationalite,records.record,records.date,records.lieu,sports.idSports,sports.sport,nationalites.idNationalite,nationalites.nationalite,nationalites.nomPays",
        "answer": '''
            SELECT N1.nomPays, N2.nomPays FROM Nationalites AS N1, Nationalites AS N2 WHERE N1.nomPays > N2.nomPays;
        ''',
    },
    {
        "question": "Who are the female athletes (idAthlete, last name, first name) of Australian nationality holding a record in a swimming event?",
         "table_name": "athletes,records,sports,nationalites",
         "description": "",
        "columns": "athletes.idAthlete, athletes.nom,athletes.prenom,athletes.dateNaissance,athletes.sexe,records.idRecords,records.idAthlete,records.idSport,records.idNationalite,records.record,records.date,records.lieu,sports.idSports,sports.sport,nationalites.idNationalite,nationalites.nationalite,nationalites.nomPays",
        "answer": " SELECT idAthlete, nom, prenom FROM ((Athletes NATURAL JOIN Records) NATURAL JOIN Sports) NATURAL JOIN Nationalites WHERE sport='Natation' AND nomPays ='Australie' AND sexe='F';",
    },
    {
        "question": "Select Surname, first name and identifier of delivery people working in a pizzeria that can accommodate at least maximum 4 deliverers and who delivers in at least two cities with more than 25,000 inhabitants",
        "table_name": "livreur,vehicule,modele,pizzeria,livraison,ville",
        "description": "",
        "columns": "livreur.idlivreur,livreur.idPizzeria,livreur.nom,livreur.prenom,livreur.ville,vehicule.idVehicule,vehicule.idPizzeria,vehicule.capacite,vehicule.modele,modele.nomModele,modele.marque,modele.puisance,pizzeria.idPizzeria,pizzeria.nomPizzeria,pizzeria.nombreLivreursMax,pizzeria.nomVille,livraison.idPizzeria,livraison.villeDesservie,ville.nonmVille,ville.codeCommune,ville.nombreHabitants",
        "answer": "SELECT nom, prenom, idLivreur FROM Livreur WHERE idPizzeria IN (SELECT idPizzeria FROM Pizzeria NATURAL JOIN Livraison JOIN Ville ON villeDesservie = Ville.nomVille WHERE nombreHabitants > 25000 AND nombreLivreursMax < 5 GROUP BY idPizzeria HAVING COUNT(villeDesservie) > 1 );",
    },
    {
        "question": "Select Pizzerias owning at least two 'Mob50' vehicles and one 'Mot125' vehicle and delivering the city of Nantes",
        "table_name": "livreur,vehicule,modele,pizzeria,livraison,ville",
        "description": "",
        "columns": "livreur.idlivreur,livreur.idPizzeria,livreur.nom,livreur.prenom,livreur.ville,vehicule.idVehicule,vehicule.idPizzeria,vehicule.capacite,vehicule.modele,modele.nomModele,modele.marque,modele.puisance,pizzeria.idPizzeria,pizzeria.nomPizzeria,pizzeria.nombreLivreursMax,pizzeria.nomVille,livraison.idPizzeria,livraison.villeDesservie,ville.nonmVille,ville.codeCommune,ville.nombreHabitants",
        "answer": "SELECT idPizzeria, nomPizzeria FROM Pizzeria NATURAL JOIN Livraison WHERE idPizzeria IN (SELECT idPizzeria FROM Vehicule WHERE modele = 'Mob50' ) AND idPizzeria IN (SELECT idPizzeria FROM Vehicule WHERE modele = 'Mot125' ) AND villeDesservie = 'Nantes';",
    },
        {
        "question": "Select Pizzerias owning at least two 'Mob50' vehicles and one 'Mot125' vehicle and delivering the city of Nantes",
        "table_name": "livreur,vehicule,modele,pizzeria,livraison,ville",
        "description": "",
        "columns": "livreur.idlivreur,livreur.idPizzeria,livreur.nom,livreur.prenom,livreur.ville,vehicule.idVehicule,vehicule.idPizzeria,vehicule.capacite,vehicule.modele,modele.nomModele,modele.marque,modele.puisance,pizzeria.idPizzeria,pizzeria.nomPizzeria,pizzeria.nombreLivreursMax,pizzeria.nomVille,livraison.idPizzeria,livraison.villeDesservie,ville.nonmVille,ville.codeCommune,ville.nombreHabitants",
        "answer": "SELECT idPizzeria, nomPizzeria FROM Pizzeria NATURAL JOIN Livraison WHERE idPizzeria IN (SELECT idPizzeria FROM Vehicule WHERE modele = 'Mob50' ) AND idPizzeria IN (SELECT idPizzeria FROM Vehicule WHERE modele = 'Mot125' ) AND villeDesservie = 'Nantes';",
    },
]

os.environ["OPENAI_API_KEY"] = "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"

llm = OpenAI(model_name="gpt-3.5-turbo", n=2)

current_time = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

_DEFAULT_TEMPLATE = """{question}\n{table_name}\n{columns}\n{description}\n{answer}"""
PROMPT = PromptTemplate(
    input_variables=["question", "table_name", "columns","description","answer"], template=_DEFAULT_TEMPLATE
)

prompt = FewShotPromptTemplate(
    examples=examples, 
    example_prompt=PROMPT,
    suffix="Question: {question}, Table: {table_name}, Columns: {columns}, description:{description}, Answer: ",
    input_variables=["question", "table_name","description", "columns"],
)

LLM_CHAIN = LLMChain(llm=llm, prompt=prompt)