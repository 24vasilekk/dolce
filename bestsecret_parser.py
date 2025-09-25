#!/usr/bin/env python3
"""
BestSecret Final Parser - Финальная версия с правильными селекторами
Поддерживает правильную навигацию, фильтры и размеры
"""

import os
import sys
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin
import uuid
import re
from dataclasses import dataclass, asdict
from pathlib import Path

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

@dataclass
class ProductData:
    url: str
    site: str = "BestSecret"
    sku: str = ""
    parsed_at: str = ""
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    gender: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    currency: Optional[str] = None
    discount_amount: Optional[float] = None
    discount_percentage: Optional[float] = None
    available_sizes: Optional[List[str]] = None
    out_of_stock_sizes: Optional[List[str]] = None
    in_stock: Optional[bool] = None
    stock_level: Optional[str] = None
    image_urls: Optional[List[str]] = None

class JSONDatabase:
    """Простая JSON база данных"""
    
    def __init__(self, filename: str = "products_database.json"):
        self.filename = filename
        self.data = []
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = []
    
    def save_product(self, product: ProductData):
        """Сохранение товара"""
        # Проверяем есть ли товар с таким URL
        product_dict = asdict(product)
        
        for i, existing in enumerate(self.data):
            if existing.get('url') == product.url:
                self.data[i] = product_dict
                break
        else:
            self.data.append(product_dict)
        
        # Сохраняем в файл
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

