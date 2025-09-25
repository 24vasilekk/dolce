#!/usr/bin/env python3
"""
BestSecret Site Explorer - Автоматическое изучение структуры сайта
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
from bs4 import BeautifulSoup
import re

class BestSecretExplorer:
    """Исследователь структуры сайта BestSecret"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = None
        self.is_logged_in = False
        
        # Результаты исследования
        self.exploration_results = {
            "timestamp": datetime.now().isoformat(),
            "header_structure": {},
            "navigation": {},
            "categories": {},
            "product_page": {},
            "filters": {},
            "size_selectors": [],
            "page_structures": {}
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
    
    def explore_header_structure(self):
        """Изучение структуры хэдера"""
        self.logger.info("🔍 Изучаем структуру хэдера...")
        
        try:
            # Ищем хэдер
            header_selectors = ["header", ".header", "#header", ".main-header", ".site-header"]
            
            for selector in header_selectors:
                try:
                    header = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if header:
                        self.logger.info(f"✅ Найден хэдер: {selector}")
                        
                        # Анализируем структуру хэдера
                        header_html = header.get_attribute('outerHTML')
                        soup = BeautifulSoup(header_html, 'html.parser')
                        
                        # Ищем навигационные элементы
                        nav_elements = soup.find_all(['nav', 'div', 'ul'], class_=re.compile(r'nav|menu|category|gender'))
                        
                        self.exploration_results["header_structure"][selector] = {
                            "found": True,
                            "navigation_elements": []
                        }
                        
                        for nav in nav_elements:
                            nav_info = {
                                "tag": nav.name,
                                "classes": nav.get('class', []),
                                "id": nav.get('id'),
                                "children_count": len(nav.find_all(['a', 'button']))
                            }
                            self.exploration_results["header_structure"][selector]["navigation_elements"].append(nav_info)
                        
                        break
                        
                except NoSuchElementException:
                    continue
            
            # Ищем конкретные элементы категорий
            self.logger.info("🔍 Ищем элементы категорий в хэдере...")
            
            category_patterns = [
                "женск", "мужск", "детск", "women", "men", "kids", "child", "female", "male"
            ]
            
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            category_links = []
            
            for link in all_links[:50]:  # Ограничиваем поиск первыми 50 ссылками
                try:
                    text = link.text.lower()
                    href = link.get_attribute('href') or ""
                    
                    for pattern in category_patterns:
                        if pattern in text or pattern in href.lower():
                            category_links.append({
                                "text": link.text,
                                "href": href,
                                "css_selector": self._generate_css_selector(link),
                                "classes": link.get_attribute('class')
                            })
                            break
                except:
                    continue
            
            self.exploration_results["categories"]["potential_category_links"] = category_links
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения хэдера: {e}")
    
    def explore_navigation_structure(self):
        """Изучение навигационной структуры"""
        self.logger.info("🧭 Изучаем навигационную структуру...")
        
        try:
            # Ищем все навигационные элементы
            nav_selectors = [
                "nav", ".navigation", ".nav", ".menu", ".category-nav", 
                "[class*='nav']", "[class*='menu']", "[class*='category']"
            ]
            
            found_navigations = []
            
            for selector in nav_selectors:
                try:
                    navs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for nav in navs:
                        nav_info = {
                            "selector": selector,
                            "text_content": nav.text[:200],  # Первые 200 символов
                            "id": nav.get_attribute('id'),
                            "classes": nav.get_attribute('class'),
                            "tag_name": nav.tag_name,
                            "children_count": len(nav.find_elements(By.XPATH, ".//*"))
                        }
                        
                        if nav_info not in found_navigations and nav.text.strip():
                            found_navigations.append(nav_info)
                            
                except:
                    continue
            
            self.exploration_results["navigation"]["found_elements"] = found_navigations
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения навигации: {e}")
    
    def explore_product_page(self):
        """Изучение структуры страницы товара"""
        self.logger.info("🛍️ Изучаем структуру страницы товара...")
        
        try:
            # Сначала найдем ссылку на товар
            product_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/product/"], a[href*="/artikel/"]')
            
            if product_links:
                product_url = product_links[0].get_attribute('href')
                self.logger.info(f"🔗 Переходим на страницу товара: {product_url}")
                
                self.driver.get(product_url)
                time.sleep(5)
                
                # Ищем элементы размеров
                self.logger.info("📏 Ищем элементы размеров...")
                
                size_selectors_to_test = [
                    "#size-selector-button",
                    "#size-options",
                    "#size-options > div",
                    "#size-options > div > span.option-size",
                    "#size-options > div:nth-child(2) > span.option-size",
                    "#size-options > div:nth-child(4)",
                    ".size-option",
                    ".size-selector",
                    "[data-size]",
                    "button[class*='size']",
                    "span[class*='size']",
                    ".product-size",
                    ".sizes"
                ]
                
                found_size_elements = []
                
                for selector in size_selectors_to_test:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for i, elem in enumerate(elements):
                            if elem.is_displayed():
                                size_info = {
                                    "selector": selector,
                                    "index": i,
                                    "text": elem.text.strip(),
                                    "tag_name": elem.tag_name,
                                    "classes": elem.get_attribute('class'),
                                    "id": elem.get_attribute('id'),
                                    "visible": elem.is_displayed(),
                                    "clickable": elem.is_enabled()
                                }
                                found_size_elements.append(size_info)
                                
                    except Exception as e:
                        self.logger.debug(f"Селектор {selector} не найден: {e}")
                
                self.exploration_results["product_page"]["size_elements"] = found_size_elements
                
                # Попробуем кликнуть на кнопку размеров
                try:
                    size_button = self.driver.find_element(By.CSS_SELECTOR, "#size-selector-button")
                    if size_button.is_displayed():
                        self.logger.info("🖱️ Кликаем на кнопку выбора размера...")
                        self.driver.execute_script("arguments[0].click();", size_button)
                        time.sleep(2)
                        
                        # После клика ищем опции размеров
                        size_options = self.driver.find_elements(By.CSS_SELECTOR, "#size-options div")
                        size_options_info = []
                        
                        for i, option in enumerate(size_options):
                            if option.text.strip():
                                size_text_elem = option.find_elements(By.CSS_SELECTOR, "span.option-size")
                                option_info = {
                                    "index": i,
                                    "full_text": option.text.strip(),
                                    "size_text": size_text_elem[0].text.strip() if size_text_elem else "",
                                    "css_selector": f"#size-options > div:nth-child({i+1})",
                                    "size_span_selector": f"#size-options > div:nth-child({i+1}) > span.option-size",
                                    "classes": option.get_attribute('class')
                                }
                                size_options_info.append(option_info)
                        
                        self.exploration_results["product_page"]["size_options_after_click"] = size_options_info
                        
                except Exception as e:
                    self.logger.warning(f"Не удалось кликнуть на кнопку размеров: {e}")
                
                # Ищем другие элементы товара
                product_elements = {
                    "title": ["h1", ".product-title", ".product-name", "[data-product-name]"],
                    "price": [".price", ".t-price", "[data-price]", ".product-price"],
                    "brand": [".brand", ".t-brand", "[data-brand]", ".product-brand"],
                    "color": [".color", "[data-color]", ".product-color"],
                    "images": ["img[src*='product']", ".product-image", ".gallery img"]
                }
                
                for element_type, selectors in product_elements.items():
                    found_elements = []
                    
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            
                            for elem in elements:
                                if elem.is_displayed() and elem.text.strip():
                                    found_elements.append({
                                        "selector": selector,
                                        "text": elem.text.strip()[:100],  # Первые 100 символов
                                        "tag": elem.tag_name
                                    })
                                    
                        except:
                            continue
                    
                    self.exploration_results["product_page"][element_type] = found_elements
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения страницы товара: {e}")
    
    def explore_filters(self):
        """Изучение фильтров"""
        self.logger.info("🎯 Изучаем фильтры...")
        
        try:
            # Переходим в luxury раздел
            try:
                luxury_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Luxury")
                luxury_link.click()
                time.sleep(5)
                
                # Ищем элементы фильтров
                filter_selectors = [
                    "[class*='filter']",
                    "[id*='filter']", 
                    ".filter-dropdown",
                    "[class*='dropdown']",
                    "select",
                    "[role='button']"
                ]
                
                found_filters = []
                
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
                                    "tag": elem.tag_name
                                }
                                found_filters.append(filter_info)
                                
                    except:
                        continue
                
                self.exploration_results["filters"]["luxury_section"] = found_filters
                
            except:
                self.logger.warning("Не удалось перейти в раздел Luxury")
            
        except Exception as e:
            self.logger.error(f"Ошибка изучения фильтров: {e}")
    
    def _generate_css_selector(self, element):
        """Генерация CSS селектора для элемента"""
        try:
            return self.driver.execute_script("""
                function getCSSSelector(el) {
                    var names = [];
                    while (el.parentNode) {
                        if (el.id) {
                            names.unshift('#' + el.id);
                            break;
                        } else {
                            if (el == el.ownerDocument.documentElement) 
                                names.unshift(el.tagName);
                            else {
                                for (var c = 1, e = el; e.previousElementSibling; e = e.previousElementSibling, c++);
                                names.unshift(el.tagName + ":nth-child(" + c + ")");
                            }
                            el = el.parentNode;
                        }
                    }
                    return names.join(" > ");
                }
                return getCSSSelector(arguments[0]);
            """, element)
        except:
            return "unknown"
    
    def run_full_exploration(self):
        """Полное исследование сайта"""
        self.logger.info("🚀 Начинаем полное исследование BestSecret...")
        
        if not self.initialize_driver():
            return False
        
        if not self.login():
            return False
        
        try:
            # Последовательное изучение всех элементов
            self.explore_header_structure()
            self.explore_navigation_structure()
            self.explore_product_page()
            self.explore_filters()
            
            # Сохраняем результаты
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"site_exploration_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.exploration_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ Исследование завершено! Результаты сохранены в {filename}")
            
            # Выводим краткую сводку
            self.print_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка во время исследования: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def print_summary(self):
        """Вывод краткой сводки результатов"""
        print("\n" + "="*60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ИССЛЕДОВАНИЯ")
        print("="*60)
        
        # Категории
        if "potential_category_links" in self.exploration_results["categories"]:
            print(f"\n🏷️ Найдено потенциальных категорий: {len(self.exploration_results['categories']['potential_category_links'])}")
            for link in self.exploration_results["categories"]["potential_category_links"][:5]:
                print(f"   • {link['text']} - {link['css_selector']}")
        
        # Элементы размеров
        if "size_elements" in self.exploration_results["product_page"]:
            print(f"\n📏 Найдено элементов размеров: {len(self.exploration_results['product_page']['size_elements'])}")
            for elem in self.exploration_results["product_page"]["size_elements"][:5]:
                print(f"   • {elem['selector']} - '{elem['text']}'")
        
        # Опции размеров после клика
        if "size_options_after_click" in self.exploration_results["product_page"]:
            print(f"\n🎯 Опции размеров после клика: {len(self.exploration_results['product_page']['size_options_after_click'])}")
            for option in self.exploration_results["product_page"]["size_options_after_click"][:5]:
                print(f"   • {option['size_span_selector']} - '{option['size_text']}'")
        
        # Фильтры
        if "luxury_section" in self.exploration_results["filters"]:
            print(f"\n🎯 Найдено фильтров в Luxury: {len(self.exploration_results['filters']['luxury_section'])}")
        
        print("="*60)

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
    
    explorer = BestSecretExplorer(EMAIL, PASSWORD)
    explorer.run_full_exploration()

if __name__ == "__main__":
    main()