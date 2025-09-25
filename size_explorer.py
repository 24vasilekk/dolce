#!/usr/bin/env python3
"""
BestSecret Size Explorer - Целенаправленное изучение системы размеров
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

class SizeExplorer:
    """Специализированный исследователь системы размеров BestSecret"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = None
        self.is_logged_in = False
        
        # Результаты исследования размеров
        self.size_results = {
            "timestamp": datetime.now().isoformat(),
            "successful_methods": [],
            "failed_methods": [],
            "size_patterns": [],
            "product_analyses": [],
            "best_selectors": []
        }
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def initialize_driver(self) -> bool:
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
        try:
            self.driver.get("https://www.bestsecret.com/entrance/index.htm")
            time.sleep(5)
            
            # Обработка cookies
            try:
                cookie_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-v-62969886]"))
                )
                cookie_btn.click()
                time.sleep(2)
            except:
                pass
            
            # Авторизация
            try:
                login_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "login-button"))
                )
                self.driver.execute_script("arguments[0].click();", login_btn)
            except:
                self.driver.get("https://login.bestsecret.com")
            
            time.sleep(5)
            
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
    
    def explore_sizes_intensively(self):
        """Интенсивное изучение системы размеров"""
        self.logger.info("🎯 НАЧИНАЕМ ИНТЕНСИВНОЕ ИЗУЧЕНИЕ РАЗМЕРОВ...")
        
        # Переходим в Luxury раздел для поиска товаров
        try:
            luxury_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#gtm-category-navigation-WOMEN_LUXURY_2"))
            )
            luxury_link.click()
            time.sleep(5)
        except:
            self.logger.warning("Не удалось перейти в Luxury, остаемся на текущей странице")
        
        # Находим товары для изучения
        product_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/product/"]')[:10]
        
        self.logger.info(f"🔍 Найдено {len(product_links)} товаров для анализа")
        
        for i, product_link in enumerate(product_links, 1):
            try:
                product_url = product_link.get_attribute('href')
                self.logger.info(f"📦 ТОВАР {i}/10: {product_url}")
                
                # Переходим на страницу товара
                self.driver.get(product_url)
                time.sleep(4)
                
                # Анализируем размеры на этой странице
                product_analysis = self._analyze_product_sizes(product_url)
                self.size_results["product_analyses"].append(product_analysis)
                
                # Если нашли рабочий метод, записываем его
                if product_analysis.get("successful_extractions"):
                    for method in product_analysis["successful_extractions"]:
                        self.size_results["successful_methods"].append(method)
                        self.logger.info(f"✅ РАБОЧИЙ МЕТОД НАЙДЕН: {method.get('method_description')}")
                
            except Exception as e:
                self.logger.error(f"Ошибка анализа товара {i}: {e}")
                continue
    
    def _analyze_product_sizes(self, product_url: str) -> Dict[str, Any]:
        """Детальный анализ размеров конкретного товара"""
        analysis = {
            "url": product_url,
            "page_title": self.driver.title,
            "size_buttons_found": [],
            "size_options_found": [],
            "interaction_attempts": [],
            "successful_extractions": [],
            "html_snapshots": {}
        }
        
        self.logger.info("🔍 Ищем кнопки и элементы размеров...")
        
        # Массивный поиск всех элементов, связанных с размерами
        size_search_strategies = [
            # ID-based selectors
            {"name": "size-selector-button", "selector": "#size-selector-button", "type": "id"},
            {"name": "size-options", "selector": "#size-options", "type": "id"},
            {"name": "size-dropdown", "selector": "#size-dropdown", "type": "id"},
            
            # Class-based selectors
            {"name": "size-selector", "selector": ".size-selector", "type": "class"},
            {"name": "size-button", "selector": ".size-button", "type": "class"},
            {"name": "size-option", "selector": ".size-option", "type": "class"},
            {"name": "option-size", "selector": ".option-size", "type": "class"},
            {"name": "product-size", "selector": ".product-size", "type": "class"},
            
            # Attribute-based selectors
            {"name": "data-size", "selector": "[data-size]", "type": "attribute"},
            {"name": "data-testid-size", "selector": "[data-testid*='size']", "type": "attribute"},
            
            # Text-based search (XPath)
            {"name": "button-text-size", "selector": "//button[contains(text(), 'Size')]", "type": "xpath"},
            {"name": "button-text-select", "selector": "//button[contains(text(), 'Select')]", "type": "xpath"},
            {"name": "span-text-size", "selector": "//span[contains(text(), 'Size')]", "type": "xpath"},
            
            # Combination selectors
            {"name": "button-size-class", "selector": "button[class*='size']", "type": "combo"},
            {"name": "div-size-class", "selector": "div[class*='size']", "type": "combo"},
            {"name": "span-size-class", "selector": "span[class*='size']", "type": "combo"}
        ]
        
        # Ищем все элементы
        for strategy in size_search_strategies:
            try:
                if strategy["type"] == "xpath":
                    elements = self.driver.find_elements(By.XPATH, strategy["selector"])
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, strategy["selector"])
                
                if elements:
                    self.logger.info(f"   🎯 {strategy['name']}: найдено {len(elements)} элементов")
                    
                    for elem in elements:
                        if elem.is_displayed():
                            elem_info = {
                                "strategy": strategy["name"],
                                "selector": strategy["selector"],
                                "tag": elem.tag_name,
                                "text": elem.text.strip()[:50],
                                "id": elem.get_attribute('id'),
                                "classes": elem.get_attribute('class'),
                                "html": elem.get_attribute('outerHTML')[:200],
                                "location": elem.location,
                                "size": elem.size,
                                "is_clickable": elem.is_enabled()
                            }
                            
                            if elem.tag_name == 'button' or 'button' in strategy["name"]:
                                analysis["size_buttons_found"].append(elem_info)
                            else:
                                analysis["size_options_found"].append(elem_info)
                            
            except Exception as e:
                self.logger.debug(f"Стратегия {strategy['name']} не сработала: {e}")
        
        # Пробуем взаимодействовать с найденными кнопками
        self.logger.info("🖱️ Тестируем взаимодействие с кнопками...")
        
        for button_info in analysis["size_buttons_found"]:
            interaction_result = self._test_size_interaction(button_info)
            analysis["interaction_attempts"].append(interaction_result)
            
            if interaction_result.get("success"):
                analysis["successful_extractions"].append(interaction_result)
        
        # Делаем снапшот HTML для анализа
        try:
            analysis["html_snapshots"]["full_page"] = self.driver.page_source[:5000]  # Первые 5000 символов
        except:
            pass
        
        return analysis
    
    def _test_size_interaction(self, button_info: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирование взаимодействия с кнопкой размеров"""
        interaction_result = {
            "button_info": button_info,
            "method_description": f"Клик по {button_info['strategy']} ({button_info['selector']})",
            "success": False,
            "extracted_sizes": [],
            "html_before": "",
            "html_after": "",
            "error": None
        }
        
        try:
            # Сохраняем состояние до взаимодействия
            try:
                size_container = self.driver.find_element(By.CSS_SELECTOR, "#size-options")
                interaction_result["html_before"] = size_container.get_attribute('outerHTML')[:500]
            except:
                pass
            
            # Находим элемент для клика
            if button_info["selector"].startswith("//"):
                element = self.driver.find_element(By.XPATH, button_info["selector"])
            else:
                element = self.driver.find_element(By.CSS_SELECTOR, button_info["selector"])
            
            # Кликаем
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
            
            # Ищем размеры после клика
            extracted_sizes = self._extract_sizes_after_interaction()
            
            if extracted_sizes:
                interaction_result["success"] = True
                interaction_result["extracted_sizes"] = extracted_sizes
                
                # Сохраняем состояние после взаимодействия
                try:
                    size_container = self.driver.find_element(By.CSS_SELECTOR, "#size-options")
                    interaction_result["html_after"] = size_container.get_attribute('outerHTML')[:500]
                except:
                    pass
                
                self.logger.info(f"✅ УСПЕШНО! Извлечено {len(extracted_sizes)} размеров")
            else:
                interaction_result["success"] = False
                self.logger.debug(f"❌ Размеры не найдены после клика по {button_info['strategy']}")
            
        except Exception as e:
            interaction_result["error"] = str(e)
            self.logger.debug(f"❌ Ошибка взаимодействия с {button_info['strategy']}: {e}")
        
        return interaction_result
    
    def _extract_sizes_after_interaction(self) -> List[Dict[str, Any]]:
        """Извлечение размеров после взаимодействия"""
        extracted_sizes = []
        
        # Множественные стратегии поиска размеров после клика
        extraction_strategies = [
            # Ваши оригинальные селекторы
            {"name": "original_1", "selector": "#size-options > div > span.option-size"},
            {"name": "original_2", "selector": "#size-options > div:nth-child(2) > span.option-size"},
            {"name": "original_3", "selector": "#size-options > div:nth-child(4)"},
            
            # Более общие
            {"name": "size_options_all", "selector": "#size-options *"},
            {"name": "size_options_divs", "selector": "#size-options div"},
            {"name": "size_options_spans", "selector": "#size-options span"},
            
            # По классам
            {"name": "option_size_class", "selector": ".option-size"},
            {"name": "size_item_class", "selector": ".size-item"},
            {"name": "size_value_class", "selector": ".size-value"},
            
            # По тегам внутри размеров
            {"name": "any_with_size_attr", "selector": "*[data-size]"},
            {"name": "clickable_sizes", "selector": "#size-options [onclick], #size-options button"},
        ]
        
        for strategy in extraction_strategies:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, strategy["selector"])
                
                for elem in elements:
                    if elem.is_displayed():
                        size_text = elem.text.strip()
                        
                        # Фильтруем релевантные размеры
                        if (size_text and 
                            size_text not in ['Size', 'Select Size', 'Choose Size', 'Sizes'] and
                            len(size_text) <= 15 and  # Размеры обычно короткие
                            not any(word in size_text.lower() for word in ['select', 'choose', 'available'])):
                            
                            size_info = {
                                "text": size_text,
                                "strategy": strategy["name"],
                                "selector": strategy["selector"],
                                "tag": elem.tag_name,
                                "classes": elem.get_attribute('class'),
                                "id": elem.get_attribute('id'),
                                "is_enabled": elem.is_enabled(),
                                "css_path": self._get_element_path(elem)
                            }
                            
                            # Избегаем дубликатов
                            if not any(existing["text"] == size_text for existing in extracted_sizes):
                                extracted_sizes.append(size_info)
                
                # Если нашли размеры этой стратегией, прекращаем поиск
                if extracted_sizes:
                    self.logger.info(f"📏 Размеры найдены стратегией: {strategy['name']}")
                    break
                    
            except Exception as e:
                self.logger.debug(f"Стратегия {strategy['name']} не сработала: {e}")
                continue
        
        return extracted_sizes
    
    def _get_element_path(self, element):
        """Получение CSS пути элемента"""
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
    
    def run_size_exploration(self):
        """Запуск исследования размеров"""
        self.logger.info("🚀 ЗАПУСК ИССЛЕДОВАНИЯ РАЗМЕРОВ BESTSECRET...")
        
        if not self.initialize_driver():
            return False
        
        if not self.login():
            return False
        
        try:
            self.explore_sizes_intensively()
            
            # Анализируем результаты
            self._analyze_results()
            
            # Сохраняем результаты
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"size_exploration_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.size_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ ИССЛЕДОВАНИЕ РАЗМЕРОВ ЗАВЕРШЕНО! Результаты в {filename}")
            
            # Выводим сводку
            self._print_size_summary()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка исследования размеров: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _analyze_results(self):
        """Анализ результатов и выявление лучших методов"""
        successful_methods = self.size_results["successful_methods"]
        
        if successful_methods:
            # Группируем по стратегиям
            strategy_success = {}
            
            for method in successful_methods:
                strategy = method["button_info"]["strategy"]
                if strategy not in strategy_success:
                    strategy_success[strategy] = []
                strategy_success[strategy].append(method)
            
            # Находим самые успешные стратегии
            best_strategies = sorted(strategy_success.items(), 
                                   key=lambda x: len(x[1]), reverse=True)
            
            for strategy, methods in best_strategies:
                avg_sizes = sum(len(m["extracted_sizes"]) for m in methods) / len(methods)
                
                best_selector_info = {
                    "strategy_name": strategy,
                    "success_count": len(methods),
                    "average_sizes_found": avg_sizes,
                    "selector": methods[0]["button_info"]["selector"],
                    "example_sizes": [size["text"] for size in methods[0]["extracted_sizes"][:5]]
                }
                
                self.size_results["best_selectors"].append(best_selector_info)
    
    def _print_size_summary(self):
        """Вывод сводки по размерам"""
        print("\n" + "="*70)
        print("📏 СВОДКА ИССЛЕДОВАНИЯ РАЗМЕРОВ")
        print("="*70)
        
        total_products = len(self.size_results["product_analyses"])
        successful_products = len([p for p in self.size_results["product_analyses"] 
                                  if p.get("successful_extractions")])
        
        print(f"\n📦 ТОВАРЫ:")
        print(f"   • Изучено товаров: {total_products}")
        print(f"   • С успешным извлечением размеров: {successful_products}")
        print(f"   • Процент успеха: {successful_products/total_products*100:.1f}%")
        
        if self.size_results["successful_methods"]:
            print(f"\n✅ УСПЕШНЫЕ МЕТОДЫ: {len(self.size_results['successful_methods'])}")
            
            for method in self.size_results["successful_methods"][:3]:
                strategy = method["button_info"]["strategy"]
                selector = method["button_info"]["selector"]
                sizes_count = len(method["extracted_sizes"])
                
                print(f"   🎯 {strategy}: {selector}")
                print(f"      Размеров найдено: {sizes_count}")
                
                example_sizes = [size["text"] for size in method["extracted_sizes"][:5]]
                print(f"      Примеры: {', '.join(example_sizes)}")
        
        if self.size_results["best_selectors"]:
            print(f"\n🏆 ЛУЧШИЕ СЕЛЕКТОРЫ:")
            
            for best in self.size_results["best_selectors"][:3]:
                print(f"   {best['strategy_name']}: {best['selector']}")
                print(f"      Успешных использований: {best['success_count']}")
                print(f"      Средне размеров за раз: {best['average_sizes_found']:.1f}")
                print(f"      Пример размеров: {', '.join(best['example_sizes'])}")
        
        print("="*70)

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
    
    explorer = SizeExplorer(EMAIL, PASSWORD)
    explorer.run_size_exploration()

if __name__ == "__main__":
    main()