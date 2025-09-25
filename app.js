// Dolce Deals Fashion App - Обновленная версия с улучшенным модальным окном
class FashionApp {
    constructor() {
        this.currentTab = 'home';
        this.currentGender = null;
        this.currentCategory = null;
        this.currentSubcategory = null;
        this.currentProduct = null;
        this.products = [];
        this.filteredProducts = [];
        this.favorites = new Set();
        this.filters = {
            brands: new Set(),
            colors: new Set(),
            sizes: new Set(),
            materials: new Set(),
            onSale: false
        };
        this.sortBy = 'name';
        this.searchQuery = '';
        this.currentPage = 1;
        this.itemsPerPage = 20;
        
        this.init();
    }

    async init() {
        await this.loadProducts();
        this.loadFavorites();
        this.setupEventListeners();
        this.hideLoadingScreen();
        this.updateUserInfo();
    }

    // Загрузка товаров из JSON файла
    async loadProducts() {
        try {
            const response = await fetch('data/products.json');
            if (!response.ok) {
                throw new Error('Не удалось загрузить товары');
            }
            this.products = await response.json();
            console.log('Загружено товаров:', this.products.length);
        } catch (error) {
            console.error('Ошибка загрузки товаров:', error);
            // Если не удалось загрузить, используем тестовые данные
            this.products = this.getExampleProducts();
        }
    }

    // Тестовые товары (на случай, если JSON не загрузится)
    getExampleProducts() {
        return [
            {
                id: 1,
                name: "Кроссовки Air Max 270",
                brand: "Nike",
                price: 12990,
                image: "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
                gender: "men",
                category: "shoes",
                subcategory: "Кроссовки и кеды",
                colors: ["black", "white"],
                sizes: ["40", "41", "42", "43", "44"],
                materials: ["Синтетика"],
                onSale: false,
                description: "Удобные кроссовки для повседневной носки"
            }
        ];
    }

