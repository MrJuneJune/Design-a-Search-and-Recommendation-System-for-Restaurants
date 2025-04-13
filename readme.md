# Design a Search and Recommendation System for Restaurants

## Requirements

- Users can search food, by etcs
- Users can order food
- Users get recommendataion

## What we need

- Users should be able to search food by x criteria / get recommendations.

User {
  id: uuid,
  username: whatever
  passowrd: hashed
}

Profile: {
  id: uuid,
  name,
  locations,
}

Restraunts 
{
  id: uuid,
  name: char,
  small_description: char,
  large_description: long char,
  attributes: json
  cousines: fk_id,
  locations: hash_values, (quad_treee)
  deleted: bool,
  created_at,
  updated_at,
}

Coutsines
{
  id: UUID/PK,
  name: char,
  deleted: bool,
  created_at,
  updated_at,
}

Dishes
{
  id: uuid,
  name: char,
  small_description: char,
  large_description: long char,
  cousines: fk_id,
  price: long int,
  deleted: bool,
  created_at,
  updated_at,
}


### Relationships

Restaurants OTM dishes

APIs
GET /search?restaurant_name={{name}}&user_info={uuid}&user_location

Elsatic search to do this by name easily # Fill this in for me chatgpt what the select would look like etcs.

SELECT 
GET /search?cousines=cousine1,cousine2,&user_info={uuid}&user_location
Elsatic search to do this by name easily same thing in here # Same here...

GET /recommendation?user_info={uuid}
Elsatic search to do this by name easily same thing in here # Same here...
  - by cloest location, quad tree
  - by what they have bought before,
  - others..
