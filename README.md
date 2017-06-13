## Synopsis

A Django Database for storing genetic variants. 

## Code Example

Coming Soon!
## Motivation

VariantDB allows the following:

1) Import VCFs into a SQL database.
2) Manage Sample QC e.g store when and who performs checks.
3) Search for variants.
4) Help with variant classification.

## Installation

1) python manage.py migrate
2) python manage.py makemigrations VariantDatabase
3) python manage.py migrate
4) python manage.py createsuperuser
5) follow instructions
6) python manage.py loaddata all.json
7) python manage.py loaddata consequence.json
8) python manage.py runserver

To import data use the python manage.py import_vcf command e.g. python manage.py import_vcf [worksheet_id]  [vcf location] [sample_name]

## Requirements

``django 1.10.5``

``pysam``

``django-auditlog``

## Tests

Coming Soon!
