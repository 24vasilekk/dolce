// Структура категорий для мужчин, женщин и детей
const CATEGORIES = {
    men: {
        title: "Men",
        categories: [
            {
                name: "All Products",
                slug: "all",
                subcategories: []
            },
            {
                name: "Sale",
                slug: "sale",
                subcategories: []
            },
            {
                name: "Brands",
                slug: "brands",
                subcategories: []
            },
            {
                name: "Clothing",
                slug: "clothing",
                subcategories: [
                    "All Items",
                    "Pants",
                    "Outerwear",
                    "Jeans",
                    "T-Shirts & Tanks",
                    "Underwear & Loungewear",
                    "Swim & Beach Shorts",
                    "Shirts",
                    "Tracksuits",
                    "Knitwear",
                    "Hoodies & Sweatshirts",
                    "Shorts"
                ]
            },
            {
                name: "Shoes",
                slug: "shoes",
                subcategories: [
                    "All Items",
                    "Boots",
                    "Sneakers",
                    "Loafers & Moccasins",
                    "Sandals & Slides",
                    "Dress Shoes",
                    "Espadrilles"
                ]
            },
            {
                name: "Bags",
                slug: "bags",
                subcategories: [
                    "All Items",
                    "Briefcases",
                    "Document Holders",
                    "Portfolios",
                    "Belt Bags",
                    "Backpacks",
                    "Duffel & Travel Bags",
                    "Shoulder Bags",
                    "Tote Bags"
                ]
            },
            {
                name: "Accessories",
                slug: "accessories",
                subcategories: [
                    "All Items",
                    "Hats",
                    "Other",
                    "Home Toys",
                    "Rings",
                    "Wallets & Cardholders",
                    "Cases & Covers",
                    "Sunglasses",
                    "Gloves",
                    "Belts",
                    "Watches",
                    "Scarves"
                ]
            },
            {
                name: "Beauty",
                slug: "beauty",
                subcategories: [
                    "All Items",
                    "Sets",
                    "Fragrance",
                    "Skincare",
                    "Body Care"
                ]
            },
            {
                name: "Jewelry",
                slug: "jewelry",
                subcategories: [
                    "All Items",
                    "Bracelets",
                    "Rings",
                    "Pendants"
                ]
            }
        ]
    },
    women: {
        title: "Women",
        categories: [
            {
                name: "All Products",
                slug: "all",
                subcategories: []
            },
            {
                name: "Sale",
                slug: "sale",
                subcategories: []
            },
            {
                name: "Brands",
                slug: "brands",
                subcategories: []
            },
            {
                name: "Clothing",
                slug: "clothing",
                subcategories: [
                    "All Items",
                    "Blouses & Shirts",
                    "Pants",
                    "Outerwear",
                    "Jeans",
                    "Jumpsuits",
                    "Suits",
                    "Swimwear",
                    "T-Shirts & Tanks",
                    "Underwear & Loungewear",
                    "Dresses",
                    "Activewear",
                    "Knitwear",
                    "Hoodies & Sweatshirts",
                    "Skirts"
                ]
            },
            {
                name: "Shoes",
                slug: "shoes",
                subcategories: [
                    "All Items",
                    "Flats",
                    "Ankle Boots",
                    "Boots",
                    "Sneakers",
                    "Loafers & Moccasins",
                    "Sandals",
                    "Tall Boots",
                    "Pumps & Heels",
                    "Slides",
                    "Espadrilles"
                ]
            },
            {
                name: "Bags",
                slug: "bags",
                subcategories: [
                    "All Items",
                    "Clutches",
                    "Cosmetic Cases",
                    "Belt Bags",
                    "Backpacks",
                    "Duffel & Travel Bags",
                    "Shoulder Bags",
                    "Tote Bags",
                    "Crossbody Bags",
                    "Luggage"
                ]
            },
            {
                name: "Accessories",
                slug: "accessories",
                subcategories: [
                    "All Items",
                    "Hats",
                    "Other",
                    "Hair Accessories",
                    "Wallets & Cardholders",
                    "Cases & Covers",
                    "Sunglasses",
                    "Gloves",
                    "Belts",
                    "Watches",
                    "Scarves & Wraps"
                ]
            },
            {
                name: "Beauty",
                slug: "beauty",
                subcategories: [
                    "All Items",
                    "Makeup",
                    "Sets",
                    "Fragrance",
                    "Hair Care",
                    "Skincare",
                    "Body Care"
                ]
            },
            {
                name: "Jewelry",
                slug: "jewelry",
                subcategories: [
                    "All Items",
                    "Bracelets",
                    "Brooches",
                    "Necklaces",
                    "Rings",
                    "Pendants",
                    "Earrings"
                ]
            }
        ]
    },
    kids: {
        title: "Kids",
        categories: [
            {
                name: "All Products",
                slug: "all",
                subcategories: []
            },
            {
                name: "Sale",
                slug: "sale",
                subcategories: []
            },
            {
                name: "Brands",
                slug: "brands",
                subcategories: []
            },
            {
                name: "Clothing",
                slug: "clothing",
                subcategories: [
                    "All Items",
                    "Pants",
                    "Outerwear",
                    "Jeans",
                    "Jumpsuits",
                    "Swimwear",
                    "T-Shirts & Tanks",
                    "Underwear",
                    "Dresses",
                    "Activewear",
                    "Knitwear",
                    "Hoodies & Sweatshirts",
                    "Shorts",
                    "Skirts"
                ]
            },
            {
                name: "Shoes",
                slug: "shoes",
                subcategories: [
                    "All Items",
                    "Flats",
                    "Boots",
                    "Sneakers",
                    "Sandals",
                    "Tall Boots",
                    "Dress Shoes",
                    "Slides"
                ]
            },
            {
                name: "Bags",
                slug: "bags",
                subcategories: [
                    "All Items",
                    "Kids Bags",
                    "Backpacks",
                    "Sports Bags"
                ]
            },
            {
                name: "Accessories",
                slug: "accessories",
                subcategories: [
                    "All Items",
                    "Hats",
                    "Hair Accessories",
                    "Toys",
                    "Sunglasses",
                    "Gloves",
                    "Belts",
                    "Watches",
                    "Scarves"
                ]
            },
            {
                name: "Beauty",
                slug: "beauty",
                subcategories: [
                    "All Items",
                    "Kids Cosmetics",
                    "Hair Care",
                    "Body Care"
                ]
            },
            {
                name: "Jewelry",
                slug: "jewelry",
                subcategories: [
                    "All Items",
                    "Bracelets",
                    "Rings",
                    "Pendants"
                ]
            }
        ]
    }
};

