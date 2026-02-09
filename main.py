from checker import Checker
#Keyword Definition

KEYWORDS_HIGH = ["暴力団", "ヤクザ", "反社", "準構成員", "フロント企業", "闇"]

KEYWORDS_MID = ["逮捕","事件","訴訟","摘発","送検","容疑","傷害","殺人","窃盗","捜査","違反","違法","偽証","罪","処分","不正","詐欺","脱税","ブラック","架空"]

KEYWORDS_LOW = ["行政処分","行政指導","課徴金","右翼","左翼"]



a = Checker(KEYWORDS_HIGH, KEYWORDS_MID, KEYWORDS_LOW)
a.main()