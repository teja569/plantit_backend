from fastapi import APIRouter


router = APIRouter(prefix="/categories", tags=["categories"])


PLANT_CATEGORY_TREE = {
    "Plants": {
        "Fruits": {
            "Seasonal Fruits": ["Mango", "Watermelon", "Litchi", "Papaya", "Guava"],
            "Non-Seasonal Fruits": ["Banana", "Apple", "Orange", "Grapes", "Pomegranate"],
            "By-products": ["Jams & Jellies", "Dried Fruits", "Juices", "Fruit Powders"],
        },
        "Vegetables": {
            "Leafy": ["Spinach", "Mint", "Coriander", "Fenugreek"],
            "Root": ["Carrot", "Beetroot", "Potato", "Radish"],
            "Seasonal": ["Pumpkin", "Cucumber", "Tomato", "Brinjal"],
            "By-products": ["Pickles", "Dried Veg Mixes", "Vegetable Powders", "Sauces"],
        },
        "Herbs": {
            "Medicinal": ["Tulsi", "Aloe Vera", "Neem", "Ashwagandha"],
            "Culinary": ["Basil", "Rosemary", "Thyme", "Oregano"],
            "By-products": ["Herbal Oils", "Herbal Powders", "Dried Herb Mixes", "Herbal Teas"],
        },
        "Flowers": {
            "Garden": ["Rose", "Jasmine", "Marigold", "Sunflower"],
            "Decorative": ["Orchid", "Lily", "Chrysanthemum"],
            "By-products": ["Essential Oils", "Dried Petals", "Perfume Extracts", "Flower Powders"],
        },
        "Roots & Ayurvedic": {
            "Main Roots": ["Ginger", "Turmeric", "Garlic", "Ginseng"],
            "By-products": ["Dried Roots", "Herbal Extracts", "Powders", "Medicinal Oils"],
        },
        "Ornamental & Indoor": {
            "Indoor": ["Money Plant", "Snake Plant", "Peace Lily", "Areca Palm"],
            "Outdoor": ["Bonsai", "Cactus", "Croton", "Hibiscus"],
            "By-products": ["Pots & Planters", "Compost & Soil Mix", "Fertilizers", "Seeds"],
        },
    }
}


@router.get("/tree")
async def get_category_tree():
    return PLANT_CATEGORY_TREE


