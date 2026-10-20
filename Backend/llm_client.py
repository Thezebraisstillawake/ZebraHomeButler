import httpx
import re

from config import settings
from schemas import ChatRequest, ChatResponse

SYSTEM_PROMPT = (
    "你是 StudyMate，一个专业的 AI 英语学习助手。"
    "用户问中文单词时，你给出英文翻译并标注音标和例句；"
    "用户问英文单词时，你给出中文释义、音标和例句。"
    "回答格式清晰有条理，例句简短实用。"
)

ANIMAL_DICT = {
    "狗": "dog", "小狗": "dog", "犬": "dog",
    "猫": "cat", "小猫": "cat", "猫咪": "cat",
    "兔子": "rabbit", "兔": "rabbit",
    "马": "horse", "小马": "horse",
    "牛": "cow", "奶牛": "cow",
    "猪": "pig", "小猪": "pig",
    "羊": "sheep", "绵羊": "sheep",
    "山羊": "goat",
    "鸡": "chicken", "小鸡": "chicken",
    "鸭子": "duck", "鸭": "duck",
    "鹅": "goose",
    "鸟": "bird",
    "鱼": "fish",
    "鲨鱼": "shark",
    "海豚": "dolphin",
    "鲸鱼": "whale",
    "青蛙": "frog",
    "乌龟": "turtle", "龟": "turtle",
    "蛇": "snake",
    "蜥蜴": "lizard",
    "蜘蛛": "spider",
    "蜜蜂": "bee",
    "蝴蝶": "butterfly",
    "蚂蚁": "ant",
    "大象": "elephant",
    "狮子": "lion",
    "老虎": "tiger",
    "熊猫": "panda",
    "熊猫": "panda",
    "熊": "bear",
    "熊": "bear",
    "猴子": "monkey",
    "猩猩": "gorilla",
    "长颈鹿": "giraffe",
    "斑马": "zebra",
    "狐狸": "fox",
    "狼": "wolf",
    "考拉": "koala",
    "袋鼠": "kangaroo",
    "鳄鱼": "crocodile",
    "企鹅": "penguin",
    "猫头鹰": "owl",
    "鹦鹉": "parrot",
    "孔雀": "peacock",
    "松鼠": "squirrel",
    "刺猬": "hedgehog",
    "鹿": "deer",
    "骆驼": "camel",
    "犀牛": "rhinoceros",
    "河马": "hippopotamus",
    "豹子": "leopard",
    "美洲豹": "jaguar",
    "水獭": "otter",
    "海象": "walrus",
    "海豹": "seal",
    "章鱼": "octopus",
    "水母": "jellyfish",
    "珊瑚": "coral",
    "龙虾": "lobster",
    "螃蟹": "crab",
    "虾": "shrimp",
    "蜗牛": "snail",
    "蚯蚓": "earthworm",
    "蜻蜓": "dragonfly",
    "萤火虫": "firefly",
    "瓢虫": "ladybug",
}

WORD_DICT = {
    "苹果": "apple", "香蕉": "banana", "橙子": "orange", "葡萄": "grape",
    "西瓜": "watermelon", "草莓": "strawberry", "樱桃": "cherry",
    "芒果": "mango", "菠萝": "pineapple", "梨": "pear",
    "桃子": "peach", "柠檬": "lemon", "椰子": "coconut",
    "胡萝卜": "carrot", "西红柿": "tomato", "土豆": "potato",
    "黄瓜": "cucumber", "白菜": "cabbage", "洋葱": "onion",
    "大米": "rice", "面包": "bread", "鸡蛋": "egg",
    "牛奶": "milk", "水": "water", "咖啡": "coffee", "茶": "tea",
    "书": "book", "笔": "pen", "桌子": "desk", "椅子": "chair",
    "电脑": "computer", "手机": "phone", "电视": "TV",
    "太阳": "sun", "月亮": "moon", "星星": "star", "天空": "sky",
    "云": "cloud", "雨": "rain", "雪": "snow", "风": "wind",
    "山": "mountain", "河": "river", "海": "sea", "湖": "lake",
    "花": "flower", "树": "tree", "草": "grass", "叶子": "leaf",
    "爸爸": "father", "妈妈": "mother", "哥哥": "brother", "姐姐": "sister",
    "老师": "teacher", "学生": "student", "医生": "doctor", "护士": "nurse",
    "警察": "police", "司机": "driver", "厨师": "chef",
    "红色": "red", "蓝色": "blue", "绿色": "green", "黄色": "yellow",
    "黑色": "black", "白色": "white", "粉色": "pink", "紫色": "purple",
    "大": "big", "小": "small", "高": "tall", "矮": "short",
    "快": "fast", "慢": "slow", "胖": "fat", "瘦": "thin",
    "爱": "love", "喜欢": "like", "吃": "eat", "喝": "drink",
    "睡": "sleep", "跑": "run", "走": "walk", "跳": "jump",
    "看": "look", "听": "listen", "说": "say", "读": "read",
    "写": "write", "玩": "play", "工作": "work", "学习": "study",
}

