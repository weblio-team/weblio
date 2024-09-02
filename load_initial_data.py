import json
from random import randint
from datetime import datetime
from django.utils.dateparse import parse_datetime


import os

### USERS

with open('initial_data/users_base.json', 'r') as file:
    data = json.load(file)

# Convert the JSON data to Django fixture format

fixture_data = []

for item in data:
    fixture_item = {
        "model": "auth.user",
        "pk": None,
        "fields": {
            "username": item["fields"].get("username")[:150],
            "password": item["fields"].get("password"),
            "email": item["fields"].get("email"),
            "is_staff": item["fields"].get("is_staff"),
            "is_superuser": item["fields"].get("is_superuser"),
            "is_active": item["fields"].get("is_active"),
            "date_joined": datetime.strptime(item["fields"].get("date_joined"), "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00Z"),
            "first_name": item["fields"].get("first_name")[:30],
            "last_name": item["fields"].get("last_name")[:150],
            "groups": [item["fields"].get("groups")]
        }
    }
    fixture_data.append(fixture_item)
    


# Write the fixture data to a new JSON file
with open('initial_data/users.json', 'w') as file:
    json.dump(fixture_data, file, indent=4)

### Members



with open('initial_data/users_base.json', 'r') as file:
    input_data = json.load(file)

# Transformation function
def transform_user_to_member(user_data):
    members = []
    for user in user_data:
        if user["model"] == "auth.user":
            fields = user["fields"]
            member = {
                "model": "members.Member",  # Adjust to your actual app label and model name
                "pk": user["pk"],
                "fields": {
                    "username": fields["username"][:150],
                    "first_name": fields["first_name"][:30],
                    "last_name": fields["last_name"][:150],
                    "email": fields["email"],
                    "is_active": fields["is_active"],
                    "is_staff": fields["is_staff"],
                    "date_joined": datetime.strptime(item["fields"].get("date_joined"), "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00Z"),  # Ensure this is in the correct format
                    # If you have a field for 'group', map it accordingly, e.g.:
                    # "group": fields["groups"],
                }
            }
            members.append(member)
    return members

# Perform transformation
transformed_data = transform_user_to_member(input_data)

# Output the transformed data
output_file = 'initial_data/members.json'
with open(output_file, 'w') as f:
    json.dump(transformed_data, f, indent=4)


### CATEGORIES

# Your input JSON data
with open('initial_data/category_base.json', 'r') as input_file:
    data = json.load(input_file)

# Fixture data preparation
fixtures = []
for item in data:
    if item["kind"] == "free": 
        precio = 0 
    else: 
        precio = item["price"]
    fixtures.append({
        "model": "posts.category",  # Replace 'yourapp' with the actual app name
        "pk": None,  # Django will auto-generate the primary key
        "fields": {
            
            "name": item["name"][:100],
            "description": item["description"][:randint(20, 99)],
            "alias": item["alias"][:2],
            "price": precio,
            "kind": item["kind"]
        }
    })



# Write to a JSON fixture file
with open('initial_data/categories.json', 'w') as file:
    json.dump(fixtures, file, indent=4)

### POSTS

# Load JSON data from a file
with open('initial_data/posts_base.json', 'r') as file:
    data = json.load(file)

# Convert the JSON data to Django fixture format
def convert_to_fixture(data):
    fixture_data = []
    
    for item in data:
        fixture_item = {
            "model": "posts.post",  # Update with your app name and model name
            "pk": item.get("id"),
            "fields": {
                "title": item.get("title")[:100],
                "title_tag": item.get("title_tag")[:100],
                "summary": item.get("summary")[:100],
                "body": item.get("body"),
                "date_posted": datetime.strptime(item.get("date_posted"), "%m/%d/%Y").strftime("%Y-%m-%dT00:00:00Z"),
                "author": item.get("author_id"),
                "status": item.get("status")[:20],
                "category": item.get("category_id"),
                "keywords": item.get("keywords")
            }
        }
        fixture_data.append(fixture_item)
    
    return fixture_data

# Convert the data
fixture_data = convert_to_fixture(data)

# Write the fixture data to a new JSON file
with open('initial_data/posts.json', 'w') as file:
    json.dump(fixture_data, file, indent=4)



# Example command: Listing files in the current directory
return_code = os.system('python manage.py loaddata initial_data/members.json')
return_code = os.system('python manage.py loaddata initial_data/categories.json')
return_code = os.system('python manage.py loaddata initial_data/posts.json')

import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weblio.settings')

# Setup Django
django.setup()

from members.models import Member
users = Member.objects.all()

from members.models import Member
for user in users:
    user.set_password("admin1234")
    user.save()
print('finished without problems')
exit()