    // Настройка обработчиков событий
    setupEventListeners() {
        // Навигация по табам
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });

        // Кнопки выбора пола
        document.querySelectorAll('.gender-card').forEach(btn => {
            btn.addEventListener('click', () => this.openCategories(btn.dataset.gender));
        });

        // Модальные окна
        const closeButtons = document.querySelectorAll('#closeCategories, #closeSearch, #closeFilter, #closeProductDetail');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.closeAllModals());
        });

        // Поиск - множественные кнопки
        const searchBtns = document.querySelectorAll('.header-search-btn, #headerSearchBtn, #productsSearchBtn, #favoritesSearchBtn');
        searchBtns.forEach(btn => {
            btn.addEventListener('click', () => this.openSearch());
        });
        
        if (document.getElementById('searchBtn')) {
            document.getElementById('searchBtn').addEventListener('click', () => this.performSearch());
        }
        
        if (document.getElementById('searchInput')) {
            document.getElementById('searchInput').addEventListener('input', (e) => this.handleSearchInput(e));
        }

        // Сортировка
        if (document.getElementById('sortButton')) {
            document.getElementById('sortButton').addEventListener('click', () => this.toggleSortDropdown());
        }

        // Опции сортировки
        document.querySelectorAll('.sort-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const sortValue = e.target.dataset.sort;
                this.setSorting(sortValue);
                this.closeSortDropdown();
            });
        });

        // Фильтры
        if (document.getElementById('openFilters')) {
            document.getElementById('openFilters').addEventListener('click', () => this.openFilters());
        }
        if (document.getElementById('clearFilters')) {
            document.getElementById('clearFilters').addEventListener('click', () => this.clearFilters());
        }
        if (document.getElementById('applyFilters')) {
            document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());
        }

        // Кнопка назад
        if (document.getElementById('backBtn')) {
            document.getElementById('backBtn').addEventListener('click', () => this.goBack());
        }

        // Загрузка файла
        if (document.getElementById('fileUpload')) {
            document.getElementById('fileUpload').addEventListener('change', (e) => this.handleFileUpload(e));
        }

        // Связаться с поддержкой
        if (document.getElementById('contactSupport')) {
            document.getElementById('contactSupport').addEventListener('click', () => this.contactSupport());
        }

        // Загрузить еще
        if (document.getElementById('loadMore')) {
            document.getElementById('loadMore').addEventListener('click', () => this.loadMore());
        }

        // Product Detail Modal - обновленные обработчики
        if (document.getElementById('productDetailFavorite')) {
            document.getElementById('productDetailFavorite').addEventListener('click', () => {
                if (this.currentProduct) {
                    this.toggleFavorite(this.currentProduct.id);
                }
            });
        }

        if (document.getElementById('productDetailBuy')) {
            document.getElementById('productDetailBuy').addEventListener('click', () => {
                if (this.currentProduct) {
                    this.buyProduct(this.currentProduct);
                }
            });
        }

        if (document.getElementById('productDetailShare')) {
            document.getElementById('productDetailShare').addEventListener('click', () => {
                if (this.currentProduct) {
                    this.shareProduct(this.currentProduct);
                }
            });
        }

        // Закрытие модальных окон и выпадающих меню по клику вне
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') || e.target.classList.contains('product-detail-modal')) {
                this.closeAllModals();
            }
            
            // Закрытие выпадающего меню сортировки
            if (!e.target.closest('.sort-dropdown')) {
                this.closeSortDropdown();
            }
        });

        // Обработка клавиши Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
                this.closeSortDropdown();
            }
        });
    }

    // Переключение табов
    switchTab(tab) {
        // Скрыть все табы
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Убрать активный класс с кнопок навигации
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Показать выбранный таб
        document.getElementById(`${tab}Tab`).classList.add('active');
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        this.currentTab = tab;

        // Обновить содержимое табов
        if (tab === 'favorites') {
            this.updateFavoritesTab();
        }
    }

    // Сортировка
    toggleSortDropdown() {
        const dropdown = document.getElementById('sortDropdown');
        const button = document.getElementById('sortButton');
        
        if (dropdown && button) {
            const isOpen = !dropdown.classList.contains('hidden');
            
            if (isOpen) {
                this.closeSortDropdown();
            } else {
                dropdown.classList.remove('hidden');
                button.classList.add('active');
            }
        }
    }

    closeSortDropdown() {
        const dropdown = document.getElementById('sortDropdown');
        const button = document.getElementById('sortButton');
        
        if (dropdown && button) {
            dropdown.classList.add('hidden');
            button.classList.remove('active');
        }
    }

    setSorting(sortBy) {
        this.sortBy = sortBy;
        
        // Обновить текст кнопки сортировки
        const sortLabel = document.getElementById('sortLabel');
        const sortOptions = {
            'name': 'Название А-Я',
            'price-asc': 'Цена: по возрастанию',
            'price-desc': 'Цена: по убыванию',
            'brand': 'Бренд А-Я'
        };
        
        if (sortLabel) {
            sortLabel.textContent = sortOptions[sortBy] || 'Сортировка';
        }
        
        // Обновить активный пункт в выпадающем меню
        document.querySelectorAll('.sort-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.sort === sortBy) {
                option.classList.add('active');
            }
        });
        
        this.sortProducts();
        this.renderProducts();
    }

    // Открытие категорий
    openCategories(gender) {
        this.currentGender = gender;
        const categoriesData = CATEGORIES[gender];
        
        document.getElementById('categoriesTitle').textContent = categoriesData.title;
        
        const categoriesList = document.getElementById('categoriesList');
        categoriesList.innerHTML = '';

        categoriesData.categories.forEach(category => {
            const categoryBtn = document.createElement('button');
            categoryBtn.className = 'category-item';
            categoryBtn.textContent = category.name;
            categoryBtn.addEventListener('click', () => this.selectCategory(category));
            categoriesList.appendChild(categoryBtn);
        });

        document.getElementById('categoriesModal').classList.remove('hidden');
    }

    // Выбор категории
    selectCategory(category) {
        this.currentCategory = category;
        this.currentSubcategory = null;
        this.closeCategories();

        if (category.subcategories && category.subcategories.length > 0) {
            this.openSubcategories(category);
        } else {
            this.showProducts();
        }
    }

    // Открытие подкатегорий
    openSubcategories(category) {
        document.getElementById('categoriesTitle').textContent = category.name;
        
        const categoriesList = document.getElementById('categoriesList');
        categoriesList.innerHTML = '';

        category.subcategories.forEach(subcategory => {
            const subcategoryBtn = document.createElement('button');
            subcategoryBtn.className = 'category-item';
            subcategoryBtn.textContent = subcategory;
            subcategoryBtn.addEventListener('click', () => {
                this.currentSubcategory = subcategory;
                this.closeCategories();
                this.showProducts();
            });
            categoriesList.appendChild(subcategoryBtn);
        });

        document.getElementById('categoriesModal').classList.remove('hidden');
    }

    // Показать товары
    showProducts() {
        this.switchTab('products');
        this.updateProductsTitle();
        this.filterProducts();
        this.renderProducts();
    }

    // Обновление заголовка товаров
    updateProductsTitle() {
        let title = '';
        if (this.currentGender) {
            title += CATEGORIES[this.currentGender].title;
        }
        if (this.currentCategory) {
            title += ` - ${this.currentCategory.name}`;
        }
        if (this.currentSubcategory && this.currentSubcategory !== 'Все позиции') {
            title += ` - ${this.currentSubcategory}`;
        }
        document.getElementById('productsTitle').textContent = title || 'Товары';
    }

    // Фильтрация товаров
    filterProducts() {
        this.filteredProducts = this.products.filter(product => {
            // Фильтр по полу
            if (this.currentGender && product.gender !== this.currentGender) {
                return false;
            }

            // Фильтр по категории
            if (this.currentCategory && this.currentCategory.slug !== 'all' && this.currentCategory.slug !== 'sale' && this.currentCategory.slug !== 'brands') {
                if (product.category !== this.currentCategory.slug) {
                    return false;
                }
            }

            // Фильтр по подкатегории
            if (this.currentSubcategory && this.currentSubcategory !== 'Все позиции') {
                if (product.subcategory !== this.currentSubcategory) {
                    return false;
                }
            }

            // Фильтр по распродаже
            if (this.currentCategory && this.currentCategory.slug === 'sale' && !product.onSale) {
                return false;
            }

            // Фильтр по поиску
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                if (!product.name.toLowerCase().includes(query) &&
                    !product.brand.toLowerCase().includes(query) &&
                    !product.description.toLowerCase().includes(query)) {
                    return false;
                }
            }

            // Фильтры
            if (this.filters.brands.size > 0 && !this.filters.brands.has(product.brand)) {
                return false;
            }

            if (this.filters.colors.size > 0) {
                const hasMatchingColor = product.colors.some(color => this.filters.colors.has(color));
                if (!hasMatchingColor) {
                    return false;
                }
            }

            if (this.filters.sizes.size > 0) {
                const hasMatchingSize = product.sizes.some(size => this.filters.sizes.has(size));
                if (!hasMatchingSize) {
                    return false;
                }
            }

            if (this.filters.materials.size > 0) {
                const hasMatchingMaterial = product.materials.some(material => this.filters.materials.has(material));
                if (!hasMatchingMaterial) {
                    return false;
                }
            }

            if (this.filters.onSale && !product.onSale) {
                return false;
            }

            return true;
        });

        this.sortProducts();
    }

    // Сортировка товаров
    sortProducts() {
        this.filteredProducts.sort((a, b) => {
            switch (this.sortBy) {
                case 'price-asc':
                    return (a.onSale ? a.salePrice : a.price) - (b.onSale ? b.salePrice : b.price);
                case 'price-desc':
                    return (b.onSale ? b.salePrice : b.price) - (a.onSale ? a.salePrice : a.price);
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'brand':
                    return a.brand.localeCompare(b.brand);
                default:
                    return 0;
            }
        });
    }

    // Отрисовка товаров
    renderProducts() {
        const grid = document.getElementById('productsGrid');
        const loadMoreBtn = document.getElementById('loadMore');
        const activeFilters = document.getElementById('activeFilters');

        if (!grid) return;

        // Показать/скрыть активные фильтры
        if (activeFilters) {
            if (this.hasActiveFilters()) {
                activeFilters.classList.remove('hidden');
                this.renderActiveFilters();
            } else {
                activeFilters.classList.add('hidden');
            }
        }

        // Рассчитать товары для текущей страницы
        const startIndex = 0;
        const endIndex = this.currentPage * this.itemsPerPage;
        const productsToShow = this.filteredProducts.slice(startIndex, endIndex);

        // Очистить сетку
        grid.innerHTML = '';

        if (productsToShow.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <div class="empty-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                    </div>
                    <h3>Товары не найдены</h3>
                    <p>Попробуйте изменить фильтры или выбрать другую категорию</p>
                </div>
            `;
            if (loadMoreBtn) loadMoreBtn.classList.add('hidden');
            return;
        }

        // Отрисовать товары
        productsToShow.forEach(product => {
            const productCard = this.createProductCard(product);
            grid.appendChild(productCard);
        });

        // Показать/скрыть кнопку "Загрузить еще"
        if (loadMoreBtn) {
            if (endIndex < this.filteredProducts.length) {
                loadMoreBtn.classList.remove('hidden');
            } else {
                loadMoreBtn.classList.add('hidden');
            }
        }
    }

    // Создание карточки товара
    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card';

        const price = product.onSale ? product.salePrice : product.price;
        const originalPrice = product.onSale ? product.price : null;
        const isLiked = this.favorites.has(product.id);

        card.innerHTML = `
            <div class="product-image-container">
                <img src="${product.image}" alt="${product.name}" class="product-image" loading="lazy">
                <button class="like-btn ${isLiked ? 'liked' : ''}" data-product-id="${product.id}">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="${isLiked ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                </button>
            </div>
            <div class="product-info">
                <div class="product-brand">${product.brand}</div>
                <div class="product-name">${product.name}</div>
                <div class="product-price">
                    ${this.formatPrice(price)}
                    ${originalPrice ? `<span class="product-original-price">${this.formatPrice(originalPrice)}</span>` : ''}
                </div>
                <div class="product-sizes">Размеры: ${product.sizes.join(', ')}</div>
            </div>
        `;

        // Обработчик лайка
        const likeBtn = card.querySelector('.like-btn');
        likeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleFavorite(product.id);
        });

        // Обработчик клика по карточке
        card.addEventListener('click', () => {
            this.openProductDetail(product);
        });

        return card;
    }

    // ОБНОВЛЕННОЕ ОТКРЫТИЕ ДЕТАЛЬНОГО ПРОСМОТРА ТОВАРА
    openProductDetail(product) {
        this.currentProduct = product;
        
        // Заполнение информации о товаре
        document.getElementById('productDetailImage').src = product.image;
        document.getElementById('productDetailImage').alt = product.name;
        document.getElementById('productDetailBrand').textContent = product.brand;
        document.getElementById('productDetailName').textContent = product.name;
        document.getElementById('productDetailDescription').textContent = product.description || 'Описание товара будет добавлено позже.';
        
        // Цена с улучшенным форматированием
        const priceEl = document.getElementById('productDetailPrice');
        const price = product.onSale ? product.salePrice : product.price;
        const originalPrice = product.onSale ? product.price : null;
        
        let priceHtml = this.formatPrice(price);
        
        if (originalPrice) {
            const discount = Math.round(((originalPrice - price) / originalPrice) * 100);
            priceHtml += `<span class="product-detail-original-price">${this.formatPrice(originalPrice)}</span>`;
            priceHtml += `<span class="product-detail-sale-badge">-${discount}%</span>`;
        }
        
        priceEl.innerHTML = priceHtml;
        
        // Размеры с улучшенным интерфейсом
        this.renderProductSizes(product);
        
        // Характеристики товара
        this.renderProductSpecs(product);
        
        // Кнопка избранного
        const favoriteBtn = document.getElementById('productDetailFavorite');
        const isLiked = this.favorites.has(product.id);
        favoriteBtn.classList.toggle('liked', isLiked);
        const favoriteSvg = favoriteBtn.querySelector('svg');
        if (favoriteSvg) {
            favoriteSvg.setAttribute('fill', isLiked ? 'currentColor' : 'none');
        }
        
        // Показать похожие товары
        this.renderSimilarProducts(product);
        
        // Показать модальное окно
        document.getElementById('productDetailModal').classList.remove('hidden');
    }

    // Отрисовка размеров товара
    renderProductSizes(product) {
        const sizesContainer = document.getElementById('productDetailSizes');
        sizesContainer.innerHTML = '';
        
        product.sizes.forEach(size => {
            const sizeBtn = document.createElement('button');
            sizeBtn.className = 'size-option';
            sizeBtn.textContent = size;
            sizeBtn.addEventListener('click', () => {
                sizesContainer.querySelectorAll('.size-option').forEach(btn => btn.classList.remove('selected'));
                sizeBtn.classList.add('selected');
            });
            sizesContainer.appendChild(sizeBtn);
        });
    }

    // Отрисовка характеристик товара
    renderProductSpecs(product) {
        const specsContainer = document.getElementById('productDetailSpecs');
        specsContainer.innerHTML = '';

        // Материалы
        if (product.materials && product.materials.length > 0) {
            const materialSpec = this.createSpecItem('Материал', product.materials.join(', '));
            specsContainer.appendChild(materialSpec);
        }

        // Цвета
        if (product.colors && product.colors.length > 0) {
            const colorSpec = document.createElement('div');
            colorSpec.className = 'spec-item';
            colorSpec.innerHTML = `
                <span class="spec-label">Цвета</span>
                <div class="spec-value">
                    <div class="color-swatches">
                        ${product.colors.map(color => {
                            const colorData = COLORS.find(c => c.value === color);
                            const colorHex = colorData ? colorData.hex : '#' + color;
                            return `<div class="color-swatch" style="background: ${colorHex};" title="${colorData ? colorData.name : color}"></div>`;
                        }).join('')}
                    </div>
                </div>
            `;
            specsContainer.appendChild(colorSpec);
        }

        // Артикул
        const articleSpec = this.createSpecItem('Артикул', `${product.brand.substring(0, 2).toUpperCase()}-${product.id.toString().padStart(6, '0')}`);
        specsContainer.appendChild(articleSpec);

        // Коллекция/Категория
        if (product.subcategory) {
            const categorySpec = this.createSpecItem('Коллекция', product.subcategory);
            specsContainer.appendChild(categorySpec);
        }
    }

    // Создание элемента характеристики
    createSpecItem(label, value) {
        const specItem = document.createElement('div');
        specItem.className = 'spec-item';
        specItem.innerHTML = `
            <span class="spec-label">${label}</span>
            <span class="spec-value">${value}</span>
        `;
        return specItem;
    }

    // Отображение похожих товаров (улучшенная версия)
    renderSimilarProducts(currentProduct) {
        const container = document.getElementById('similarProductsGrid');
        container.innerHTML = '';
        
        // Найти похожие товары
        let similarProducts = this.findSimilarProducts(currentProduct);
        
        // Ограничить до 4 товаров
        similarProducts = similarProducts.slice(0, 4);
        
        if (similarProducts.length === 0) {
            // Если похожих товаров нет, показать случайные из той же категории
            similarProducts = this.products
                .filter(p => p.id !== currentProduct.id && p.gender === currentProduct.gender)
                .slice(0, 4);
        }
        
        similarProducts.forEach(product => {
            const similarCard = document.createElement('div');
            similarCard.className = 'similar-product-card';
            
            const price = product.onSale ? product.salePrice : product.price;
            
            similarCard.innerHTML = `
                <img src="${product.image}" alt="${product.name}" class="similar-product-image" loading="lazy">
                <div class="similar-product-info">
                    <div class="similar-product-brand">${product.brand}</div>
                    <div class="similar-product-name">${product.name}</div>
                    <div class="similar-product-price">${this.formatPrice(price)}</div>
                </div>
            `;
            
            similarCard.addEventListener('click', () => {
                this.openProductDetail(product);
            });
            
            container.appendChild(similarCard);
        });
    }

    // Поиск похожих товаров (улучшенный алгоритм)
    findSimilarProducts(currentProduct) {
        const allProducts = this.products.filter(p => p.id !== currentProduct.id);
        
        // Приоритет 1: Тот же бренд и схожее название
        const sameBrandSimilarName = allProducts.filter(p => 
            p.brand === currentProduct.brand && 
            p.gender === currentProduct.gender &&
            this.isSimilarName(p.name, currentProduct.name)
        );
        
        if (sameBrandSimilarName.length >= 4) {
            return sameBrandSimilarName;
        }
        
        // Приоритет 2: Та же категория и подкатегория
        const sameCategorySubcategory = allProducts.filter(p => 
            p.category === currentProduct.category && 
            p.subcategory === currentProduct.subcategory &&
            p.gender === currentProduct.gender
        );
        
        // Приоритет 3: Тот же бренд
        const sameBrand = allProducts.filter(p => 
            p.brand === currentProduct.brand &&
            p.gender === currentProduct.gender
        );
        
        // Объединить результаты
        const combined = [...sameBrandSimilarName, ...sameCategorySubcategory, ...sameBrand];
        const unique = combined.filter((product, index, self) => 
            index === self.findIndex(p => p.id === product.id)
        );
        
        if (unique.length >= 4) {
            return unique;
        }
        
        // Приоритет 4: Та же категория
        const sameCategory = allProducts.filter(p => 
            p.category === currentProduct.category &&
            p.gender === currentProduct.gender
        );
        
        const finalCombined = [...unique, ...sameCategory];
        return finalCombined.filter((product, index, self) => 
            index === self.findIndex(p => p.id === product.id)
        );
    }

    // Проверка схожести названий (улучшенная версия)
    isSimilarName(name1, name2) {
        const words1 = name1.toLowerCase().split(' ');
        const words2 = name2.toLowerCase().split(' ');
        
        // Проверить, есть ли общие слова
        const commonWords = words1.filter(word => words2.includes(word));
        
        // Считать похожими, если есть минимум 2 общих слова или 1 слово длиннее 4 символов
        return commonWords.length >= 2 || commonWords.some(word => word.length > 4);
    }

    // НОВАЯ ФУНКЦИЯ: Поделиться товаром
    shareProduct(product) {
        const shareData = {
            title: `${product.brand} - ${product.name}`,
            text: `Посмотри на этот товар в Dolce Deals: ${product.name} от ${product.brand}`,
            url: window.location.href
        };

        if (navigator.share) {
            // Если поддерживается нативное API поделиться
            navigator.share(shareData).catch(console.error);
        } else if (navigator.clipboard) {
            // Копируем ссылку в буфер обмена
            const shareText = `${shareData.title}\n${shareData.text}\n${shareData.url}`;
            navigator.clipboard.writeText(shareText).then(() => {
                // Показать уведомление
                this.showNotification('Ссылка скопирована в буфер обмена');
            }).catch(console.error);
        } else {
            // Fallback для старых браузеров
            const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(shareData.url)}&text=${encodeURIComponent(shareData.text)}`;
            window.open(shareUrl, '_blank');
        }
    }

    // НОВАЯ ФУНКЦИЯ: Показать уведомление
    showNotification(message) {
        // Создаем простое уведомление
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #000;
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            z-index: 10000;
            font-size: 0.9rem;
            animation: fadeInOut 2s ease-in-out forwards;
        `;

        // Добавляем стили анимации
        if (!document.getElementById('notificationStyles')) {
            const style = document.createElement('style');
            style.id = 'notificationStyles';
            style.textContent = `
                @keyframes fadeInOut {
                    0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                    20%, 80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                    100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Удаляем уведомление через 2 секунды
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 2000);
    }

    // Покупка товара (улучшенная версия)
    buyProduct(product) {
        const selectedSize = document.querySelector('.size-option.selected');
        
        if (!selectedSize) {
            this.showNotification('Пожалуйста, выберите размер');
            return;
        }
        
        const price = product.onSale ? product.salePrice : product.price;
        const message = `🛍️ *НОВЫЙ ЗАКАЗ*\n\n` +
                       `📦 *Товар:* ${product.brand} - ${product.name}\n` +
                       `💰 *Цена:* ${this.formatPrice(price)}\n` +
                       `📏 *Размер:* ${selectedSize.textContent}\n` +
                       `🆔 *Артикул:* ${product.brand.substring(0, 2).toUpperCase()}-${product.id.toString().padStart(6, '0')}\n` +
                       `🔗 *Изображение:* ${product.image}\n\n` +
                       `Пожалуйста, подтвердите заказ и сообщите детали доставки.`;
        
        const encodedMessage = encodeURIComponent(message);
        const telegramUrl = `https://t.me/dolcedeals_manager?text=${encodedMessage}`;
        
        // Анимация кнопки покупки
        const buyBtn = document.getElementById('productDetailBuy');
        buyBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            buyBtn.style.transform = '';
            window.open(telegramUrl, '_blank');
        }, 150);
    }

    // Закрытие модального окна товара
    closeProductDetail() {
        document.getElementById('productDetailModal').classList.add('hidden');
        this.currentProduct = null;
    }

    // Форматирование цены
    formatPrice(price) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0
        }).format(price);
    }

    // Переключение избранного
    toggleFavorite(productId) {
        if (this.favorites.has(productId)) {
            this.favorites.delete(productId);
        } else {
            this.favorites.add(productId);
        }
        
        this.saveFavorites();
        this.updateFavoriteButtons();
        
        // Обновить кнопку в модальном окне, если товар открыт
        if (this.currentProduct && this.currentProduct.id === productId) {
            const favoriteBtn = document.getElementById('productDetailFavorite');
            const isLiked = this.favorites.has(productId);
            favoriteBtn.classList.toggle('liked', isLiked);
            const favoriteSvg = favoriteBtn.querySelector('svg');
            if (favoriteSvg) {
                favoriteSvg.setAttribute('fill', isLiked ? 'currentColor' : 'none');
            }
        }
        
        if (this.currentTab === 'favorites') {
            this.updateFavoritesTab();
        }
    }

    // Обновление кнопок избранного
    updateFavoriteButtons() {
        document.querySelectorAll('.like-btn').forEach(btn => {
            const productId = parseInt(btn.dataset.productId);
            const isLiked = this.favorites.has(productId);
            const svg = btn.querySelector('svg');
            
            btn.classList.toggle('liked', isLiked);
            if (svg) {
                svg.setAttribute('fill', isLiked ? 'currentColor' : 'none');
            }
        });
    }

    // Поиск
    openSearch() {
        const searchModal = document.getElementById('searchModal');
        if (searchModal) {
            searchModal.classList.remove('hidden');
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
    }

    closeSearch() {
        const searchModal = document.getElementById('searchModal');
        if (searchModal) {
            searchModal.classList.add('hidden');
        }
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            searchResults.innerHTML = '';
        }
    }

    handleSearchInput(e) {
        const query = e.target.value.trim();
        if (query.length > 2) {
            this.showSearchResults(query);
        } else {
            const searchResults = document.getElementById('searchResults');
            if (searchResults) {
                searchResults.innerHTML = '';
            }
        }
    }

    performSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            this.searchQuery = searchInput.value.trim();
        }
        this.closeSearch();
        this.currentPage = 1;
        this.filterProducts();
        this.renderProducts();
        
        if (this.currentTab !== 'products') {
            this.switchTab('products');
        }
    }

    showSearchResults(query) {
        const results = this.products.filter(product => 
            product.name.toLowerCase().includes(query.toLowerCase()) ||
            product.brand.toLowerCase().includes(query.toLowerCase()) ||
            product.description.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);

        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';

        results.forEach(product => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.innerHTML = `
                <img src="${product.image}" alt="${product.name}" class="search-result-image">
                <div class="search-result-info">
                    <div class="search-result-name">${product.name}</div>
                    <div class="search-result-brand">${product.brand}</div>
                    <div class="search-result-price">${this.formatPrice(product.onSale ? product.salePrice : product.price)}</div>
                </div>
            `;
            
            resultItem.addEventListener('click', () => {
                this.closeSearch();
                this.openProductDetail(product);
            });
            
            resultsContainer.appendChild(resultItem);
        });
    }

    // Фильтры
    openFilters() {
        this.renderFilterOptions();
        const filterModal = document.getElementById('filterModal');
        if (filterModal) {
            filterModal.classList.remove('hidden');
        }
    }

    closeFilter() {
        const filterModal = document.getElementById('filterModal');
        if (filterModal) {
            filterModal.classList.add('hidden');
        }
    }

    renderFilterOptions() {
        // Бренды
        const brandFilters = document.getElementById('brandFilters');
        if (brandFilters) {
            brandFilters.innerHTML = '';
            const availableBrands = [...new Set(this.products.map(p => p.brand))].sort();
            
            availableBrands.forEach(brand => {
                const label = document.createElement('label');
                label.className = 'filter-checkbox';
                label.innerHTML = `
                    <input type="checkbox" value="${brand}" ${this.filters.brands.has(brand) ? 'checked' : ''}>
                    <span class="checkmark"></span>
                    <span>${brand}</span>
                `;
                brandFilters.appendChild(label);
            });
        }

        // Цвета
        const colorFilters = document.getElementById('colorFilters');
        if (colorFilters) {
            colorFilters.innerHTML = '';
            
            COLORS.forEach(color => {
                const colorBtn = document.createElement('button');
                colorBtn.className = `color-filter ${this.filters.colors.has(color.value) ? 'active' : ''}`;
                colorBtn.style.setProperty('--color', color.hex);
                colorBtn.dataset.color = color.value;
                colorBtn.title = color.name;
                colorFilters.appendChild(colorBtn);
            });
        }

        // Размеры
        const sizeFilters = document.getElementById('sizeFilters');
        if (sizeFilters) {
            sizeFilters.innerHTML = '';
            const availableSizes = [...new Set(this.products.flatMap(p => p.sizes))].sort();
            
            availableSizes.forEach(size => {
                const sizeBtn = document.createElement('button');
                sizeBtn.className = `size-filter ${this.filters.sizes.has(size) ? 'active' : ''}`;
                sizeBtn.textContent = size;
                sizeBtn.dataset.size = size;
                sizeFilters.appendChild(sizeBtn);
            });
        }

        // Материалы
        const materialFilters = document.getElementById('materialFilters');
        if (materialFilters) {
            materialFilters.innerHTML = '';
            const availableMaterials = [...new Set(this.products.flatMap(p => p.materials))].sort();
            
            availableMaterials.forEach(material => {
                const label = document.createElement('label');
                label.className = 'filter-checkbox';
                label.innerHTML = `
                    <input type="checkbox" value="${material}" ${this.filters.materials.has(material) ? 'checked' : ''}>
                    <span class="checkmark"></span>
                    <span>${material}</span>
                `;
                materialFilters.appendChild(label);
            });
        }

        // Специальные фильтры
        const saleFilter = document.getElementById('saleFilter');
        if (saleFilter) {
            saleFilter.checked = this.filters.onSale;
        }

        // Обработчики событий для фильтров
        this.setupFilterEventListeners();
    }

    setupFilterEventListeners() {
        // Бренды
        const brandFilters = document.getElementById('brandFilters');
        if (brandFilters) {
            brandFilters.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    if (e.target.checked) {
                        this.filters.brands.add(e.target.value);
                    } else {
                        this.filters.brands.delete(e.target.value);
                    }
                }
            });
        }

        // Цвета
        const colorFilters = document.getElementById('colorFilters');
        if (colorFilters) {
            colorFilters.addEventListener('click', (e) => {
                if (e.target.classList.contains('color-filter')) {
                    const color = e.target.dataset.color;
                    if (this.filters.colors.has(color)) {
                        this.filters.colors.delete(color);
                        e.target.classList.remove('active');
                    } else {
                        this.filters.colors.add(color);
                        e.target.classList.add('active');
                    }
                }
            });
        }

        // Размеры
        const sizeFilters = document.getElementById('sizeFilters');
        if (sizeFilters) {
            sizeFilters.addEventListener('click', (e) => {
                if (e.target.classList.contains('size-filter')) {
                    const size = e.target.dataset.size;
                    if (this.filters.sizes.has(size)) {
                        this.filters.sizes.delete(size);
                        e.target.classList.remove('active');
                    } else {
                        this.filters.sizes.add(size);
                        e.target.classList.add('active');
                    }
                }
            });
        }

        // Материалы
        const materialFilters = document.getElementById('materialFilters');
        if (materialFilters) {
            materialFilters.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    if (e.target.checked) {
                        this.filters.materials.add(e.target.value);
                    } else {
                        this.filters.materials.delete(e.target.value);
                    }
                }
            });
        }

        // Специальные фильтры
        const saleFilter = document.getElementById('saleFilter');
        if (saleFilter) {
            saleFilter.addEventListener('change', (e) => {
                this.filters.onSale = e.target.checked;
            });
        }
    }

    applyFilters() {
        this.closeFilter();
        this.currentPage = 1;
        this.filterProducts();
        this.renderProducts();
    }

    clearFilters() {
        this.filters = {
            brands: new Set(),
            colors: new Set(),
            sizes: new Set(),
            materials: new Set(),
            onSale: false
        };
        this.renderFilterOptions();
    }

    hasActiveFilters() {
        return this.filters.brands.size > 0 ||
               this.filters.colors.size > 0 ||
               this.filters.sizes.size > 0 ||
               this.filters.materials.size > 0 ||
               this.filters.onSale ||
               this.searchQuery;
    }

    renderActiveFilters() {
        const container = document.getElementById('activeFilters');
        if (!container) return;
        
        container.innerHTML = '<div class="filter-tags"></div>';
        const tagsContainer = container.querySelector('.filter-tags');

        // Добавить теги фильтров
        this.filters.brands.forEach(brand => this.addFilterTag(tagsContainer, 'brand', brand, brand));
        this.filters.colors.forEach(color => {
            const colorData = COLORS.find(c => c.value === color);
            this.addFilterTag(tagsContainer, 'color', color, colorData ? colorData.name : color);
        });
        this.filters.sizes.forEach(size => this.addFilterTag(tagsContainer, 'size', size, size));
        this.filters.materials.forEach(material => this.addFilterTag(tagsContainer, 'material', material, material));
        
        if (this.filters.onSale) {
            this.addFilterTag(tagsContainer, 'sale', 'true', 'Распродажа');
        }
        
        if (this.searchQuery) {
            this.addFilterTag(tagsContainer, 'search', this.searchQuery, `"${this.searchQuery}"`);
        }
    }

    addFilterTag(container, type, value, label) {
        const tag = document.createElement('div');
        tag.className = 'filter-tag';
        tag.innerHTML = `
            <span>${label}</span>
            <button class="remove-filter" data-type="${type}" data-value="${value}">×</button>
        `;
        
        tag.querySelector('.remove-filter').addEventListener('click', () => {
            this.removeFilter(type, value);
        });
        
        container.appendChild(tag);
    }

    removeFilter(type, value) {
        switch (type) {
            case 'brand':
                this.filters.brands.delete(value);
                break;
            case 'color':
                this.filters.colors.delete(value);
                break;
            case 'size':
                this.filters.sizes.delete(value);
                break;
            case 'material':
                this.filters.materials.delete(value);
                break;
            case 'sale':
                this.filters.onSale = false;
                break;
            case 'search':
                this.searchQuery = '';
                break;
        }
        
        this.currentPage = 1;
        this.filterProducts();
        this.renderProducts();
    }

    // Навигация
    goBack() {
        if (this.currentSubcategory) {
            this.currentSubcategory = null;
            this.showProducts();
        } else if (this.currentCategory) {
            this.currentCategory = null;
            this.currentGender = null;
            this.switchTab('home');
        } else {
            this.switchTab('home');
        }
    }

    // Избранное
    updateFavoritesTab() {
        const grid = document.getElementById('favoritesGrid');
        const emptyState = document.getElementById('emptyFavorites');
        
        if (!grid || !emptyState) return;
        
        grid.innerHTML = '';
        
        const favoriteProducts = this.products.filter(product => this.favorites.has(product.id));
        
        if (favoriteProducts.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }
        
        emptyState.classList.add('hidden');
        
        favoriteProducts.forEach(product => {
            const productCard = this.createProductCard(product);
            grid.appendChild(productCard);
        });
    }

    // Загрузка еще товаров
    loadMore() {
        this.currentPage++;
        this.renderProducts();
    }

    // Закрытие всех модальных окон
    closeAllModals() {
        this.closeCategories();
        this.closeSearch();
        this.closeFilter();
        this.closeProductDetail();
    }

    closeCategories() {
        const categoriesModal = document.getElementById('categoriesModal');
        if (categoriesModal) {
            categoriesModal.classList.add('hidden');
        }
    }

    // Работа с файлами
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const statusEl = document.getElementById('uploadStatus');
        if (statusEl) {
            statusEl.classList.remove('hidden');
            statusEl.className = 'upload-status';
            statusEl.textContent = 'Загрузка...';

            try {
                let products = [];
                
                if (file.name.endsWith('.json')) {
                    const text = await file.text();
                    products = JSON.parse(text);
                } else if (file.name.endsWith('.csv')) {
                    statusEl.className = 'upload-status error';
                    statusEl.textContent = 'CSV файлы пока не поддерживаются';
                    return;
                } else {
                    throw new Error('Неподдерживаемый формат файла');
                }

                const validProducts = this.validateProducts(products);
                
                if (validProducts.length > 0) {
                    this.products = [...this.products, ...validProducts];
                    statusEl.className = 'upload-status success';
                    statusEl.textContent = `Успешно загружено ${validProducts.length} товаров`;
                } else {
                    throw new Error('Не найдено валидных товаров');
                }
                
            } catch (error) {
                statusEl.className = 'upload-status error';
                statusEl.textContent = `Ошибка: ${error.message}`;
            }
        }
    }

    validateProducts(products) {
        return products.filter(product => {
            return product.name && product.brand && product.price && product.image;
        }).map(product => ({
            ...product,
            id: product.id || Date.now() + Math.random(),
            colors: Array.isArray(product.colors) ? product.colors : [],
            sizes: Array.isArray(product.sizes) ? product.sizes : [],
            materials: Array.isArray(product.materials) ? product.materials : [],
            onSale: Boolean(product.onSale),
            price: Number(product.price)
        }));
    }

    // Поддержка
    contactSupport() {
        const supportUrl = 'https://t.me/dolcedeals_support';
        window.open(supportUrl, '_blank');
    }

    // Информация о пользователе
    updateUserInfo() {
        const userName = document.getElementById('userName');
        const userID = document.getElementById('userID');
        
        if (userName && userID) {
            if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe.user) {
                const user = window.Telegram.WebApp.initDataUnsafe.user;
                userName.textContent = user.first_name + (user.last_name ? ` ${user.last_name}` : '');
                userID.textContent = `ID: ${user.id}`;
            } else {
                userName.textContent = 'Пользователь';
                userID.textContent = 'ID: 123456789';
            }
        }
    }

    // Сохранение избранного
    saveFavorites() {
        localStorage.setItem('dolce-deals-favorites', JSON.stringify([...this.favorites]));
    }

    loadFavorites() {
        try {
            const stored = localStorage.getItem('dolce-deals-favorites');
            if (stored) {
                this.favorites = new Set(JSON.parse(stored));
            }
        } catch (error) {
            console.error('Ошибка загрузки избранного:', error);
            this.favorites = new Set();
        }
    }

    // Скрытие экрана загрузки
    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loadingScreen');
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
                
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 500);
            }
        }, 1500);
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FashionApp();
});

// PWA и Telegram WebApp интеграция
if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
    
    // Настройка главной кнопки
    tg.MainButton.text = 'Перейти к товарам';
    tg.MainButton.show();
    
    tg.onEvent('mainButtonClicked', () => {
        if (window.app) {
            window.app.switchTab('products');
        }
    });
    
    // Обработка кнопки назад
    tg.onEvent('backButtonClicked', () => {
        if (window.app) {
            window.app.goBack();
        }
    });
}

// Service Worker регистрация
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}