// Структура категорий для мужчин, женщин и детей
const CATEGORIES = {
    men: {
        title: "Мужчинам",
        categories: [
            {
                name: "Все товары",
                slug: "all",
                subcategories: []
            },
            {
                name: "Распродажа",
                slug: "sale",
                subcategories: []
            },
            {
                name: "Бренды",
                slug: "brands",
                subcategories: []
            },
            {
                name: "Одежда",
                slug: "clothing",
                subcategories: [
                    "Все позиции",
                    "Брюки",
                    "Верхняя одежда",
                    "Джинсы",
                    "Майки и футболки",
                    "Нижнее белье",
                    "Пляжные шорты",
                    "Рубашки",
                    "Спортивные костюмы",
                    "Трикотаж",
                    "Худи и толстовки",
                    "Шорты"
                ]
            },
            {
                name: "Обувь",
                slug: "shoes",
                subcategories: [
                    "Все позиции",
                    "Ботинки",
                    "Кроссовки и кеды",
                    "Лоферы и мокасины",
                    "Сандалии",
                    "Туфли",
                    "Эспадрильи"
                ]
            },
            {
                name: "Сумки",
                slug: "bags",
                subcategories: [
                    "Все позиции",
                    "Портфели",
                    "Папки для документов",
                    "Деловые сумки",
                    "Поясные сумки",
                    "Рюкзаки",
                    "Дорожные сумки",
                    "Сумки через плечо",
                    "Сумки тоут"
                ]
            },
            {
                name: "Аксессуары",
                slug: "accessories",
                subcategories: [
                    "Все позиции",
                    "Головные уборы",
                    "Разное",
                    "Кольца",
                    "Кошельки и картхолдеры",
                    "Чехлы и обложки",
                    "Солнцезащитные очки",
                    "Перчатки",
                    "Ремни",
                    "Часы",
                    "Шарфы"
                ]
            },
            {
                name: "Красота",
                slug: "beauty",
                subcategories: [
                    "Все позиции",
                    "Наборы",
                    "Парфюмерия",
                    "Уход за кожей",
                    "Уход за телом"
                ]
            },
            {
                name: "Украшения",
                slug: "jewelry",
                subcategories: [
                    "Все позиции",
                    "Браслеты",
                    "Кольца",
                    "Подвески"
                ]
            }
        ]
    },
    women: {
        title: "Женщинам",
        categories: [
            {
                name: "Все товары",
                slug: "all",
                subcategories: []
            },
            {
                name: "Распродажа",
                slug: "sale",
                subcategories: []
            },
            {
                name: "Бренды",
                slug: "brands",
                subcategories: []
            },
            {
                name: "Одежда",
                slug: "clothing",
                subcategories: [
                    "Все позиции",
                    "Блузки и рубашки",
                    "Брюки",
                    "Верхняя одежда",
                    "Джинсы",
                    "Комбинезоны",
                    "Костюмы",
                    "Купальники",
                    "Майки и футболки",
                    "Нижнее белье",
                    "Платья",
                    "Спортивная одежда",
                    "Трикотаж",
                    "Худи и толстовки",
                    "Юбки"
                ]
            },
            {
                name: "Обувь",
                slug: "shoes",
                subcategories: [
                    "Все позиции",
                    "Балетки",
                    "Ботильоны",
                    "Ботинки",
                    "Кроссовки и кеды",
                    "Лоферы и мокасины",
                    "Сандалии",
                    "Сапоги",
                    "Туфли на каблуке",
                    "Слипоны",
                    "Эспадрильи"
                ]
            },
            {
                name: "Сумки",
                slug: "bags",
                subcategories: [
                    "Все позиции",
                    "Клатчи",
                    "Косметички",
                    "Поясные сумки",
                    "Рюкзаки",
                    "Дорожные сумки",
                    "Сумки через плечо",
                    "Сумки тоут",
                    "Кроссбоди",
                    "Чемоданы"
                ]
            },
            {
                name: "Аксессуары",
                slug: "accessories",
                subcategories: [
                    "Все позиции",
                    "Головные уборы",
                    "Разное",
                    "Аксессуары для волос",
                    "Кошельки и картхолдеры",
                    "Чехлы и обложки",
                    "Солнцезащитные очки",
                    "Перчатки",
                    "Ремни",
                    "Часы",
                    "Шарфы и палантины"
                ]
            },
            {
                name: "Красота",
                slug: "beauty",
                subcategories: [
                    "Все позиции",
                    "Декоративная косметика",
                    "Наборы",
                    "Парфюмерия",
                    "Уход за волосами",
                    "Уход за кожей",
                    "Уход за телом"
                ]
            },
            {
                name: "Украшения",
                slug: "jewelry",
                subcategories: [
                    "Все позиции",
                    "Браслеты",
                    "Броши",
                    "Колье",
                    "Кольца",
                    "Подвески",
                    "Серьги"
                ]
            }
        ]
    },
    kids: {
        title: "Детям",
        categories: [
            {
                name: "Все товары",
                slug: "all",
                subcategories: []
            },
            {
                name: "Распродажа",
                slug: "sale",
                subcategories: []
            },
            {
                name: "Бренды",
                slug: "brands",
                subcategories: []
            },
            {
                name: "Одежда",
                slug: "clothing",
                subcategories: [
                    "Все позиции",
                    "Брюки",
                    "Верхняя одежда",
                    "Джинсы",
                    "Комбинезоны",
                    "Купальники",
                    "Майки и футболки",
                    "Нижнее белье",
                    "Платья",
                    "Спортивная одежда",
                    "Трикотаж",
                    "Худи и толстовки",
                    "Шорты",
                    "Юбки"
                ]
            },
            {
                name: "Обувь",
                slug: "shoes",
                subcategories: [
                    "Все позиции",
                    "Балетки",
                    "Ботинки",
                    "Кроссовки и кеды",
                    "Сандалии",
                    "Сапоги",
                    "Туфли",
                    "Слипоны"
                ]
            },
            {
                name: "Сумки",
                slug: "bags",
                subcategories: [
                    "Все позиции",
                    "Детские сумочки",
                    "Рюкзаки",
                    "Спортивные сумки"
                ]
            },
            {
                name: "Аксессуары",
                slug: "accessories",
                subcategories: [
                    "Все позиции",
                    "Головные уборы",
                    "Аксессуары для волос",
                    "Игрушки",
                    "Солнцезащитные очки",
                    "Перчатки",
                    "Ремни",
                    "Часы",
                    "Шарфы"
                ]
            },
            {
                name: "Красота",
                slug: "beauty",
                subcategories: [
                    "Все позиции",
                    "Детская косметика",
                    "Уход за волосами",
                    "Уход за телом"
                ]
            },
            {
                name: "Украшения",
                slug: "jewelry",
                subcategories: [
                    "Все позиции",
                    "Браслеты",
                    "Кольца",
                    "Подвески"
                ]
            }
        ]
    }
};