class BestSecretParser:
    """Финальный парсер BestSecret с правильными селекторами"""
    
    # Селекторы категорий с множественными стратегиями
    CATEGORY_SELECTORS = {
        "WOMEN": [
            "#app > header:nth-child(1) > div:nth-child(3) > div:nth-child(1) > nav:nth-child(1) > div:nth-child(3) > a:nth-child(1)",
            ".gender-switch-with-dropdown a:nth-child(1)",
            ".gender-switch-links a:nth-child(1)",
            "nav a[href*='FEMALE']",
            "a:contains('WOMEN')",
            "a:contains('Women')"
        ],
        "MEN": [
            "#app > header:nth-child(1) > div:nth-child(3) > div:nth-child(1) > nav:nth-child(1) > div:nth-child(3) > a:nth-child(2)",
            ".gender-switch-with-dropdown a:nth-child(2)", 
            ".gender-switch-links a:nth-child(2)",
            "nav a[href*='MALE']",
            "a:contains('MEN')",
            "a:contains('Men')"
        ], 
        "KIDS": [
            "#app > header:nth-child(1) > div:nth-child(3) > div:nth-child(1) > nav:nth-child(1) > div:nth-child(3) > a:nth-child(3)",
            ".gender-switch-with-dropdown a:nth-child(3)",
            ".gender-switch-links a:nth-child(3)",
            "nav a[href*='KIDS']",
            "a:contains('KIDS')",
            "a:contains('Kids')"
        ],
        # Aliases для совместимости
        "Женское": [
            ".gender-switch-with-dropdown a:nth-child(1)",
            "nav a[href*='FEMALE']",
            "a:contains('WOMEN')"
        ],
        "Мужское": [
            ".gender-switch-with-dropdown a:nth-child(2)",
            "nav a[href*='MALE']", 
            "a:contains('MEN')"
        ],
        "Детское": [
            ".gender-switch-with-dropdown a:nth-child(3)",
            "nav a[href*='KIDS']",
            "a:contains('KIDS')"
        ]
    }
    
    # Селекторы подкатегорий (найдены site explorer'ом)
    SUBCATEGORY_SELECTORS = {
        # Women's subcategories
        "WOMEN_HOME": "#gtm-category-navigation-WOMEN_NEW_1",
        "WOMEN_LUXURY": "#gtm-category-navigation-WOMEN_LUXURY_2",
        "WOMEN_CLOTHING": "#gtm-category-navigation-WOMEN_CLOTHING_3",
        "WOMEN_SHOES": "#gtm-category-navigation-WOMEN_SHOES_4",
        "WOMEN_SPORTS": "#gtm-category-navigation-WOMEN_SPORTS_5", 
        "WOMEN_ACCESSORIES": "#gtm-category-navigation-WOMEN_ACCESSORIES_6",
        "WOMEN_DESIGNER": "#gtm-category-navigation-WOMEN_DESIGNER_7",
        "WOMEN_PREVIEW": "#gtm-category-navigation-WOMEN_PREVIEW_8",
        
        # Men's subcategories (предполагаемые селекторы)
        "MEN_HOME": "#gtm-category-navigation-MEN_NEW_1",
        "MEN_LUXURY": "#gtm-category-navigation-MEN_LUXURY_2",
        "MEN_CLOTHING": "#gtm-category-navigation-MEN_CLOTHING_3",
        "MEN_SHOES": "#gtm-category-navigation-MEN_SHOES_4",
        "MEN_SPORTS": "#gtm-category-navigation-MEN_SPORTS_5", 
        "MEN_ACCESSORIES": "#gtm-category-navigation-MEN_ACCESSORIES_6",
        "MEN_DESIGNER": "#gtm-category-navigation-MEN_DESIGNER_7",
        
        # Kids subcategories (предполагаемые селекторы)
        "KIDS_HOME": "#gtm-category-navigation-KIDS_NEW_1",
        "KIDS_CLOTHING": "#gtm-category-navigation-KIDS_CLOTHING_3",
        "KIDS_SHOES": "#gtm-category-navigation-KIDS_SHOES_4",
        
        # Aliases для совместимости
        "Home": "#gtm-category-navigation-WOMEN_NEW_1",
        "Luxury": "#gtm-category-navigation-WOMEN_LUXURY_2",
        "Clothing": "#gtm-category-navigation-WOMEN_CLOTHING_3",
        "Shoes": "#gtm-category-navigation-WOMEN_SHOES_4",
        "MEN": "#gtm-category-navigation-MEN_NEW_1"  # Default men's section
    }
    
    # Селекторы фильтров в Luxury
    LUXURY_FILTER_SELECTORS = [
        "#v1-0-4 > span > span.filter-dropdown__button-label__text > span.filter-dropdown__button-label__text__inactive-version",
        "#v1-0-7 > span > span.filter-dropdown__button-label__text > span.filter-dropdown__button-label__text__inactive-version",
        "#v1-0-12 > span > span.filter-dropdown__button-label__text > span.filter-dropdown__button-label__text__inactive-version"
    ]
    
    # Селектор категорий одежды 
    CLOTHING_CATEGORY_FILTER = "body > astro-island > div > main > article > div.plp__content > div > div.plp__left-navigation-container > nav > ul > li:nth-child(1) > div > a"
    
    # Селекторы размеров
    SIZE_SELECTOR_BUTTON = "#size-selector-button"
    SIZE_OPTIONS = "#size-options > div > span.option-size"
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = None
        self.is_logged_in = False
        
        # База данных
        self.database = JSONDatabase()
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_driver(self) -> bool:
        """Инициализация браузера"""
        try:
            options = Options()
            options.add_argument("--window-size=1400,900")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Chrome(options=options)
            
            # Скрипты против детекции
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска браузера: {e}")
            return False
    
    def login(self) -> bool:
        """Авторизация на BestSecret"""
        try:
            self.driver.get("https://www.bestsecret.com/entrance/index.htm")
            time.sleep(5)
            
            # Обработка cookies
            self._handle_cookie_consent()
            
            # Клик по кнопке Login
            try:
                login_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "login-button"))
                )
                self.driver.execute_script("arguments[0].click();", login_btn)
            except:
                self.driver.get("https://login.bestsecret.com")
            
            time.sleep(5)
            
            # Ввод данных
            username_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(self.email)
            password_field.clear()
            password_field.send_keys(self.password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')]")
            login_button.click()
            
            time.sleep(10)
            
            # Проверяем успех
            current_url = self.driver.current_url
            if "bestsecret.com" in current_url and "login." not in current_url:
                self.is_logged_in = True
                self.logger.info("✅ Авторизация успешна")
                return True
            else:
                self.logger.error(f"❌ Авторизация не удалась. URL: {current_url}")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка авторизации: {e}")
            return False
    
    def _handle_cookie_consent(self):
        """Обработка согласия на cookies"""
        try:
            cookie_selectors = [
                "button[data-v-62969886]",
                ".cmp-overlay button", 
                "[data-testid='accept-cookies']"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_btn.click()
                    time.sleep(2)
                    return True
                except:
                    continue
        except:
            pass
        
        return False
    
    def navigate_to_category(self, category: str) -> bool:
        """Навигация к основной категории с множественными селекторами"""
        try:
            if category not in self.CATEGORY_SELECTORS:
                self.logger.error(f"❌ Неизвестная категория: {category}")
                return False
            
            selectors = self.CATEGORY_SELECTORS[category]
            self.logger.info(f"🧭 Переход в категорию: {category}")
            
            # Пробуем каждый селектор по очереди
            for i, selector in enumerate(selectors):
                try:
                    self.logger.debug(f"Пробуем селектор {i+1}/{len(selectors)}: {selector}")
                    
                    # Для XPath селекторов с contains
                    if 'contains' in selector:
                        # Извлекаем текст из селектора типа "a:contains('WOMEN')"
                        text_to_find = selector.split("contains('")[1].split("')")[0]
                        xpath_selector = f"//a[contains(text(), '{text_to_find}')]"
                        category_link = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_selector))
                        )
                    else:
                        category_link = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    self.driver.execute_script("arguments[0].click();", category_link)
                    time.sleep(5)
                    
                    self.logger.info(f"✅ Перешли в категорию {category} (селектор {i+1}: {selector})")
                    return True
                    
                except Exception as e:
                    self.logger.debug(f"Селектор {i+1} не сработал: {e}")
                    continue
            
            self.logger.error(f"❌ Все селекторы для категории {category} не сработали")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка навигации к категории: {e}")
            return False
    
    def navigate_to_subcategory(self, subcategory_key: str) -> bool:
        """Навигация к подкатегории"""
        try:
            if subcategory_key not in self.SUBCATEGORY_SELECTORS:
                self.logger.error(f"❌ Неизвестная подкатегория: {subcategory_key}")
                return False
            
            selector = self.SUBCATEGORY_SELECTORS[subcategory_key]
            self.logger.info(f"🔍 Переход к подкатегории: {subcategory_key}")
            
            subcategory_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            self.driver.execute_script("arguments[0].click();", subcategory_link)
            time.sleep(5)
            
            self.logger.info(f"✅ Перешли в подкатегорию: {subcategory_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка навигации к подкатегории: {e}")
            return False
    
    def apply_luxury_filters(self, filter_index: int = 0) -> bool:
        """Применение фильтров в разделе Luxury"""
        try:
            if filter_index >= len(self.LUXURY_FILTER_SELECTORS):
                self.logger.error(f"❌ Неверный индекс фильтра: {filter_index}")
                return False
            
            selector = self.LUXURY_FILTER_SELECTORS[filter_index]
            self.logger.info(f"🎯 Применяем luxury фильтр {filter_index + 1}")
            
            filter_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            self.driver.execute_script("arguments[0].click();", filter_element)
            time.sleep(3)
            
            self.logger.info(f"✅ Применен luxury фильтр {filter_index + 1}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка применения luxury фильтра: {e}")
            return False
    
    def get_product_links(self, max_products: int = 20) -> List[str]:
        """Получение ссылок на товары со страницы"""
        try:
            product_links = []
            
            # Ждем загрузки страницы
            time.sleep(3)
            
            # Селекторы для ссылок на товары
            product_selectors = [
                'a[href*="/product/"]',
                'a[href*="/artikel/"]', 
                'a[href*="/item/"]',
                '.product-tile a',
                '.product-card a',
                '.product-link',
                '[data-testid*="product"] a'
            ]
            
            for selector in product_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for link in links[:max_products]:
                        href = link.get_attribute('href')
                        if href and href not in product_links:
                            if href.startswith('/'):
                                href = 'https://www.bestsecret.com' + href
                            product_links.append(href)
                    
                    if product_links:
                        break
                        
                except Exception:
                    continue
            
            self.logger.info(f"🔍 Найдено {len(product_links)} ссылок на товары")
            return product_links[:max_products]
            
        except Exception as e:
            self.logger.error(f"Ошибка получения ссылок на товары: {e}")
            return []
    
    def extract_sizes_from_product_page(self) -> Tuple[List[str], List[str]]:
        """Извлечение размеров с страницы товара с множественными стратегиями"""
        available_sizes = []
        out_of_stock_sizes = []
        
        try:
            # СТРАТЕГИЯ 1: Интерактивные элементы размеров
            size_button_found = self._try_interactive_size_extraction()
            
            if size_button_found:
                available_sizes, out_of_stock_sizes = self._extract_from_interactive_elements()
            
            # СТРАТЕГИЯ 2: Если интерактивное извлечение не сработало, парсим из описания
            if not available_sizes and not out_of_stock_sizes:
                self.logger.info("🔍 Интерактивные размеры не найдены, парсим из описания...")
                available_sizes = self._extract_sizes_from_description()
            
            # СТРАТЕГИЯ 3: Если и описание не помогло, ищем в HTML
            if not available_sizes and not out_of_stock_sizes:
                self.logger.info("🔍 Размеры в описании не найдены, ищем в HTML...")
                available_sizes, out_of_stock_sizes = self._extract_from_static_elements()
            
            # Логируем результат
            total_sizes = len(available_sizes) + len(out_of_stock_sizes)
            if total_sizes > 0:
                self.logger.info(f"📏 Извлечено размеров: {len(available_sizes)} доступных, {len(out_of_stock_sizes)} недоступных")
                self.logger.info(f"    Доступные: {available_sizes}")
                if out_of_stock_sizes:
                    self.logger.info(f"    Недоступные: {out_of_stock_sizes}")
            else:
                self.logger.warning("⚠️ Размеры не найдены ни одной стратегией")
                        
        except Exception as e:
            self.logger.error(f"❌ Ошибка извлечения размеров: {e}")
            
        return available_sizes, out_of_stock_sizes
    
    def _try_interactive_size_extraction(self) -> bool:
        """Попытка интерактивного извлечения размеров"""
        size_button_selectors = [
            "#size-selector-button",
            ".size-selector-button", 
            "button[class*='size']",
            "[data-testid*='size']",
            ".product-size-selector",
            "button[aria-label*='size']",
            "button[aria-label*='Size']"
        ]
        
        for selector in size_button_selectors:
            try:
                size_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                self.driver.execute_script("arguments[0].click();", size_button)
                time.sleep(2)
                self.logger.info(f"✅ Кликнули на кнопку размеров: {selector}")
                return True
            except:
                continue
        
        self.logger.debug("🔍 Кнопка размеров не найдена")
        return False
    
    def _extract_from_interactive_elements(self) -> Tuple[List[str], List[str]]:
        """Извлечение размеров из интерактивных элементов после клика"""
        available_sizes = []
        out_of_stock_sizes = []
        
        size_option_selectors = [
            "#size-options > div > span.option-size",
            "#size-options > div:nth-child(2) > span.option-size", 
            "#size-options > div:nth-child(4)",
            "#size-options div",
            "#size-options span",
            ".size-option",
            ".size-list .size",
            "[data-size]",
            "span[class*='size']",
            ".product-sizes .size",
            ".size-dropdown-option"
        ]
        
        for selector in size_option_selectors:
            try:
                size_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if size_elements:
                    self.logger.info(f"📏 Найдено размеров с селектором {selector}: {len(size_elements)}")
                    
                    for elem in size_elements:
                        if elem.is_displayed():
                            size_text = elem.text.strip()
                            
                            if size_text and size_text not in ['Size', 'Select Size', 'Choose Size', 'Sizes']:
                                # Проверяем доступность
                                is_disabled = self._is_element_disabled(elem)
                                
                                if is_disabled:
                                    if size_text not in out_of_stock_sizes:
                                        out_of_stock_sizes.append(size_text)
                                else:
                                    if size_text not in available_sizes:
                                        available_sizes.append(size_text)
                    
                    if available_sizes or out_of_stock_sizes:
                        break
                        
            except Exception as e:
                self.logger.debug(f"Селектор {selector} не сработал: {e}")
                continue
        
        return available_sizes, out_of_stock_sizes
    
    def _extract_sizes_from_description(self) -> List[str]:
        """Извлечение размеров из описания товара"""
        sizes = []
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            description_selectors = [
                '.product-description', '.description', '.product-details',
                '.item-description', '.product-info', '.product-measurements'
            ]
            
            description_text = ""
            for selector in description_selectors:
                elem = soup.select_one(selector)
                if elem:
                    description_text = elem.get_text()
                    break
            
            if description_text:
                # Паттерны для поиска размеров в описании
                size_patterns = [
                    r'size\s+(\w+):', r'Size\s+(\w+):', 
                    r'Our model is wearing:\s*(\w+)', r'Model wearing:\s*(\w+)',
                    r'Measurements for size\s+(\w+):', r'Size\s+(\w+)\s*[:\-]',
                    r'Available in sizes?\s*[:\-]?\s*([\w\s,\-XS-XL0-9]+)',
                    r'Sizes?\s+available\s*[:\-]?\s*([\w\s,\-XS-XL0-9]+)'
                ]
                
                for pattern in size_patterns:
                    matches = re.findall(pattern, description_text, re.IGNORECASE)
                    for match in matches:
                        # Обрабатываем найденные размеры
                        if ',' in match:  # Несколько размеров через запятую
                            size_list = [s.strip() for s in match.split(',')]
                        elif '-' in match and any(x in match for x in ['XS', 'S', 'M', 'L', 'XL']):  # Диапазон размеров типа XS-XL
                            size_list = self._expand_size_range(match)
                        else:
                            size_list = [match.strip()]
                        
                        for size in size_list:
                            if size and len(size) <= 10 and size not in sizes:
                                sizes.append(size)
                
                # Дополнительно ищем цифровые размеры (35, 36, 37, etc.)
                numeric_sizes = re.findall(r'\b(3[0-9]|4[0-9]|5[0-9])\b', description_text)
                for size in numeric_sizes:
                    if size not in sizes:
                        sizes.append(size)
                
                if sizes:
                    self.logger.info(f"📏 Найдены размеры в описании: {sizes}")
                    
        except Exception as e:
            self.logger.debug(f"Ошибка парсинга размеров из описания: {e}")
        
        return sizes
    
    def _extract_from_static_elements(self) -> Tuple[List[str], List[str]]:
        """Извлечение размеров из статических элементов страницы"""
        available_sizes = []
        out_of_stock_sizes = []
        
        try:
            # Ищем любые элементы, которые могут содержать размеры
            size_selectors = [
                '*[data-size]', '*[data-testid*="size"]', 
                '.size', '.sizes', '.product-size', '.item-size',
                'span:contains("XS")', 'span:contains("XL")', 'span:contains("Size")',
                '.measurements', '.size-guide'
            ]
            
            for selector in size_selectors:
                try:
                    if 'contains' in selector:
                        # Используем XPath для поиска по тексту
                        xpath_patterns = [
                            "//span[contains(text(), 'XS') or contains(text(), 'S') or contains(text(), 'M') or contains(text(), 'L') or contains(text(), 'XL')]",
                            "//div[contains(text(), 'Size') or contains(text(), 'size')]",
                            "//*[contains(@class, 'size') and string-length(text()) > 0 and string-length(text()) < 10]"
                        ]
                        
                        for xpath in xpath_patterns:
                            elements = self.driver.find_elements(By.XPATH, xpath)
                            for elem in elements:
                                if elem.is_displayed():
                                    text = elem.text.strip()
                                    if self._is_valid_size(text):
                                        is_disabled = self._is_element_disabled(elem)
                                        if is_disabled:
                                            if text not in out_of_stock_sizes:
                                                out_of_stock_sizes.append(text)
                                        else:
                                            if text not in available_sizes:
                                                available_sizes.append(text)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            if elem.is_displayed():
                                # Попробуем получить размер из атрибута data-size
                                size_from_attr = elem.get_attribute('data-size')
                                if size_from_attr and self._is_valid_size(size_from_attr):
                                    is_disabled = self._is_element_disabled(elem)
                                    if is_disabled:
                                        if size_from_attr not in out_of_stock_sizes:
                                            out_of_stock_sizes.append(size_from_attr)
                                    else:
                                        if size_from_attr not in available_sizes:
                                            available_sizes.append(size_from_attr)
                                
                                # Также проверяем текст элемента
                                text = elem.text.strip()
                                if self._is_valid_size(text):
                                    is_disabled = self._is_element_disabled(elem)
                                    if is_disabled:
                                        if text not in out_of_stock_sizes:
                                            out_of_stock_sizes.append(text)
                                    else:
                                        if text not in available_sizes:
                                            available_sizes.append(text)
                            
                except Exception as e:
                    self.logger.debug(f"Ошибка с селектором {selector}: {e}")
                    continue
        
        except Exception as e:
            self.logger.debug(f"Ошибка статического извлечения размеров: {e}")
        
        return available_sizes, out_of_stock_sizes
    
    def _is_element_disabled(self, element) -> bool:
        """Проверка, отключен ли элемент"""
        try:
            # Проверяем атрибуты элемента
            if element.get_attribute('disabled') or not element.is_enabled():
                return True
            
            # Проверяем классы
            classes = element.get_attribute('class') or ''
            if any(cls in classes.lower() for cls in ['disabled', 'unavailable', 'out-of-stock', 'sold-out']):
                return True
            
            # Проверяем родительские элементы
            try:
                parent = element.find_element(By.XPATH, "..")
                parent_classes = parent.get_attribute('class') or ""
                if any(cls in parent_classes.lower() for cls in ['disabled', 'unavailable', 'out-of-stock', 'sold-out']):
                    return True
            except:
                pass
                
            return False
        except:
            return False
    
    def _is_valid_size(self, text: str) -> bool:
        """Проверка, является ли текст валидным размером"""
        if not text or len(text) > 15:
            return False
        
        text = text.strip()
        
        # Исключаем нерелевантные тексты
        invalid_texts = {
            'size', 'sizes', 'select', 'choose', 'available', 'select size', 
            'choose size', 'size guide', 'measurements', 'fit', 'model'
        }
        
        if text.lower() in invalid_texts:
            return False
        
        # Проверяем валидные паттерны размеров
        valid_patterns = [
            r'^(XS|S|M|L|XL|XXL|XXXL)$',  # Буквенные размеры
            r'^\d+$',  # Цифровые размеры (35, 36, 37, etc.)
            r'^\d{1,2}[.,]?\d{0,1}$',  # Размеры с десятичными (38.5, 39,5)
            r'^(ONE SIZE|One Size|ONESIZE)$',  # One size
            r'^\d+[A-Z]{1,2}$',  # Размеры типа 32A, 34B
            r'^\d+/\d+$',  # Размеры типа 32/34
            r'^[A-Z]\d+$'  # Размеры типа S36, M38
        ]
        
        return any(re.match(pattern, text.upper()) for pattern in valid_patterns)
    
    def _expand_size_range(self, size_range: str) -> List[str]:
        """Расширение диапазона размеров типа XS-XL в список"""
        try:
            if '-' in size_range:
                start, end = size_range.split('-', 1)
                start, end = start.strip().upper(), end.strip().upper()
                
                # Стандартные размерные сетки
                size_orders = {
                    'letter': ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'],
                    'numeric': list(range(30, 60))  # Для обувь/одежда
                }
                
                # Определяем тип размеров
                if start in size_orders['letter'] and end in size_orders['letter']:
                    start_idx = size_orders['letter'].index(start)
                    end_idx = size_orders['letter'].index(end)
                    return size_orders['letter'][start_idx:end_idx+1]
                
                elif start.isdigit() and end.isdigit():
                    start_num, end_num = int(start), int(end)
                    return [str(i) for i in range(start_num, end_num + 1)]
        
        except:
            pass
        
        return [size_range]  # Возвращаем исходный, если не можем разобрать
    
    def _parse_product_page(self, product_url: str) -> Optional[ProductData]:
        """Парсинг страницы товара"""
        try:
            self.driver.get(product_url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Создаем объект продукта
            product = ProductData(
                url=product_url,
                site="BestSecret",
                sku=f"BS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}",
                parsed_at=datetime.now().isoformat()
            )
            
            # Извлекаем данные
            product.name = self._extract_name(soup)
            product.brand = self._extract_brand(soup)
            product.current_price, product.original_price, product.currency = self._extract_prices(soup)
            
            # Рассчитываем скидку
            if product.current_price and product.original_price and product.original_price > product.current_price:
                product.discount_amount = round(product.original_price - product.current_price, 2)
                product.discount_percentage = round(
                    (product.discount_amount / product.original_price) * 100, 2
                )
            
            # Извлекаем размеры с помощью правильных селекторов
            product.available_sizes, product.out_of_stock_sizes = self.extract_sizes_from_product_page()
            
            product.in_stock, product.stock_level = self._extract_stock_info(soup)
            product.color = self._extract_color(soup)
            product.description = self._extract_description(soup)
            product.image_urls = self._extract_image_urls(soup)
            
            # Сохраняем в базу
            self.database.save_product(product)
            
            return product
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга товара {product_url}: {e}")
            return None
    
    def go_to_home(self) -> bool:
        """Переход на главную страницу"""
        try:
            self.driver.get("https://www.bestsecret.com/")
            time.sleep(3)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка перехода на главную: {e}")
            return False

    def parse_category(self, category: str, subcategory: str = None, max_products: int = 10) -> List[ProductData]:
        """Парсинг товаров из категории"""
        
        if not self.is_logged_in:
            self.logger.error("❌ Требуется авторизация")
            return []
        
        products = []
        
        try:
            # 0. Переходим на главную страницу для чистого старта
            self.go_to_home()
            
            # 1. Навигация к категории
            if not self.navigate_to_category(category):
                self.logger.warning(f"⚠️ Не удалось перейти к категории {category}, пропускаем")
                return products
            
            # 2. Навигация к подкатегории (если указана)
            if subcategory:
                if not self.navigate_to_subcategory(subcategory):
                    self.logger.warning(f"⚠️ Не удалось перейти к подкатегории {subcategory}, продолжаем с основной категорией")
                    # Не возвращаемся, продолжаем парсинг основной категории
            
            # 3. Получение ссылок на товары
            product_links = self.get_product_links(max_products)
            
            if not product_links:
                self.logger.warning(f"❌ Товары не найдены в {category}")
                return products
            
            # 4. Парсинг каждого товара
            for i, product_url in enumerate(product_links, 1):
                self.logger.info(f"📦 Парсинг товара {i}/{len(product_links)}: {product_url}")
                
                product_data = self._parse_product_page(product_url)
                if product_data:
                    # Добавляем информацию о категории
                    product_data.category = category
                    product_data.subcategory = subcategory
                    
                    products.append(product_data)
                    
                    # Выводим краткую информацию
                    price_info = f" - {product_data.current_price}€" if product_data.current_price else ""
                    discount_info = f" (-{product_data.discount_percentage}%)" if product_data.discount_percentage else ""
                    sizes_info = f" - размеры: {product_data.available_sizes}" if product_data.available_sizes else ""
                    
                    self.logger.info(f"    ✅ {product_data.name}{price_info}{discount_info}{sizes_info}")
                
                time.sleep(2)  # Пауза между товарами
            
            return products
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка парсинга категории: {e}")
            return products
    
    # Методы извлечения данных (упрощенные)
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            '[data-product-name]', '.product-name', '.product-title', 
            '.item-name', 'h1[class*="product"]', 'h1[class*="title"]', 'h1'
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text(strip=True):
                return elem.get_text(strip=True)
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            '[data-product-brand]', '.brand-name', '.product-brand', 
            '.designer-name', '.vendor', '.brand', 'span[class*="brand"]', 
            'div[class*="brand"]', '.t-brand'
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text(strip=True):
                return elem.get_text(strip=True)
        return None
    
    def _extract_prices(self, soup: BeautifulSoup) -> tuple:
        current_price = original_price = None
        currency = 'EUR'
        
        # Сначала ищем цены в описании товара
        description_elem = soup.select_one('.product-description, .description, .product-details, .item-description, .product-info')
        if description_elem:
            description_text = description_elem.get_text(strip=True)
            
            # Шаблоны для цен в описании
            price_patterns = [
                r'RRP\s+([\d.,]+)\s*€\s*-\s*(\d+)%\s*([\d.,]+)\s*€',
                r'([\d.,]+)\s*€\s*-\s*(\d+)%\s*([\d.,]+)\s*€',
                r'RRP\s+([\d.,]+)\s*€.*?([\d.,]+)\s*€',
                r'(\d{1,4}[.,]\d{2})\s*€.*?(\d{1,4}[.,]\d{2})\s*€',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, description_text)
                if match:
                    try:
                        def parse_price(price_str):
                            price_str = price_str.strip()
                            if ',' in price_str and '.' in price_str:
                                price_str = price_str.replace('.', '').replace(',', '.')
                            elif ',' in price_str:
                                price_str = price_str.replace(',', '.')
                            return float(price_str)
                        
                        if len(match.groups()) >= 3:
                            original_price = parse_price(match.group(1))
                            current_price = parse_price(match.group(3))
                        elif len(match.groups()) >= 2:
                            original_price = parse_price(match.group(1))
                            current_price = parse_price(match.group(2))
                        
                        if original_price and current_price:
                            if current_price > original_price:
                                original_price, current_price = current_price, original_price
                            break
                    except ValueError:
                        continue
        
        return current_price, original_price, currency
    
    def _extract_stock_info(self, soup: BeautifulSoup) -> tuple:
        in_stock = True
        stock_level = "in_stock"
        
        out_of_stock_indicators = [
            '.out-of-stock', '.sold-out', '.unavailable',
            '[data-stock="false"]', '.stock-out'
        ]
        
        for selector in out_of_stock_indicators:
            if soup.select_one(selector):
                in_stock = False
                stock_level = "out_of_stock"
                break
        
        return in_stock, stock_level
    
    def _extract_color(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            '.color-name', '.product-color', '[data-color]',
            '.selected-color', '.color-option.selected'
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.get_text(strip=True):
                return elem.get_text(strip=True)
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            '.product-description', '.description', '.product-details',
            '.item-description', '.product-info'
        ]
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                desc_text = elem.get_text(strip=True)
                if len(desc_text) > 50:
                    return desc_text[:1000]
        return None
    
    def _extract_image_urls(self, soup: BeautifulSoup) -> List[str]:
        images = []
        selectors = [
            '.product-image img', '.product-gallery img', '.main-image img',
            '[data-product-image]', 'img[src*="product"]', 'img[alt*="product"]'
        ]
        
        for selector in selectors:
            elems = soup.select(selector)
            for elem in elems:
                src = elem.get('src') or elem.get('data-src') or elem.get('data-original')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.bestsecret.com' + src
                    
                    if src not in images and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        images.append(src)
        
        return images[:10]
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def demo_parsing():
    """Демонстрация работы парсера"""
    print("🚀 BestSecret Final Parser - Демо")
    print("=" * 50)
    
    # Загружаем данные из .env
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
            email_match = re.search(r'BESTSECRET_EMAIL=(.+)', env_content)
            password_match = re.search(r'BESTSECRET_PASSWORD=(.+)', env_content)
            
            EMAIL = email_match.group(1) if email_match else None
            PASSWORD = password_match.group(1) if password_match else None
    except:
        EMAIL = "akinitovfilipp@gmail.com"
        PASSWORD = "Kaluga40"
    
    parser = BestSecretParser(EMAIL, PASSWORD)
    
    try:
        # Инициализация
        if not parser.initialize_driver():
            print("❌ Не удалось запустить браузер")
            return
        
        # Авторизация
        if not parser.login():
            print("❌ Ошибка авторизации")
            return
        
        # Тестируем различные категории
        test_cases = [
            ("Женское", "WOMEN_LUXURY", 2),
            ("Мужское", "MEN", 2),  # Navigate to Men section first
            ("Детское", None, 1)
        ]
        
        all_products = []
        
        for category, subcategory, max_products in test_cases:
            print(f"\n🎯 Парсинг: {category}" + (f" → {subcategory}" if subcategory else ""))
            
            products = parser.parse_category(category, subcategory, max_products)
            all_products.extend(products)
            
            print(f"✅ Найдено {len(products)} товаров")
        
        # Общая статистика
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего товаров: {len(all_products)}")
        
        if all_products:
            with_prices = sum(1 for p in all_products if p.current_price)
            with_sizes = sum(1 for p in all_products if p.available_sizes)
            with_images = sum(1 for p in all_products if p.image_urls)
            
            print(f"   С ценами: {with_prices}/{len(all_products)} ({with_prices/len(all_products)*100:.1f}%)")
            print(f"   С размерами: {with_sizes}/{len(all_products)} ({with_sizes/len(all_products)*100:.1f}%)")
            print(f"   С изображениями: {with_images}/{len(all_products)} ({with_images/len(all_products)*100:.1f}%)")
        
        print(f"\n💾 Данные сохранены в: {parser.database.filename}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        parser.cleanup()

if __name__ == "__main__":
    demo_parsing()