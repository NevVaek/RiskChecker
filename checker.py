import os, time, sys
import pandas as pd
from dotenv import load_dotenv
from requests import RequestException
from serpapi import GoogleSearch
from urllib.parse import urlparse

# Configuration

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

MAX_COMPANIES = int(os.getenv("MAX_COMPANIES"))
SLEEP_TIME = float(os.getenv("SLEEP_SECONDS"))

INPUT_FILE = os.getenv("INPUT_FILE")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

WEIGHT_HIGH = 3
WEIGHT_MID  = 2
WEIGHT_LOW  = 1

SOURCE_BONUS_TRUSTED = 1
SOURCE_PENALTY_LOW   = -1

TRUSTED_DOMAINS = {
    "nhk.or.jp",
    "asahi.com",
    "nikkei.com",
    "mainichi.jp",
    "yomiuri.co.jp",
    "jiji.com",
    "kyodo.co.jp",
}

# Main Logic

class Checker:
    def __init__(self, high, mid, low):
        self.KEYWORDS_HIGH = high
        self.KEYWORDS_MID = mid
        self.KEYWORDS_LOW = low
        self.ALL_KEYWORDS = self.KEYWORDS_HIGH + self.KEYWORDS_MID + self.KEYWORDS_LOW

    def load_companies(self, path:str):
        df = pd.read_excel(path)
        return df

    def build_query(self, company: str):
        keyword_part = " OR ".join(self.ALL_KEYWORDS)
        return f'"{company}" ({keyword_part})'

    def serpapi_search(self, query:str):
        params = {
            "engine": "google",
            "q": query,
            "hl": "ja",
            "gl": "jp",
            "api_key": SERPAPI_KEY,
        }

        for attempt in range(6):
            try:
                search = GoogleSearch(params)
                results = search.get_dict()

                return results.get("organic_results", [])
            except RequestException:
                if attempt <  5:
                    print(f"No internet connection. Retrying in 10s (attempt {attempt + 1}/5)")
                    time.sleep(10)
                else:
                    print(f"Couldn't connect. Please try again later")
        return None

    def extract_found_keywords(self, results: list[dict]):
        found = dict()

        for r in results:
            text = (r.get("title", "") + " " + r.get("snippet", ""))
            for kw in self.ALL_KEYWORDS:
                if kw in text and not self.contains_negation(kw, text):
                    found.setdefault(kw, [])
                    found[kw].append(r)
        return found

    def extract_domain(self, url: str):
        netloc = urlparse(url).netloc.lower()
        return netloc.replace("www.", "")

    def is_blog_or_forum(self, domain:str, url:str):
        blog_domains = {"note.com", "ameblo.jp", "hatena.ne.jp", "fc2.com", "wordpress.com"}

        if domain in blog_domains:
            return True

        blog_indicators = ["/blog", "/entry", "/bbs", "/forum", "/thread"]
        return any(ind in url.lower() for ind in blog_indicators)

    def contains_negation(self, keyword, text):
        NEGATION_PATTERNS = [
            "ありません",
            "該当しません",
            "確認されていません",
            "デマ",
            "虚偽",
            "誤情報",
            "風評被害",
            "無関係",
            "回収",
            "取り扱い品目",
            "買取"
            "お問い合わせ",
            "ご相談",
            "お問い合わせ",
            "無料",
            "!"
        ]

        key_index = text.find(keyword)
        if key_index == -1:
            return False

        start = max(0, key_index - 30)
        end = key_index + len(keyword) + 50
        context = text[start:end]

        return any(pat in context for pat in NEGATION_PATTERNS)

    def classify_keyword(self, keyword):
        if keyword in self.KEYWORDS_HIGH:
            return WEIGHT_HIGH
        elif keyword in self.KEYWORDS_MID:
            return WEIGHT_MID
        elif keyword in self.KEYWORDS_LOW:
            return WEIGHT_LOW
        else: return 0

    def classify_risk(self, found_keywords: dict):
        total_score = 0
        hit_keywords = dict()

        for key, val in found_keywords.items():  # key: the keyword hit, val: how many sites the keyword was present
            score = self.classify_keyword(key)
            source_score = 0
            hit_keywords.setdefault(key, 0)
            domain_hits = set()
            for r in val:   # r: Request object of each site that contained the keyword
                link = r.get("link", "")
                domain = self.extract_domain(link)

                if domain in domain_hits:
                    continue

                if domain in TRUSTED_DOMAINS:
                    source_score += SOURCE_BONUS_TRUSTED
                elif self.is_blog_or_forum(domain, link):
                    source_score += SOURCE_PENALTY_LOW
                total_score  += score + source_score
                domain_hits.add(domain)
                hit_keywords[key] += 1

        total_score = max(total_score, 0)
        result = {"keys": hit_keywords}

        if total_score >= 9:
            result["risk"] = "高"
        elif total_score >= 5:
            result["risk"] = "中"
        elif total_score >= 3:
            result["risk"] = "低"
        else:
            result["risk"] = "なし"

        return result

    def write_output(self, df):
        df.to_excel("risk_result.xlsx", index=False)

    def main(self):
        if not SERPAPI_KEY:
            raise RuntimeError("SERPAPI_KEYがセットされていません。.envを開きセットしてください")

        df = self.load_companies(INPUT_FILE)

        if MAX_COMPANIES:
            df = df.head(MAX_COMPANIES)

        #for idx, row in df.iterrows():
        #    companies = row["取引先名"]
        #    pref = row["都道府県(請求先)"]
        #    tel = row["電話"]
        #    record_type = row["取引先レコードタイプ"]

        print(f"[INFO] {len(df)} 社　処理中...")

        df["危険度"] = ""

        for idx, row in enumerate(df.itertuples(index=False), start=1):
            company = row.取引先名
            print(f"[INFO] ({idx}/{len(df)}) {company}")

            query = self.build_query(company)
            search_results = self.serpapi_search(query)
            if search_results is None:
                sys.exit(1)

            found_keywords = self.extract_found_keywords(search_results)
            hit_keys, risk = self.classify_risk(found_keywords).values()

            display_key = ""
            for key, num in hit_keys.items():
                display_key += f"{key}{num}　"

            df.at[idx - 1, "危険度"] = risk
            df.at[idx - 1, "関連する可能性のあるワード"] = display_key

            time.sleep(SLEEP_TIME)

        self.write_output(df)
        print(f"[INFO] {OUTPUT_FILE} へ出力完了")