// Цвета для фильтров
const COLORS = [
    { name: "Черный", value: "black", hex: "#000000" },
    { name: "Белый", value: "white", hex: "#FFFFFF" },
    { name: "Красный", value: "red", hex: "#DC2626" },
    { name: "Синий", value: "blue", hex: "#2563EB" },
    { name: "Зеленый", value: "green", hex: "#059669" },
    { name: "Желтый", value: "yellow", hex: "#D97706" },
    { name: "Розовый", value: "pink", hex: "#EC4899" },
    { name: "Фиолетовый", value: "purple", hex: "#7C3AED" },
    { name: "Коричневый", value: "brown", hex: "#92400E" },
    { name: "Серый", value: "grey", hex: "#6B7280" },
    { name: "Оранжевый", value: "orange", hex: "#EA580C" },
    { name: "Бежевый", value: "beige", hex: "#D2B48C" },
    { name: "Золотой", value: "gold", hex: "#FFD700" },
    { name: "Серебряный", value: "silver", hex: "#C0C0C0" },
    { name: "Бордовый", value: "burgundy", hex: "#800020" },
    { name: "Темно-синий", value: "navy", hex: "#1E3A8A" }
];

// Размеры для фильтров
const SIZES = {
    clothing: ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "40", "42", "44", "46", "48", "50", "52", "54"],
    shoes: ["35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46"],
    accessories: ["One Size", "S", "M", "L", "XL"]
};

// Материалы для фильтров
const MATERIALS = [
    "Хлопок",
    "Шерсть", 
    "Кашемир",
    "Шелк",
    "Лен",
    "Синтетика",
    "Кожа",
    "Замша",
    "Деним",
    "Трикотаж",
    "Мех",
    "Пластик",
    "Металл",
    "Керамика",
    "Стекло"
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