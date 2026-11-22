
#REAL RESTAURANTS:Business names, addresses and listing ratings are based on public listings.
#DEMO MENU:Dishes and prices are illustrative project data, not official menus.

restaurants = {
    "the-indian-curry-house": {
        "name": "The Indian Curry House",
        "cuisine": "North Indian · Chinese · Italian",
        "cuisines": ["North Indian", "Chinese", "Italian"],
        "type": "Pure Vegetarian Restaurant",
        "rating": 4.2,
        "distance": 2.1,
        "address": "366, Popular Landmark Building, Ramaswamy Circle, Chamrajpura, Mysuru, Karnataka 570004, India",
        "phone": "+91 87224 41234",
        "description": "A popular pure-vegetarian restaurant with North Indian, Indo-Chinese and Italian-style choices.",
        "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=1000&q=85",
        "menu": [
            {"name": "Paneer Butter Masala", "price": 279, "description": "Paneer in a rich tomato, butter and cashew gravy.", "category": "Main Course", "food_type": "Veg", "cuisine": "North Indian"},
            {"name": "Dal Makhani", "price": 259, "description": "Slow-cooked black lentils finished with cream and butter.", "category": "Main Course", "food_type": "Veg", "cuisine": "North Indian"},
            {"name": "Veg Dum Biryani", "price": 219, "description": "Fragrant basmati rice layered with vegetables and spices.", "category": "Rice", "food_type": "Veg", "cuisine": "North Indian"},
            {"name": "Gobi Manchurian", "price": 189, "description": "Crisp cauliflower tossed in a savoury Indo-Chinese sauce.", "category": "Starters", "food_type": "Veg", "cuisine": "Chinese"},
            {"name": "Vegetable Hakka Noodles", "price": 199, "description": "Wok-tossed noodles with vegetables and spring onion.", "category": "Noodles", "food_type": "Veg", "cuisine": "Chinese"},
            {"name": "Margherita Pizza", "price": 229, "description": "Tomato, mozzarella and basil on a crisp base.", "category": "Pizza", "food_type": "Veg", "cuisine": "Italian"},
            {"name": "Chocolate Brownie", "price": 129, "description": "A rich chocolate brownie.", "category": "Desserts", "food_type": "Veg", "cuisine": "Dessert"},
            {"name": "Fresh Lime Soda", "price": 79, "description": "Chilled lime soda, sweet or salted.", "category": "Drinks", "food_type": "Veg", "cuisine": "Beverage"}
        ]
    },

    "the-old-house": {
        "name": "The Old House",
        "cuisine": "Italian · European",
        "cuisines": ["Italian", "French", "European"],
        "type": "Cafe & Restaurant",
        "rating": 4.4,
        "distance": 3.0,
        "address": "451, RTO Circle, Jhansi Rani Lakshmi Bai Road, K.G. Koppal, Mysuru, Karnataka 570024, India",
        "phone": "+91 90088 00044",
        "description": "A heritage-bungalow cafe known for Italian and European-inspired food, coffee and desserts.",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1000&q=85",
        "menu": [
            {"name": "Margherita Wood-Fired Pizza", "price": 299, "description": "Tomato, mozzarella and basil on a wood-fired style crust.", "category": "Pizza", "food_type": "Veg", "cuisine": "Italian"},
            {"name": "Pesto Penne Pasta", "price": 279, "description": "Penne tossed in basil pesto with parmesan.", "category": "Pasta", "food_type": "Veg", "cuisine": "Italian"},
            {"name": "Mushroom Risotto", "price": 319, "description": "Creamy rice with mushrooms and herbs.", "category": "Main Course", "food_type": "Veg", "cuisine": "Italian"},
            {"name": "Grilled Chicken Panini", "price": 299, "description": "Grilled chicken, cheese and greens in toasted bread.", "category": "Sandwiches", "food_type": "Non-Veg", "cuisine": "European"},
            {"name": "Ratatouille with Toast", "price": 269, "description": "French-style slow-cooked vegetables with toasted bread.", "category": "Main Course", "food_type": "Veg", "cuisine": "French"},
            {"name": "Croque Monsieur", "price": 289, "description": "French-inspired toasted cheese sandwich with béchamel.", "category": "Sandwiches", "food_type": "Veg", "cuisine": "French"},
            {"name": "Creme Brulee", "price": 159, "description": "Vanilla custard with a crisp caramelised sugar top.", "category": "Desserts", "food_type": "Veg", "cuisine": "French"},
            {"name": "Iced Cafe Latte", "price": 139, "description": "Chilled espresso with milk over ice.", "category": "Drinks", "food_type": "Veg", "cuisine": "Beverage"}
        ]
    },

    "empire-restaurant": {
        "name": "Empire Restaurant",
        "cuisine": "Mughlai · North Indian · Chinese",
        "cuisines": ["Mughlai", "North Indian", "Chinese"],
        "type": "Restaurant",
        "rating": 3.5,
        "distance": 3.4,
        "address": "2820/1, 8th Cross, Kalidasa Road, Vani Vilas Mohalla, Mysuru, Karnataka 570002, India",
        "phone": "+91 80 4041 4141",
        "description": "A casual restaurant known for biryani, kebabs, Mughlai and North Indian dishes, with Chinese-style options.",
        "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=1000&q=85",
        "menu": [
            {"name": "Chicken Dum Biryani", "price": 259, "description": "Basmati rice cooked with chicken and aromatic spices.", "category": "Rice", "food_type": "Non-Veg", "cuisine": "Mughlai"},
            {"name": "Butter Chicken", "price": 289, "description": "Chicken in a creamy tomato gravy.", "category": "Main Course", "food_type": "Non-Veg", "cuisine": "North Indian"},
            {"name": "Chicken Seekh Kebab", "price": 249, "description": "Minced chicken kebabs seasoned with herbs and spices.", "category": "Starters", "food_type": "Non-Veg", "cuisine": "Mughlai"},
            {"name": "Fish Fry", "price": 239, "description": "Spiced fish fillet, shallow-fried until crisp.", "category": "Starters", "food_type": "Non-Veg", "cuisine": "Indian"},
            {"name": "Egg Fried Rice", "price": 199, "description": "Wok-fried rice with egg and vegetables.", "category": "Rice", "food_type": "Non-Veg", "cuisine": "Chinese"},
            {"name": "Chicken Hakka Noodles", "price": 229, "description": "Stir-fried noodles with chicken and vegetables.", "category": "Noodles", "food_type": "Non-Veg", "cuisine": "Chinese"},
            {"name": "Gulab Jamun", "price": 79, "description": "Soft milk-solid dumplings in cardamom sugar syrup.", "category": "Desserts", "food_type": "Veg", "cuisine": "Indian"},
            {"name": "Mango Lassi", "price": 99, "description": "Chilled yoghurt drink blended with mango.", "category": "Drinks", "food_type": "Veg", "cuisine": "Beverage"}
        ]
    },

    "mysore-tiffanys": {
        "name": "Mysore Tiffanys",
        "cuisine": "South Indian · North Indian",
        "cuisines": ["South Indian", "North Indian", "Chinese"],
        "type": "Pure Vegetarian Restaurant",
        "rating": 4.6,
        "distance": 2.7,
        "address": "Zoo Road, opposite Aqua World, Indira Nagar, Ittige Gudu, Mysuru, Karnataka 570010, India",
        "phone": "+91 97412 92376",
        "description": "A well-known vegetarian dining spot for South Indian tiffin favourites and broader Indian choices.",
        "image": "https://images.unsplash.com/photo-1567337710282-00832b415979?auto=format&fit=crop&w=1000&q=85",
        "menu": [
            {"name": "Mysore Masala Dosa", "price": 95, "description": "Crisp dosa with spiced potato filling and chutney.", "category": "Breakfast", "food_type": "Veg", "cuisine": "South Indian"},
            {"name": "Thatte Idli", "price": 65, "description": "Soft steamed rice cake served with chutney and sambar.", "category": "Breakfast", "food_type": "Veg", "cuisine": "South Indian"},
            {"name": "Medu Vada", "price": 60, "description": "Crisp lentil doughnut served with sambar and chutney.", "category": "Breakfast", "food_type": "Veg", "cuisine": "South Indian"},
            {"name": "South Indian Meals", "price": 180, "description": "Rice, sambar, rasam, vegetables and traditional accompaniments.", "category": "Meals", "food_type": "Veg", "cuisine": "South Indian"},
            {"name": "Paneer Tikka", "price": 219, "description": "Marinated paneer grilled with peppers and spices.", "category": "Starters", "food_type": "Veg", "cuisine": "North Indian"},
            {"name": "Veg Fried Rice", "price": 189, "description": "Wok-fried rice with vegetables and spring onion.", "category": "Rice", "food_type": "Veg", "cuisine": "Chinese"},
            {"name": "Kesari Bath", "price": 65, "description": "Semolina sweet flavoured with saffron and ghee.", "category": "Desserts", "food_type": "Veg", "cuisine": "South Indian"},
            {"name": "Filter Coffee", "price": 45, "description": "Traditional South Indian filter coffee.", "category": "Drinks", "food_type": "Veg", "cuisine": "Beverage"}
        ]
    },

    "infinit": {
        "name": "Infinit",
        "cuisine": "Indian · Chinese · Thai · Italian",
        "cuisines": ["North Indian", "South Indian", "Chinese", "Thai", "Italian", "Continental", "Korean"],
        "type": "Fine Dining Restaurant",
        "rating": 4.8,
        "distance": 3.2,
        "address": "D-29, 6th Main Road, Vani Vilas Mohalla, Mysuru, Karnataka 570002, India",
        "phone": "+91 79966 60001",
        "description": "A multi-cuisine dining destination offering Indian, Chinese, Continental, Thai and Italian-inspired dishes.",
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1000&q=85",
        "menu": [
            {"name": "Veg Manchurian", "price": 219, "description": "Vegetable dumplings tossed in a tangy Indo-Chinese sauce.", "category": "Starters", "food_type": "Veg", "cuisine": "Chinese"},
            {"name": "Chilli Chicken", "price": 269, "description": "Chicken tossed with peppers, onions and chilli sauce.", "category": "Starters", "food_type": "Non-Veg", "cuisine": "Chinese"},
            {"name": "Thai Green Curry with Rice", "price": 289, "description": "Coconut curry with vegetables served with rice.", "category": "Main Course", "food_type": "Veg", "cuisine": "Thai"},
            {"name": "Thai Basil Chicken", "price": 319, "description": "Chicken stir-fried with basil, garlic and chillies.", "category": "Main Course", "food_type": "Non-Veg", "cuisine": "Thai"},
            {"name": "Paneer Tikka Masala", "price": 279, "description": "Grilled paneer in a spiced tomato gravy.", "category": "Main Course", "food_type": "Veg", "cuisine": "North Indian"},
            {"name": "Chicken Alfredo Pasta", "price": 299, "description": "Pasta in a creamy sauce with grilled chicken.", "category": "Pasta", "food_type": "Non-Veg", "cuisine": "Italian"},
            {"name": "Korean Gochujang Tofu Bowl", "price": 269, "description": "Korean-inspired tofu bowl with rice and vegetables.", "category": "Rice Bowls", "food_type": "Veg", "cuisine": "Korean"},
            {"name": "Korean Fried Chicken", "price": 329, "description": "Crispy chicken in a sweet-spicy Korean-inspired glaze.", "category": "Starters", "food_type": "Non-Veg", "cuisine": "Korean"},
            {"name": "New York Cheesecake", "price": 169, "description": "Creamy baked cheesecake with a biscuit base.", "category": "Desserts", "food_type": "Veg", "cuisine": "Dessert"},
            {"name": "Classic Cold Coffee", "price": 149, "description": "Chilled coffee blended with milk and ice cream.", "category": "Drinks", "food_type": "Veg", "cuisine": "Beverage"}
        ]
    }
}

restaurant_tables = {
    "the-indian-curry-house": [
        {"table_id": "T1", "capacity": 2},
        {"table_id": "T2", "capacity": 4},
        {"table_id": "T3", "capacity": 4},
        {"table_id": "T4", "capacity": 6}
    ],
    "the-old-house": [
        {"table_id": "T1", "capacity": 2},
        {"table_id": "T2", "capacity": 4},
        {"table_id": "T3", "capacity": 6}
    ],
    "empire-restaurant": [
        {"table_id": "T1", "capacity": 2},
        {"table_id": "T2", "capacity": 4},
        {"table_id": "T3", "capacity": 6}
    ],
    "mysore-tiffanys": [
        {"table_id": "T1", "capacity": 2},
        {"table_id": "T2", "capacity": 4},
        {"table_id": "T3", "capacity": 6}
    ],
    "infinit": [
        {"table_id": "T1", "capacity": 2},
        {"table_id": "T2", "capacity": 4},
        {"table_id": "T3", "capacity": 6}
    ]
}
