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
design-a-search-recommendation-system-for-restaurants

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
  attributes: json, # {vegan: true}  etcs
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

GET /search?q={{value}}&user_info={uuid}&user_location

where q value is going to be searched through elastic search which is reverse indexed from postgres every hour or so.

query: {
  multi_match: {
    fields: ["name^3", "small_description^2", "large_description^2", "cuisine^2"]
  }
  script_score: {
    script: {
      source: """
        double relevance = \_score,
        double rating = doc['avg_rating'].value
        double reviews = doc['num_reviews'].value
        return relavance * (rating + (reviews / 100.0))
      """
    }
  }
}

GET /search?cousines=cousine1,cousine2,&user_info={uuid}&user_location
Elsatic search to do this by name easily same thing in here # Same here...

GET /recommendation?user_info={uuid}
Elsatic search to do this by name easily same thing in here # Same here...
  - by cloest location, quad tree
  - by what they have bought before,
  - others..