ALL_DICT = {**ANIMAL_DICT, **WORD_DICT}

EN_TO_CN = {v: k for k, v in ALL_DICT.items()}

PHONETICS = {
    "dog": "/dɒɡ/", "cat": "/kæt/", "rabbit": "/ˈræbɪt/",
    "horse": "/hɔːs/", "cow": "/kaʊ/", "pig": "/pɪɡ/",
    "sheep": "/ʃiːp/", "chicken": "/ˈtʃɪkɪn/", "duck": "/dʌk/",
    "bird": "/bɜːd/", "fish": "/fɪʃ/", "elephant": "/ˈelɪfənt/",
    "lion": "/ˈlaɪən/", "tiger": "/ˈtaɪɡə(r)/", "panda": "/ˈpændə/",
    "bear": "/beə(r)/", "monkey": "/ˈmʌŋki/", "fox": "/fɒks/",
    "apple": "/ˈæpl/", "banana": "/bəˈnɑːnə/", "orange": "/ˈɒrɪndʒ/",
    "grape": "/ɡreɪp/", "watermelon": "/ˈwɔːtəmelən/",
    "book": "/bʊk/", "pen": "/pen/", "desk": "/desk/",
    "sun": "/sʌn/", "moon": "/muːn/", "star": "/stɑː(r)/",
    "love": "/lʌv/", "like": "/laɪk/", "eat": "/iːt/",
}

EXAMPLES = {
    "dog": "The dog is playing in the park.",
    "cat": "My cat loves to sleep on the sofa.",
    "rabbit": "The rabbit is eating carrots.",
    "apple": "I eat an apple every day.",
    "book": "This book is very interesting.",
    "sun": "The sun is shining brightly.",
    "love": "I love my family very much.",
    "school": "I go to school by bus.",
}


def build_reply(word_cn: str, word_en: str) -> str:
    phonetic = PHONETICS.get(word_en, "")
    example = EXAMPLES.get(word_en, f"I like {word_en.capitalize()} very much!")
    lines = [
        f"**{word_cn}** 的英文是：**{word_en}**",
    ]
    if phonetic:
        lines.append(f"📖 音标：{phonetic}")
    lines.append(f"💬 例句：{example}")
    lines.append("")
    lines.append("还需要我帮你翻译其他单词吗？😊")
    return "\n".join(lines)


def build_reply_en(word_en: str, word_cn: str) -> str:
    phonetic = PHONETICS.get(word_en, "")
    example = EXAMPLES.get(word_en, f"I like {word_en.capitalize()} very much!")
    lines = [
        f"**{word_en}** 的中文是：**{word_cn}**",
    ]
    if phonetic:
        lines.append(f"📖 音标：{phonetic}")
    lines.append(f"💬 例句：{example}")
    lines.append("")
    lines.append("还需要我帮你翻译其他单词吗？😊")
    return "\n".join(lines)


def offline_chat(message: str) -> str | None:
    msg = message.strip()
    msg_lower = msg.lower()

    if msg_lower in EN_TO_CN:
        cn = EN_TO_CN[msg_lower]
        return build_reply_en(msg_lower, cn)

    if msg in ALL_DICT:
        en = ALL_DICT[msg]
        return build_reply(msg, en)

    cn_match = re.search(r'[\u4e00-\u9fff]+', msg)
    if cn_match:
        for key, val in ALL_DICT.items():
            if key in msg:
                return build_reply(key, val)

    en_words = re.findall(r'[a-zA-Z]+', msg)
    for word in en_words:
        wl = word.lower()
        if wl in EN_TO_CN:
            return build_reply_en(wl, EN_TO_CN[wl])

    return None


async def call_llm(req: ChatRequest) -> ChatResponse:
    api_key = settings.llm_api_key
    is_valid_key = api_key and not api_key.startswith("sk-your")

    if not is_valid_key:
        offline = offline_chat(req.message)
        if offline:
            return ChatResponse(reply=offline)
        return ChatResponse(
            reply=(
                "⚠️ 当前使用离线模式，API Key 未配置。\n\n"
                "你可以提问常见的中/英文单词翻译。\n"
                "如需完整 AI 能力，请在 Backend/config.py 中配置有效的 API Key。"
            )
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.message},
        ],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.llm_api_url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        reply = data["choices"][0]["message"]["content"]
        return ChatResponse(reply=reply.strip())
    except Exception:
        offline = offline_chat(req.message)
        if offline:
            return ChatResponse(reply=f"（离线词典回复）\n\n{offline}")
        return ChatResponse(
            reply="抱歉，LLM 服务暂时不可用，离线词典也未找到相关内容 😢"
        )