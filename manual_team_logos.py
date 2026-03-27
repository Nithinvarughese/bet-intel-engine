"""
Static team and league badge URLs (TheSportsDB CDN — hotlink-friendly).

Add or edit entries here if API-Football names in your DB differ slightly;
`resolve_manual_team_logo_url` matches case-insensitively and checks aliases.
"""

from __future__ import annotations

# API-Football v3 league id -> league badge (sidebar)
MANUAL_LEAGUE_BADGE_URL: dict[int, str] = {
    39: "https://r2.thesportsdb.com/images/media/league/badge/gasy9d1737743125.png",
    140: "https://r2.thesportsdb.com/images/media/league/badge/ja4it51687628717.png",
    135: "https://r2.thesportsdb.com/images/media/league/badge/67q3q21679951383.png",
    78: "https://r2.thesportsdb.com/images/media/league/badge/teqh1b1679952008.png",
    61: "https://r2.thesportsdb.com/images/media/league/badge/9f7z9d1742983155.png",
}

# API-Football v3 league id -> { team_name: badge_url }
MANUAL_TEAM_LOGO_URL: dict[int, dict[str, str]] = {
    39: {
        "Arsenal": "https://r2.thesportsdb.com/images/media/team/badge/uyhbfe1612467038.png",
        "Aston Villa": "https://r2.thesportsdb.com/images/media/team/badge/jykrpv1717309891.png",
        "Bournemouth": "https://r2.thesportsdb.com/images/media/team/badge/y08nak1534071116.png",
        "Brentford": "https://r2.thesportsdb.com/images/media/team/badge/grv1aw1546453779.png",
        "Brighton": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Brighton_%26_Hove_Albion_logo.svg/200px-Brighton_%26_Hove_Albion_logo.svg.png",
        "Burnley": "https://r2.thesportsdb.com/images/media/team/badge/ql7nl31686893820.png",
        "Chelsea": "https://r2.thesportsdb.com/images/media/team/badge/yvwvtu1448813215.png",
        "Crystal Palace": "https://r2.thesportsdb.com/images/media/team/badge/ia6i3m1656014992.png",
        "Everton": "https://r2.thesportsdb.com/images/media/team/badge/eqayrf1523184794.png",
        "Fulham": "https://r2.thesportsdb.com/images/media/team/badge/xwwvyt1448811086.png",
        "Liverpool": "https://r2.thesportsdb.com/images/media/team/badge/kfaher1737969724.png",
        "Luton": "https://r2.thesportsdb.com/images/media/team/badge/v977eh1681319466.png",
        "Manchester City": "https://r2.thesportsdb.com/images/media/team/badge/vwpvry1467462651.png",
        "Manchester United": "https://r2.thesportsdb.com/images/media/team/badge/xzqdr11517660252.png",
        "Newcastle": "https://r2.thesportsdb.com/images/media/team/badge/aes2o51646347790.png",
        "Nottingham Forest": "https://r2.thesportsdb.com/images/media/team/badge/bk4qjs1546440351.png",
        "Sheffield Utd": "https://r2.thesportsdb.com/images/media/team/badge/w7f8pj1672950689.png",
        "Tottenham": "https://r2.thesportsdb.com/images/media/team/badge/dfyfhl1604094109.png",
        "West Ham": "https://r2.thesportsdb.com/images/media/team/badge/yutyxs1467459956.png",
        "Wolves": "https://r2.thesportsdb.com/images/media/team/badge/saimjk1656789616.png",
    },
    140: {
        "Real Madrid": "https://r2.thesportsdb.com/images/media/team/badge/vwvwrw1473502969.png",
        "Barcelona": "https://r2.thesportsdb.com/images/media/team/badge/wq9sir1639406443.png",
        "Atletico Madrid": "https://r2.thesportsdb.com/images/media/team/badge/0ulh3q1719984315.png",
        "Atlético Madrid": "https://r2.thesportsdb.com/images/media/team/badge/0ulh3q1719984315.png",
        "Girona": "https://r2.thesportsdb.com/images/media/team/badge/kfu7zu1659897499.png",
        "Real Sociedad": "https://r2.thesportsdb.com/images/media/team/badge/vptvpr1473502986.png",
        "Athletic Club": "https://r2.thesportsdb.com/images/media/team/badge/68w7fe1639408210.png",
        "Athletic Bilbao": "https://r2.thesportsdb.com/images/media/team/badge/68w7fe1639408210.png",
        "Valencia": "https://r2.thesportsdb.com/images/media/team/badge/dm8l6o1655594864.png",
        "Villarreal": "https://r2.thesportsdb.com/images/media/team/badge/vrypqy1473503073.png",
        "Getafe": "https://r2.thesportsdb.com/images/media/team/badge/eyh2891655594452.png",
        "Osasuna": "https://r2.thesportsdb.com/images/media/team/badge/rvspvt1473502960.png",
        "Real Betis": "https://r2.thesportsdb.com/images/media/team/badge/2oqulv1663245386.png",
        "Sevilla": "https://r2.thesportsdb.com/images/media/team/badge/vpsqqx1473502977.png",
        "Mallorca": "https://r2.thesportsdb.com/images/media/team/badge/ssptsx1473503730.png",
        "Celta Vigo": "https://r2.thesportsdb.com/images/media/team/badge/xfjtku1690436219.png",
        "Rayo Vallecano": "https://r2.thesportsdb.com/images/media/team/badge/nzhu941655595465.png",
        "Alaves": "https://r2.thesportsdb.com/images/media/team/badge/mfn99h1734673842.png",
        "Cadiz": "https://r2.thesportsdb.com/images/media/team/badge/e2phzp1639408503.png",
        "Cádiz": "https://r2.thesportsdb.com/images/media/team/badge/e2phzp1639408503.png",
        "Las Palmas": "https://r2.thesportsdb.com/images/media/team/badge/mmhyb11616443601.png",
        "Granada": "https://r2.thesportsdb.com/images/media/team/badge/f9iss11677472689.png",
        "Granada CF": "https://r2.thesportsdb.com/images/media/team/badge/f9iss11677472689.png",
        "Almeria": "https://r2.thesportsdb.com/images/media/team/badge/yswsww1473503818.png",
        "Almería": "https://r2.thesportsdb.com/images/media/team/badge/yswsww1473503818.png",
    },
    135: {
        "Inter": "https://r2.thesportsdb.com/images/media/team/badge/ryhu6d1617113103.png",
        "Inter Milan": "https://r2.thesportsdb.com/images/media/team/badge/ryhu6d1617113103.png",
        "AC Milan": "https://r2.thesportsdb.com/images/media/team/badge/wvspur1448806617.png",
        "Milan": "https://r2.thesportsdb.com/images/media/team/badge/wvspur1448806617.png",
        "Juventus": "https://r2.thesportsdb.com/images/media/team/badge/uxf0gr1742983727.png",
        "Napoli": "https://r2.thesportsdb.com/images/media/team/badge/l8qyxv1742982541.png",
        "Roma": "https://r2.thesportsdb.com/images/media/team/badge/jwro2s1760820674.png",
        "Lazio": "https://r2.thesportsdb.com/images/media/team/badge/rwqyvs1448806608.png",
        "Atalanta": "https://r2.thesportsdb.com/images/media/team/badge/lrvxg71534873930.png",
        "Fiorentina": "https://r2.thesportsdb.com/images/media/team/badge/hc8nhu1656098030.png",
        "Torino": "https://r2.thesportsdb.com/images/media/team/badge/xxprty1448806802.png",
        "Bologna": "https://r2.thesportsdb.com/images/media/team/badge/2qi1u31655592366.png",
        "Monza": "https://r2.thesportsdb.com/images/media/team/badge/bxearg1603170113.png",
        "Genoa": "https://r2.thesportsdb.com/images/media/team/badge/52s8dn1655553600.png",
        "Lecce": "https://r2.thesportsdb.com/images/media/team/badge/j4vznr1567365249.png",
        "Sassuolo": "https://r2.thesportsdb.com/images/media/team/badge/xystvp1448806138.png",
        "Udinese": "https://r2.thesportsdb.com/images/media/team/badge/vwvstr1448806811.png",
        "Verona": "https://r2.thesportsdb.com/images/media/team/badge/p6camf1593457737.png",
        "Hellas Verona": "https://r2.thesportsdb.com/images/media/team/badge/p6camf1593457737.png",
        "Empoli": "https://r2.thesportsdb.com/images/media/team/badge/c1ie6b1622561483.png",
        "Frosinone": "https://r2.thesportsdb.com/images/media/team/badge/a7xa151603170120.png",
        "Cagliari": "https://r2.thesportsdb.com/images/media/team/badge/wvsvxt1447534471.png",
        "Salernitana": "https://r2.thesportsdb.com/images/media/team/badge/nmi7mk1603170517.png",
        "Como": "https://r2.thesportsdb.com/images/media/team/badge/02x81t1627405841.png",
        "Parma": "https://r2.thesportsdb.com/images/media/team/badge/6yiaxs1627406063.png",
        "Venezia": "https://r2.thesportsdb.com/images/media/team/badge/95fg4n1656696080.png",
    },
    78: {
        "Bayern Munich": "https://r2.thesportsdb.com/images/media/team/badge/01ogkh1716960412.png",
        "Bayern München": "https://r2.thesportsdb.com/images/media/team/badge/01ogkh1716960412.png",
        "Borussia Dortmund": "https://r2.thesportsdb.com/images/media/team/badge/tqo8ge1716960353.png",
        "RB Leipzig": "https://r2.thesportsdb.com/images/media/team/badge/zjgapo1594244951.png",
        "Bayer Leverkusen": "https://r2.thesportsdb.com/images/media/team/badge/3x9k851726760113.png",
        "Eintracht Frankfurt": "https://r2.thesportsdb.com/images/media/team/badge/rurwpy1473453269.png",
        "Wolfsburg": "https://r2.thesportsdb.com/images/media/team/badge/07kp421599680274.png",
        "Freiburg": "https://r2.thesportsdb.com/images/media/team/badge/urwtup1473453288.png",
        "Union Berlin": "https://r2.thesportsdb.com/images/media/team/badge/q0o5001599679795.png",
        "Borussia Monchengladbach": "https://r2.thesportsdb.com/images/media/team/badge/sysurw1473453380.png",
        "Borussia Mönchengladbach": "https://r2.thesportsdb.com/images/media/team/badge/sysurw1473453380.png",
        "Mainz": "https://r2.thesportsdb.com/images/media/team/badge/fhm9v51552134916.png",
        "Hoffenheim": "https://r2.thesportsdb.com/images/media/team/badge/9hwvb21621593919.png",
        "Augsburg": "https://r2.thesportsdb.com/images/media/team/badge/xqyyvq1473453233.png",
        "FC Augsburg": "https://r2.thesportsdb.com/images/media/team/badge/xqyyvq1473453233.png",
        "Stuttgart": "https://r2.thesportsdb.com/images/media/team/badge/yppyux1473454085.png",
        "VfB Stuttgart": "https://r2.thesportsdb.com/images/media/team/badge/yppyux1473454085.png",
        "Werder Bremen": "https://r2.thesportsdb.com/images/media/team/badge/tkvqan1716960454.png",
        "Heidenheim": "https://r2.thesportsdb.com/images/media/team/badge/lbj7g01608236988.png",
        "FC Heidenheim": "https://r2.thesportsdb.com/images/media/team/badge/lbj7g01608236988.png",
        "Darmstadt": "https://r2.thesportsdb.com/images/media/team/badge/5f3dyd1608236981.png",
        "Holstein Kiel": "https://r2.thesportsdb.com/images/media/team/badge/1fpmgs1514394524.png",
        "Bochum": "https://r2.thesportsdb.com/images/media/team/badge/kag3jy1599821108.png",
        "Koln": "https://r2.thesportsdb.com/images/media/team/badge/2j1sc91566049407.png",
        "Köln": "https://r2.thesportsdb.com/images/media/team/badge/2j1sc91566049407.png",
        "FC Köln": "https://r2.thesportsdb.com/images/media/team/badge/2j1sc91566049407.png",
    },
    61: {
        "Paris Saint Germain": "https://r2.thesportsdb.com/images/media/team/badge/rwqrrq1473504808.png",
        "Paris SG": "https://r2.thesportsdb.com/images/media/team/badge/rwqrrq1473504808.png",
        "PSG": "https://r2.thesportsdb.com/images/media/team/badge/rwqrrq1473504808.png",
        "Marseille": "https://r2.thesportsdb.com/images/media/team/badge/uutsyt1473504764.png",
        "Monaco": "https://r2.thesportsdb.com/images/media/team/badge/exjf5l1678808044.png",
        "Lyon": "https://r2.thesportsdb.com/images/media/team/badge/blk9771656932845.png",
        "Lille": "https://r2.thesportsdb.com/images/media/team/badge/2giize1534005340.png",
        "Lens": "https://r2.thesportsdb.com/images/media/team/badge/3pxoum1598797195.png",
        "Nice": "https://r2.thesportsdb.com/images/media/team/badge/msy7ly1621593859.png",
        "Rennes": "https://r2.thesportsdb.com/images/media/team/badge/ypturx1473504818.png",
        "Toulouse": "https://r2.thesportsdb.com/images/media/team/badge/17eqox1688449282.png",
        "Reims": "https://r2.thesportsdb.com/images/media/team/badge/l5rr1n1637315636.png",
        "Montpellier": "https://r2.thesportsdb.com/images/media/team/badge/8wn9x31750879448.png",
        "Strasbourg": "https://r2.thesportsdb.com/images/media/team/badge/b8k77w1766625501.png",
        "Nantes": "https://r2.thesportsdb.com/images/media/team/badge/mla9x61678808018.png",
        "Le Havre": "https://r2.thesportsdb.com/images/media/team/badge/aikowk1546475003.png",
        "Metz": "https://r2.thesportsdb.com/images/media/team/badge/1iuew61688452857.png",
        "Brest": "https://r2.thesportsdb.com/images/media/team/badge/z69be41598797026.png",
        "Clermont Foot": "https://r2.thesportsdb.com/images/media/team/badge/wrytst1426871249.png",
        "Lorient": "https://r2.thesportsdb.com/images/media/team/badge/sxsttw1473504748.png",
        "Angers": "https://r2.thesportsdb.com/images/media/team/badge/ix6q4w1678808069.png",
        "Auxerre": "https://r2.thesportsdb.com/images/media/team/badge/lzdtbf1658753355.png",
    },
}

