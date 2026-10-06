"""
emoji_sentiment.py — polaritas emoji untuk komentar trailer film (EKSPLORATIF).

Pemetaan dibuat sendiri untuk konteks komentar trailer horor/komedi Indonesia:
- POSITIF : jelas memuji / antusias / sayang
- NEGATIF : jelas menolak / marah / jijik / bosan
- AMBIGU  : bisa pujian maupun ejekan/takut/terharu (😂 🤣 😅 😭 😢 😱 ...).
            Dihitung NETRAL (skor 0) agar tidak mendorong label ke arah mana pun,
            tetapi tetap dilaporkan terpisah.
Pemetaan ini perlu diuji lewat anotasi manual sebelum dijadikan klaim paper.
"""
import re

POS_EMOJI = set("❤ 🧡 💛 💚 💙 💜 🤍 🖤 💗 💖 💕 💞 💓 😍 🥰 😘 😊 ☺ 😁 😄 😃 🤩 🥳 🎉 🎊 👍 👏 🙌 🔥 💯 ⭐ 🌟 ✨ 🏆 🥇 👌 💪 🙏 😎 🤗".split())
NEG_EMOJI = set("👎 😡 😠 🤬 💩 😒 🙄 😤 😞 😔 🤮 🤢 😑 😐 🥱 😴 💔 ❌ 🚫 🤡".split())
AMB_EMOJI = set("😂 🤣 😅 😭 😢 😥 😱 😨 😰 😮 😯 😳 😟 😬 🙈 😆 😜 😝 🤪 👻 💀 ☠ 😈 👀".split())

try:
    import emoji as _emoji

    def extract(text):
        return [e["emoji"] for e in _emoji.emoji_list(str(text))]
except ImportError:  # cadangan tanpa pustaka emoji
    _RX = re.compile("[\U0001F1E6-\U0001F1FF]{2}|(?:[\U0001F300-\U0001FAFF☀-➿⭐❤♥]"
                     "[️\U0001F3FB-\U0001F3FF]?(?:‍[\U0001F300-\U0001FAFF☀-➿♀♂]️?)*)")

    def extract(text):
        return _RX.findall(str(text))


def _base(e):
    # buang variation selector & warna kulit agar ❤️ == ❤, 👍🏽 == 👍
    return re.sub("[️\U0001F3FB-\U0001F3FF]", "", e)


def emoji_score(text):
    """Kembalikan (skor, jumlah_emoji, jumlah_ambigu). Skor >0 positif, <0 negatif."""
    s, n, amb = 0, 0, 0
    for e in extract(text):
        b = _base(e)
        n += 1
        if b in POS_EMOJI:
            s += 1
        elif b in NEG_EMOJI:
            s -= 1
        elif b in AMB_EMOJI:
            amb += 1
    return s, n, amb


def emoji_label(text):
    s, n, _ = emoji_score(text)
    if n == 0:
        return "tanpa_emoji"
    return "positif" if s > 0 else "negatif" if s < 0 else "netral"


def has_letters(text):
    return bool(re.search(r"[A-Za-z]{2,}", str(text)))