// Цвета для фильтров
const COLORS = [
    { name: "Black", value: "black", hex: "#000000" },
    { name: "White", value: "white", hex: "#FFFFFF" },
    { name: "Red", value: "red", hex: "#DC2626" },
    { name: "Blue", value: "blue", hex: "#2563EB" },
    { name: "Green", value: "green", hex: "#059669" },
    { name: "Yellow", value: "yellow", hex: "#D97706" },
    { name: "Pink", value: "pink", hex: "#EC4899" },
    { name: "Purple", value: "purple", hex: "#7C3AED" },
    { name: "Brown", value: "brown", hex: "#92400E" },
    { name: "Grey", value: "grey", hex: "#6B7280" },
    { name: "Orange", value: "orange", hex: "#EA580C" },
    { name: "Beige", value: "beige", hex: "#D2B48C" },
    { name: "Gold", value: "gold", hex: "#FFD700" },
    { name: "Silver", value: "silver", hex: "#C0C0C0" },
    { name: "Burgundy", value: "burgundy", hex: "#800020" },
    { name: "Navy", value: "navy", hex: "#1E3A8A" }
];

// Размеры для фильтров
const SIZES = {
    clothing: ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "40", "42", "44", "46", "48", "50", "52", "54"],
    shoes: ["35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46"],
    accessories: ["One Size", "S", "M", "L", "XL"]
};

// Материалы для фильтров
const MATERIALS = [
    "Cotton",
    "Wool",
    "Cashmere",
    "Silk",
    "Linen",
    "Synthetic",
    "Leather",
    "Suede",
    "Denim",
    "Knitwear",
    "Fur",
    "Plastic",
    "Metal",
    "Ceramic",
    "Glass"
];

// Бренды для фильтров (будут заполняться динамически из базы данных)
const BRANDS = [
    "Gucci",
    "Prada",
    "Louis Vuitton",
    "Chanel",
    "Hermès",
    "Dior",
    "Balenciaga",
    "Saint Laurent",
    "Bottega Veneta",
    "Valentino",
    "Versace",
    "Armani",
    "Dolce & Gabbana",
    "Tom Ford",
    "Burberry",
    "Off-White",
    "Stone Island",
    "Moncler",
    "Nike",
    "Adidas"
];

// Экспорт для использования в основном приложении
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CATEGORIES, COLORS, SIZES, MATERIALS, BRANDS };
} else {
    window.CATEGORIES = CATEGORIES;
    window.COLORS = COLORS;
    window.SIZES = SIZES;
    window.MATERIALS = MATERIALS;
    window.BRANDS = BRANDS;
}