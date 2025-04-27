from duckduckgo_search import DDGS
from dotenv import load_dotenv
import os
import requests
import json

class DuckDuckGoAgent:
    def __init__(self):
        self.ddgs = DDGS(proxy=None, timeout=10) 
        self.search_types = {
            "weather": self.search_weather,
            "news": self.search_news,
            "location": self.search_location,
            "general": self.search_general
        }

    def parse_query(self, query: str) -> str:
        """查詢分析邏輯"""
        query = query.lower()
        
        weather_keywords = ["天氣", "weather", "temperature", "forecast", "溫度", "降雨", "雨量", 
                            "氣象", "climate", "濕度", "humidity", "紫外線", "uv"]
                            
        news_keywords = ["新聞", "news", "headlines", "report", "事件", "時事", "報導", 
                        "breaking", "latest", "today", "頭條", "焦點"]
                        
        location_keywords = ["附近", "地圖", "map", "nearby", "location", "restaurant", "店",
                            "餐廳", "咖啡廳", "cafe", "coffee", "地點", "距離", "營業時間", "地址", 
                            "怎麼走", "捷運站", "公車站", "hotel", "飯店", "公園"]
        
        if any(w in query for w in weather_keywords):
            return "weather"
        elif any(w in query for w in news_keywords):
            return "news"
        elif any(w in query for w in location_keywords):
            return "location"
        else:
            return "general"

    def search_weather(self, query: str) -> list:
        results = self.ddgs.text(
            f"{query} 天氣預報 即時資訊",
            region="tw-tzh",
            timelimit="d",
            max_results=5
        )
        
        if not results:
            results = self.ddgs.text(
                f"{query} weather forecast current",
                region="tw-tzh",
                timelimit="d",
                max_results=5
            )
            
        return results

    def search_news(self, query: str) -> list:
        return self.ddgs.news(
            keywords=query,
            region="tw-tzh",
            timelimit="d",
            max_results=5
        )

    def search_location(self, query: str) -> list:
        """搜尋地點相關資訊"""
        results = self.ddgs.text(
            query,
            region="tw-tzh",
            max_results=5
        )
        
        if not results:
            results = self.ddgs.text(
                f"{query} 位置 地址",
                region="tw-tzh",
                max_results=5
            )
        
        if not results:
            results = self.ddgs.text(
                f"{query} location address",
                region="tw-tzh",
                max_results=5
            )
            
        return results

    def search_general(self, query: str) -> list:
        results = []
        
        direct_results = self.ddgs.text(
            query,
            region="tw-tzh",
            max_results=3
        )
        
        quoted_results = self.ddgs.text(
            f'"{query}"',
            region="tw-tzh",
            max_results=3
        )
        
        seen_urls = set()
        for result_set in [direct_results, quoted_results]:
            if result_set:
                for item in result_set:
                    url = item.get('href', '')
                    if url not in seen_urls:
                        results.append(item)
                        seen_urls.add(url)
                        if len(results) >= 5:
                            break
        
        return results

class ChatAgent:
    def __init__(self, search_engine="duckduckgo"):
        self.search_engine_type = search_engine.lower()
        self.search_engine = DuckDuckGoAgent()
        self.last_query = ""
    
    def generate_response(self, user_query: str) -> str:
        """處理用戶查詢並生成回應"""
        self.last_query = user_query  # 保存當前查詢以供評分使用
        query_type = self.search_engine.parse_query(user_query)
        search_function = self.search_engine.search_types[query_type]
        
        try:
            results = search_function(user_query)
            
            if not results:
                return json.dumps([{"content": "No results found for your query. Please try a different search term.", "url": ""}], ensure_ascii=False, indent=2)
                
            return self.format_results(results, query_type)
        except Exception as e:
            return json.dumps([{"content": f"Error processing your query: {str(e)}", "url": ""}], ensure_ascii=False, indent=2)
        
    def format_results(self, results: list, query_type: str) -> str:
        """格式化搜尋結果"""
        try:
            return self._format_ddg_results(results, query_type)
        except Exception as e:
            error_data = [{"content": f"Error formatting results: {str(e)}", "url": ""}]
            return json.dumps(error_data, ensure_ascii=False, indent=2)
        
    def _evaluate_relevance(self, item, query, query_type):
        """評估搜尋結果與查詢的相關性分數"""
        title = item.get('title', '').lower()
        body = item.get('body', '').lower() if 'body' in item else ''
        url = item.get('href', '').lower()
        
        # 將查詢詞分解為關鍵詞
        query_words = query.lower().split()
        # 移除常見的停用詞
        stopwords = {"的", "了", "是", "在", "我", "你", "他", "她", "它", "與", "和", "或", "幫", "查", "找"}
        query_words = [w for w in query_words if w not in stopwords and len(w) > 1]
        
        # 初始分數
        score = 0
        
        # 標題匹配評分（最重要）
        for word in query_words:
            if word in title:
                score += 10  # 標題中的關鍵詞給予高分
        
        # 完整查詢詞組在標題中的匹配
        if query.lower() in title:
            score += 30  # 標題包含完整查詢詞組，大幅加分
        
        # 內容匹配評分
        for word in query_words:
            if body and word in body:
                score += 5  # 內容中的關鍵詞給予中等分數
        
        # URL 相關性
        for word in query_words:
            if word in url:
                score += 3  # URL 中的關鍵詞給予一些分數
        
        if query_type == "location":
            location_indicators = ["地址", "map", "地圖", "位置", "address"]
            if any(indicator in body.lower() for indicator in location_indicators):
                score += 15
            
            location_parts = [w for w in query_words if len(w) >= 2]  # 可能的地點名稱
            target_words = [w for w in query_words if w not in location_parts]  # 可能的搜尋目標
            
            if location_parts and target_words:
                if any(loc in title for loc in location_parts) and any(target in title for target in target_words):
                    score += 25 
        
        return score

    def _format_ddg_results(self, results: list, query_type: str) -> str:
        """格式化 DuckDuckGo 結果為JSON，只返回最相關的結果"""
        if not results:
            formatted_results = [{"content": "No results found.", "url": ""}]
            return json.dumps(formatted_results, ensure_ascii=False, indent=2)
        
        scored_results = []
        for item in results:
            relevance_score = self._evaluate_relevance(item, self.last_query, query_type)
            scored_results.append((item, relevance_score))
        
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        best_result = scored_results[0][0]
        
        formatted_result = {"content": "", "url": ""}
        
        if query_type == "weather":
            formatted_result = {
                "content": f"{best_result.get('title', 'No title')}: {best_result.get('body', 'No content')[:100]}...",
                "url": best_result.get('href', 'No link')
            }
        elif query_type == "news":
            formatted_result = {
                "content": best_result.get('title', 'No title'),
                "url": best_result.get('url', best_result.get('href', 'No link'))
            }
        elif query_type == "location":
            formatted_result = {
                "content": best_result.get('title', 'No title'),
                "url": best_result.get('href', 'No link')
            }
        else:
            formatted_result = {
                "content": f"{best_result.get('title', 'No title')} - {best_result.get('body', 'No content')[:150]}...",
                "url": best_result.get('href', 'No link')
            }
        
        return json.dumps([formatted_result], ensure_ascii=False, indent=2)