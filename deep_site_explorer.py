#!/usr/bin/env python3
"""
BestSecret Deep Explorer - Глубокое изучение всех элементов сайта
Изучает хедер, фильтры, категории, товары и размеры детально
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re

class DeepBestSecretExplorer:
    """Глубокий исследователь всех элементов BestSecret"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = None
        self.is_logged_in = False
        
        # Результаты глубокого исследования
        self.exploration_results = {
            "timestamp": datetime.now().isoformat(),
            "header_deep_analysis": {},
            "all_categories": {},
            "all_subcategories": {},
            "filter_systems": {},
            "product_page_analysis": {},
            "size_extraction_methods": {},
            "navigation_paths": {},
            "interactive_elements": {},
            "page_variations": {}
        }
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def initialize_driver(self) -> bool:
        """Инициализация браузера"""
        try:
            options = Options()
            options.add_argument("--window-size=1400,900")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Chrome(options=options)
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
    
    def deep_explore_header(self):
        """Глубокое изучение хедера"""
        self.logger.info("🔬 ГЛУБОКОЕ ИЗУЧЕНИЕ ХЕДЕРА...")
        
        try:
            # Получаем весь HTML хедера
            header_html = self.driver.execute_script("return document.querySelector('header').outerHTML")
            soup = BeautifulSoup(header_html, 'html.parser')
            
            # Анализируем каждый элемент хедера
            header_analysis = {
                "total_elements": len(soup.find_all()),
                "navigation_elements": [],
                "interactive_elements": [],
                "category_switches": [],
                "all_links": [],
                "form_elements": []
            }
            
            # Все навигационные элементы
            nav_elements = soup.find_all(['nav', 'ul', 'li'])
            for nav in nav_elements:
                nav_info = {
                    "tag": nav.name,
                    "id": nav.get('id'),
                    "classes": nav.get('class', []),
                    "text": nav.get_text(strip=True)[:100],
                    "children_count": len(nav.find_all())
                }
                header_analysis["navigation_elements"].append(nav_info)
            
            # Все ссылки в хедере
            links = soup.find_all('a')
            for link in links:
                link_info = {
                    "href": link.get('href', ''),
                    "text": link.get_text(strip=True),
                    "id": link.get('id'),
                    "classes": link.get('class', []),
                    "css_selector": self._generate_css_path(link)
                }
                header_analysis["all_links"].append(link_info)
            
            # Интерактивные элементы
            interactive = soup.find_all(['button', 'input', 'select'])
            for elem in interactive:
                elem_info = {
                    "tag": elem.name,
                    "type": elem.get('type', ''),
                    "id": elem.get('id'),
                    "classes": elem.get('class', []),
                    "text": elem.get_text(strip=True)
                }
                header_analysis["interactive_elements"].append(elem_info)
            
            self.exploration_results["header_deep_analysis"] = header_analysis
            self.logger.info(f"✅ Хедер: {header_analysis['total_elements']} элементов, {len(header_analysis['all_links'])} ссылок")
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения хедера: {e}")
    
    def explore_all_categories(self):
        """Изучение всех возможных категорий"""
        self.logger.info("🗂️ ИЗУЧЕНИЕ ВСЕХ КАТЕГОРИЙ...")
        
        try:
            categories_found = {
                "gender_categories": [],
                "main_categories": [],
                "quick_links": [],
                "campaign_links": []
            }
            
            # Гендерные категории в хедере
            gender_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a[href*='gender=']")
            for link in gender_links:
                category_info = {
                    "text": link.text,
                    "href": link.get_attribute('href'),
                    "css_selector": self._get_element_selector(link),
                    "is_active": 'active' in link.get_attribute('class') or '',
                    "gender": self._extract_gender_from_url(link.get_attribute('href'))
                }
                categories_found["gender_categories"].append(category_info)
            
            # Основные категории (Luxury, Clothing, etc.)
            main_category_selectors = [
                "[id*='gtm-category-navigation']",
                ".category-link",
                "nav[class*='category'] a"
            ]
            
            for selector in main_category_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.text.strip():
                            category_info = {
                                "text": elem.text,
                                "href": elem.get_attribute('href'),
                                "id": elem.get_attribute('id'),
                                "classes": elem.get_attribute('class'),
                                "css_selector": self._get_element_selector(elem)
                            }
                            categories_found["main_categories"].append(category_info)
                except:
                    continue
            
            # Быстрые ссылки
            quick_links = self.driver.find_elements(By.CSS_SELECTOR, ".category-quick-link a")
            for link in quick_links:
                if link.text.strip():
                    quick_link_info = {
                        "text": link.text,
                        "href": link.get_attribute('href'),
                        "css_selector": self._get_element_selector(link)
                    }
                    categories_found["quick_links"].append(quick_link_info)
            
            # Кампании и промо
            campaign_links = self.driver.find_elements(By.CSS_SELECTOR, ".campaign-link")
            for link in campaign_links:
                if link.text.strip():
                    campaign_info = {
                        "text": link.text[:100],  # Ограничиваем текст
                        "href": link.get_attribute('href'),
                        "css_selector": self._get_element_selector(link)
                    }
                    categories_found["campaign_links"].append(campaign_info)
            
            self.exploration_results["all_categories"] = categories_found
            
            total_categories = (len(categories_found["gender_categories"]) + 
                              len(categories_found["main_categories"]) + 
                              len(categories_found["quick_links"]) + 
                              len(categories_found["campaign_links"]))
            
            self.logger.info(f"✅ Найдено {total_categories} категорий:")
            self.logger.info(f"   - Гендерных: {len(categories_found['gender_categories'])}")
            self.logger.info(f"   - Основных: {len(categories_found['main_categories'])}")
            self.logger.info(f"   - Быстрых ссылок: {len(categories_found['quick_links'])}")
            self.logger.info(f"   - Кампаний: {len(categories_found['campaign_links'])}")
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения категорий: {e}")
    
    def explore_filter_systems(self):
        """Глубокое изучение систем фильтрации"""
        self.logger.info("🎯 ИЗУЧЕНИЕ СИСТЕМ ФИЛЬТРАЦИИ...")
        
        filter_systems = {}
        
        # Переходим в разные разделы для изучения фильтров
        sections_to_explore = [
            ("Home", "#gtm-category-navigation-WOMEN_NEW_1"),
            ("Luxury", "#gtm-category-navigation-WOMEN_LUXURY_2"), 
            ("Clothing", "#gtm-category-navigation-WOMEN_CLOTHING_3"),
            ("Shoes", "#gtm-category-navigation-WOMEN_SHOES_4")
        ]
        
        for section_name, selector in sections_to_explore:
            try:
                self.logger.info(f"🔍 Изучаем фильтры в разделе: {section_name}")
                
                # Переходим в раздел
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                time.sleep(5)
                
                # Ищем все возможные фильтры
                filter_elements = self._find_all_filter_elements()
                filter_systems[section_name] = filter_elements
                
                self.logger.info(f"✅ {section_name}: найдено {len(filter_elements)} фильтров")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось изучить фильтры в {section_name}: {e}")
        
        self.exploration_results["filter_systems"] = filter_systems
    
    def _find_all_filter_elements(self):
        """Поиск всех элементов фильтрации на текущей странице"""
        filter_elements = []
        
        # Различные типы фильтров
        filter_selectors = [
            # Dropdown фильтры
            "[class*='filter-dropdown']",
            "[class*='dropdown']",
            "select",
            
            # Checkbox фильтры  
            "input[type='checkbox']",
            "[class*='checkbox']",
            
            # Button фильтры
            "button[class*='filter']",
            "[data-filter]",
            
            # Range фильтры (цена)
            "input[type='range']",
            "input[type='number']",
            "[class*='price']",
            "[class*='range']",
            
            # Специфичные для BestSecret
            "[id*='v1-0-']",
            ".filter-dropdown__button-label__text",
            ".plp__left-navigation-container",
            "[class*='navigation-container']"
        ]
        
        for selector in filter_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        filter_info = {
                            "selector": selector,
                            "id": elem.get_attribute('id'),
                            "classes": elem.get_attribute('class'),
                            "text": elem.text.strip()[:50],
                            "tag": elem.tag_name,
                            "type": elem.get_attribute('type'),
                            "css_path": self._get_element_selector(elem),
                            "is_clickable": elem.is_enabled()
                        }
                        filter_elements.append(filter_info)
            except:
                continue
        
        return filter_elements
    
    def deep_explore_products(self):
        """Глубокое изучение страниц товаров"""
        self.logger.info("🛍️ ГЛУБОКОЕ ИЗУЧЕНИЕ СТРАНИЦ ТОВАРОВ...")
        
        try:
            # Находим несколько товаров для изучения
            product_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/product/"]')[:5]
            
            product_analyses = []
            
            for i, product_link in enumerate(product_links, 1):
                product_url = product_link.get_attribute('href')
                self.logger.info(f"🔬 Анализируем товар {i}: {product_url}")
                
                # Переходим на страницу товара
                self.driver.get(product_url)
                time.sleep(5)
                
                # Глубокий анализ страницы товара
                product_analysis = self._deep_analyze_product_page()
                product_analysis["url"] = product_url
                product_analyses.append(product_analysis)
                
                # Специально изучаем размеры
                size_analysis = self._deep_analyze_sizes()
                product_analysis["size_analysis"] = size_analysis
            
            self.exploration_results["product_page_analysis"] = product_analyses
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения товаров: {e}")
    
    def _deep_analyze_product_page(self):
        """Детальный анализ страницы товара"""
        analysis = {
            "page_title": self.driver.title,
            "current_url": self.driver.current_url,
            "all_elements": {},
            "interactive_elements": {},
            "data_attributes": {},
            "scripts": []
        }
        
        try:
            # Анализируем все элементы на странице
            all_elements = self.driver.find_elements(By.XPATH, "//*")
            
            element_types = {}
            for elem in all_elements:
                tag = elem.tag_name
                element_types[tag] = element_types.get(tag, 0) + 1
            
            analysis["all_elements"] = element_types
            
            # Интерактивные элементы
            interactive_selectors = ['button', 'input', 'select', 'a[href]', '[onclick]', '[data-testid]']
            for selector in interactive_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    interactive_info = []
                    
                    for elem in elements[:10]:  # Ограничиваем количество
                        elem_info = {
                            "tag": elem.tag_name,
                            "text": elem.text.strip()[:30],
                            "id": elem.get_attribute('id'),
                            "classes": elem.get_attribute('class'),
                            "data_attributes": self._get_data_attributes(elem)
                        }
                        interactive_info.append(elem_info)
                    
                    analysis["interactive_elements"][selector] = interactive_info
                except:
                    continue
            
            # JavaScript скрипты
            try:
                scripts = self.driver.find_elements(By.TAG_NAME, "script")
                script_info = []
                for script in scripts[:5]:  # Первые 5 скриптов
                    src = script.get_attribute('src')
                    if src:
                        script_info.append({"src": src})
                    else:
                        content = script.get_attribute('innerHTML')
                        if content and len(content) < 200:
                            script_info.append({"inline": content[:100]})
                
                analysis["scripts"] = script_info
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа страницы товара: {e}")
        
        return analysis
    
    def _deep_analyze_sizes(self):
        """Детальный анализ системы размеров"""
        self.logger.info("📏 ДЕТАЛЬНЫЙ АНАЛИЗ РАЗМЕРОВ...")
        
        size_analysis = {
            "size_button_analysis": [],
            "size_options_analysis": [],
            "size_interaction_methods": [],
            "html_structure": "",
            "javascript_events": []
        }
        
        try:
            # Ищем все возможные элементы, связанные с размерами
            size_related_selectors = [
                "*[id*='size']",
                "*[class*='size']", 
                "*[data-size]",
                "*[aria-label*='size']",
                "button:contains('Size')",
                "button:contains('Select')",
                ".option-size",
                "#size-options",
                "#size-selector-button"
            ]
            
            for selector in size_related_selectors:
                try:
                    if 'contains' in selector:
                        # Используем XPath для поиска по тексту
                        xpath = f"//*[contains(text(), 'Size') or contains(text(), 'Select')]"
                        elements = self.driver.find_elements(By.XPATH, xpath)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in elements:
                        if elem.is_displayed():
                            elem_info = {
                                "selector_used": selector,
                                "tag": elem.tag_name,
                                "id": elem.get_attribute('id'),
                                "classes": elem.get_attribute('class'),
                                "text": elem.text.strip(),
                                "html": elem.get_attribute('outerHTML')[:200],
                                "data_attributes": self._get_data_attributes(elem),
                                "css_path": self._get_element_selector(elem),
                                "is_clickable": elem.is_enabled(),
                                "location": elem.location,
                                "size": elem.size
                            }
                            
                            if 'button' in selector or elem.tag_name == 'button':
                                size_analysis["size_button_analysis"].append(elem_info)
                            else:
                                size_analysis["size_options_analysis"].append(elem_info)
                
                except Exception as e:
                    self.logger.debug(f"Селектор {selector} не сработал: {e}")
                    continue
            
            # Пробуем кликнуть на найденные кнопки размеров
            for button_info in size_analysis["size_button_analysis"]:
                try:
                    self.logger.info(f"🖱️ Пробуем кликнуть: {button_info['css_path']}")
                    
                    element = self.driver.find_element(By.CSS_SELECTOR, button_info['css_path'])
                    
                    # Записываем состояние до клика
                    before_click = len(self.driver.find_elements(By.CSS_SELECTOR, "*"))
                    
                    # Кликаем
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(2)
                    
                    # Записываем состояние после клика
                    after_click = len(self.driver.find_elements(By.CSS_SELECTOR, "*"))
                    
                    # Ищем новые элементы размеров
                    new_size_elements = []
                    size_option_selectors = [
                        "#size-options *",
                        "*[class*='option']",
                        "*[class*='size-item']",
                        ".size-list *"
                    ]
                    
                    for opt_selector in size_option_selectors:
                        try:
                            options = self.driver.find_elements(By.CSS_SELECTOR, opt_selector)
                            for opt in options:
                                if opt.is_displayed() and opt.text.strip():
                                    opt_info = {
                                        "text": opt.text.strip(),
                                        "tag": opt.tag_name,
                                        "classes": opt.get_attribute('class'),
                                        "css_path": self._get_element_selector(opt),
                                        "html": opt.get_attribute('outerHTML')[:100]
                                    }
                                    new_size_elements.append(opt_info)
                        except:
                            continue
                    
                    interaction_result = {
                        "button_clicked": button_info['css_path'],
                        "elements_before": before_click,
                        "elements_after": after_click,
                        "new_size_elements": new_size_elements,
                        "success": len(new_size_elements) > 0
                    }
                    
                    size_analysis["size_interaction_methods"].append(interaction_result)
                    
                    if len(new_size_elements) > 0:
                        self.logger.info(f"✅ НАЙДЕНЫ РАЗМЕРЫ! Кнопка: {button_info['css_path']}, элементов: {len(new_size_elements)}")
                        
                        # Записываем HTML структуру размеров
                        try:
                            size_container = self.driver.find_element(By.CSS_SELECTOR, "#size-options")
                            size_analysis["html_structure"] = size_container.get_attribute('outerHTML')
                        except:
                            pass
                        break  # Если нашли рабочий способ, прекращаем поиск
                    
                except Exception as e:
                    self.logger.debug(f"Не удалось кликнуть {button_info.get('css_path', 'unknown')}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа размеров: {e}")
        
        return size_analysis
    
    def _get_data_attributes(self, element):
        """Получение всех data-атрибутов элемента"""
        data_attrs = {}
        try:
            # Получаем все атрибуты через JavaScript
            attrs = self.driver.execute_script("""
                var items = {};
                for (var i = 0; i < arguments[0].attributes.length; i++) {
                    var attr = arguments[0].attributes[i];
                    if (attr.name.startsWith('data-')) {
                        items[attr.name] = attr.value;
                    }
                }
                return items;
            """, element)
            return attrs
        except:
            return {}
    
    def _get_element_selector(self, element):
        """Генерация уникального CSS селектора для элемента"""
        try:
            return self.driver.execute_script("""
                function getPath(element) {
                    if (element.id !== '') {
                        return '#' + element.id;
                    }
                    if (element === document.body) {
                        return 'body';
                    }
                    
                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element) {
                            return getPath(element.parentNode) + ' > ' + element.tagName + ':nth-child(' + (ix + 1) + ')';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }
                return getPath(arguments[0]).toLowerCase();
            """, element)
        except:
            return "unknown"
    
    def _generate_css_path(self, element):
        """Генерация CSS пути для BeautifulSoup элемента"""
        path = []
        while element.parent:
            siblings = element.parent.find_all(element.name, recursive=False)
            if len(siblings) == 1:
                path.append(element.name)
            else:
                for i, sibling in enumerate(siblings, 1):
                    if sibling == element:
                        path.append(f"{element.name}:nth-child({i})")
                        break
            element = element.parent
        return " > ".join(reversed(path))
    
    def _extract_gender_from_url(self, url):
        """Извлечение гендера из URL"""
        if 'FEMALE' in url:
            return 'FEMALE'
        elif 'MALE' in url:
            return 'MALE'
        elif 'KIDS' in url:
            return 'KIDS'
        return 'UNKNOWN'
    
    def run_deep_exploration(self):
        """Запуск полного глубокого исследования"""
        self.logger.info("🚀 НАЧИНАЕМ ГЛУБОКОЕ ИССЛЕДОВАНИЕ BESTSECRET...")
        
        if not self.initialize_driver():
            return False
        
        if not self.login():
            return False
        
        try:
            # Последовательное глубокое изучение
            self.deep_explore_header()
            self.explore_all_categories() 
            self.explore_filter_systems()
            self.deep_explore_products()
            
            # Сохраняем результаты
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"deep_exploration_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.exploration_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ ГЛУБОКОЕ ИССЛЕДОВАНИЕ ЗАВЕРШЕНО! Результаты в {filename}")
            
            # Выводим детальную сводку
            self._print_detailed_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка во время глубокого исследования: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _print_detailed_summary(self):
        """Детальная сводка результатов"""
        print("\n" + "="*80)
        print("📊 ДЕТАЛЬНАЯ СВОДКА ГЛУБОКОГО ИССЛЕДОВАНИЯ")
        print("="*80)
        
        # Хедер
        header_analysis = self.exploration_results.get("header_deep_analysis", {})
        if header_analysis:
            print(f"\n🏠 ХЕДЕР САЙТА:")
            print(f"   • Всего элементов: {header_analysis.get('total_elements', 0)}")
            print(f"   • Навигационных элементов: {len(header_analysis.get('navigation_elements', []))}")
            print(f"   • Ссылок: {len(header_analysis.get('all_links', []))}")
            print(f"   • Интерактивных элементов: {len(header_analysis.get('interactive_elements', []))}")
        
        # Категории
        categories = self.exploration_results.get("all_categories", {})
        if categories:
            print(f"\n🗂️ КАТЕГОРИИ:")
            print(f"   • Гендерных категорий: {len(categories.get('gender_categories', []))}")
            print(f"   • Основных категорий: {len(categories.get('main_categories', []))}")
            print(f"   • Быстрых ссылок: {len(categories.get('quick_links', []))}")
            print(f"   • Кампаний: {len(categories.get('campaign_links', []))}")
            
            # Показываем главные категории
            for cat in categories.get('gender_categories', [])[:3]:
                print(f"     - {cat.get('text', 'N/A')} → {cat.get('gender', 'N/A')}")
        
        # Фильтры
        filters = self.exploration_results.get("filter_systems", {})
        if filters:
            print(f"\n🎯 СИСТЕМЫ ФИЛЬТРАЦИИ:")
            for section, filter_list in filters.items():
                print(f"   • {section}: {len(filter_list)} фильтров")
        
        # Товары и размеры
        products = self.exploration_results.get("product_page_analysis", [])
        if products:
            print(f"\n🛍️ АНАЛИЗ ТОВАРОВ:")
            print(f"   • Изучено товаров: {len(products)}")
            
            # Анализ размеров
            size_methods_found = 0
            successful_size_extractions = 0
            
            for product in products:
                size_analysis = product.get("size_analysis", {})
                interaction_methods = size_analysis.get("size_interaction_methods", [])
                
                size_methods_found += len(interaction_methods)
                successful_size_extractions += len([m for m in interaction_methods if m.get("success")])
            
            print(f"   • Методов извлечения размеров найдено: {size_methods_found}")
            print(f"   • Успешных извлечений размеров: {successful_size_extractions}")
            
            # Показываем успешные методы
            for product in products:
                size_analysis = product.get("size_analysis", {})
                for method in size_analysis.get("size_interaction_methods", []):
                    if method.get("success"):
                        print(f"   ✅ РАБОЧИЙ МЕТОД: {method.get('button_clicked')}")
                        print(f"      Найдено размеров: {len(method.get('new_size_elements', []))}")
                        for size_elem in method.get('new_size_elements', [])[:3]:
                            print(f"      - Размер: '{size_elem.get('text')}' (CSS: {size_elem.get('css_path', 'N/A')[:50]})")
        
        print("="*80)

def main():
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
    
    explorer = DeepBestSecretExplorer(EMAIL, PASSWORD)
    explorer.run_deep_exploration()

if __name__ == "__main__":
    main()