# Optional: map alternate DB strings -> canonical key in MANUAL_TEAM_LOGO_URL[league_id]
TEAM_NAME_ALIASES: dict[int, dict[str, str]] = {
    39: {
        "sheffield united": "Sheffield Utd",
        "sheffield utd": "Sheffield Utd",
        "wolverhampton wanderers": "Wolves",
        "wolverhampton": "Wolves",
        "tottenham hotspur": "Tottenham",
        "west ham united": "West Ham",
        "brighton and hove albion": "Brighton",
        "nottingham forest": "Nottingham Forest",
        "newcastle united": "Newcastle",
        "manchester utd": "Manchester United",
        "man united": "Manchester United",
        "man city": "Manchester City",
    },
    140: {
        "deportivo alaves": "Alaves",
        "deportivo alavés": "Alaves",
        "club atletico de madrid": "Atletico Madrid",
        "granada cf": "Granada CF",
        "ud almeria": "Almeria",
        "ud almería": "Almeria",
    },
    135: {
        "internazionale": "Inter",
        "fc internazionale milano": "Inter",
        "as roma": "Roma",
        "ssc napoli": "Napoli",
        "ss lazio": "Lazio",
        "atalanta bc": "Atalanta",
        "acf fiorentina": "Fiorentina",
        "torino fc": "Torino",
        "bologna fc": "Bologna",
        "ac monza": "Monza",
        "genoa cfc": "Genoa",
        "us lecce": "Lecce",
        "us sassuolo": "Sassuolo",
        "udinese calcio": "Udinese",
        "empoli fc": "Empoli",
        "cagliari calcio": "Cagliari",
        "us salernitana": "Salernitana",
        "como 1907": "Como",
    },
    78: {
        "fc bayern munchen": "Bayern Munich",
        "fc bayern münchen": "Bayern Munich",
        "bvb": "Borussia Dortmund",
        "1. fc union berlin": "Union Berlin",
        "1. fsv mainz 05": "Mainz",
        "fsv mainz 05": "Mainz",
        "tsg hoffenheim": "Hoffenheim",
        "1. fc heidenheim": "FC Heidenheim",
        "sv darmstadt 98": "Darmstadt",
        "vfl bochum": "Bochum",
        "1. fc koln": "FC Köln",
        "1. fc köln": "FC Köln",
    },
    61: {
        "paris saint-germain": "Paris SG",
        "olympique marseille": "Marseille",
        "olympique lyonnais": "Lyon",
        "olympique lyon": "Lyon",
        "lille osc": "Lille",
        "rc lens": "Lens",
        "ogc nice": "Nice",
        "stade rennais": "Rennes",
        "stade rennais fc": "Rennes",
        "toulouse fc": "Toulouse",
        "stade de reims": "Reims",
        "montpellier hsc": "Montpellier",
        "rc strasbourg": "Strasbourg",
        "rc strasbourg alsace": "Strasbourg",
        "fc nantes": "Nantes",
        "le havre ac": "Le Havre",
        "fc metz": "Metz",
        "stade brestois": "Brest",
        "stade brestois 29": "Brest",
        "clermont foot 63": "Clermont Foot",
        "fc lorient": "Lorient",
        "angers sco": "Angers",
        "aj auxerre": "Auxerre",
    },
}


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def resolve_manual_team_logo_url(league_id: int, team_name: str) -> str | None:
    table = MANUAL_TEAM_LOGO_URL.get(league_id)
    if not table or not team_name:
        return None
    name = team_name.strip()
    if name in table:
        return table[name]
    aliases = TEAM_NAME_ALIASES.get(league_id, {})
    canon = aliases.get(_norm(name))
    if canon and canon in table:
        return table[canon]
    nl = _norm(name)
    for k, url in table.items():
        if _norm(k) == nl:
            return url
    return None


def manual_league_badge_url(league_id: int) -> str | None:
    return MANUAL_LEAGUE_BADGE_URL.get(league_id)
