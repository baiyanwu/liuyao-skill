#!/usr/bin/env python3
"""
六爻纳甲占卜引擎 - 传统京房八宫体系
完整流程：起卦 → 纳甲 → 装六亲 → 安六神 → 定世应 → 查空亡月破 → 输出排盘
"""

import random
import datetime
import json
import sys
import os

# ============================================================
# 八卦基础数据
# ============================================================

BAGUA = {
    '乾': (1, 1, 1), '兑': (0, 1, 1), '离': (1, 0, 1), '震': (0, 0, 1),
    '巽': (1, 1, 0), '坎': (0, 1, 0), '艮': (1, 0, 0), '坤': (0, 0, 0),
}

BAGUA_WUXING = {
    '乾': '金', '兑': '金', '离': '火', '震': '木',
    '巽': '木', '坎': '水', '艮': '土', '坤': '土',
}

# ============================================================
# 纳甲数据 (京房易传)
# ============================================================

NAYUE_TIANGAN = {
    '乾': ('甲', '壬'), '震': ('庚', '庚'), '坎': ('戊', '戊'), '艮': ('丙', '丙'),
    '坤': ('乙', '癸'), '巽': ('辛', '辛'), '离': ('己', '己'), '兑': ('丁', '丁'),
}

NAYUE_DIZHI_INNER = {  # 内卦地支 (初爻→三爻)
    '乾': ['子', '寅', '辰'],
    '震': ['子', '寅', '辰'],
    '坎': ['寅', '辰', '午'],
    '艮': ['辰', '午', '申'],
    '坤': ['未', '巳', '卯'],
    '巽': ['丑', '亥', '酉'],
    '离': ['卯', '丑', '亥'],
    '兑': ['巳', '卯', '丑'],
}

NAYUE_DIZHI_OUTER = {  # 外卦地支 (四爻→上爻)
    '乾': ['午', '申', '戌'],
    '震': ['午', '申', '戌'],
    '坎': ['申', '戌', '子'],
    '艮': ['戌', '子', '寅'],
    '坤': ['丑', '亥', '酉'],
    '巽': ['未', '巳', '卯'],
    '离': ['酉', '未', '巳'],
    '兑': ['亥', '酉', '未'],
}

DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# ============================================================
# 京房八宫六十四卦
# ============================================================

PALACE_CHART = {
    '乾': {
        '五行': '金',
        '卦序': ['乾为天', '天风姤', '天山遁', '天地否', '风地观', '山地剥', '火地晋', '火天大有'],
        '上下卦': [('乾','乾'), ('巽','乾'), ('艮','乾'), ('坤','乾'), ('坤','巽'), ('坤','艮'), ('离','坤'), ('乾','离')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '兑': {
        '五行': '金',
        '卦序': ['兑为泽', '泽水困', '泽地萃', '泽山咸', '水山蹇', '地山谦', '雷山小过', '雷泽归妹'],
        '上下卦': [('兑','兑'), ('坎','兑'), ('坤','兑'), ('艮','兑'), ('艮','坎'), ('艮','坤'), ('艮','震'), ('兑','震')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '离': {
        '五行': '火',
        '卦序': ['离为火', '火山旅', '火风鼎', '火水未济', '山水蒙', '风水涣', '天水讼', '天火同人'],
        '上下卦': [('离','离'), ('艮','离'), ('巽','离'), ('坎','离'), ('坎','艮'), ('坎','巽'), ('坎','乾'), ('离','乾')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '震': {
        '五行': '木',
        '卦序': ['震为雷', '雷地豫', '雷水解', '雷风恒', '地风升', '水风井', '泽风大过', '泽雷随'],
        '上下卦': [('震','震'), ('坤','震'), ('坎','震'), ('巽','震'), ('巽','坤'), ('巽','坎'), ('巽','兑'), ('震','兑')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '巽': {
        '五行': '木',
        '卦序': ['巽为风', '风天小畜', '风火家人', '风雷益', '天雷无妄', '火雷噬嗑', '山雷颐', '山风蛊'],
        '上下卦': [('巽','巽'), ('乾','巽'), ('离','巽'), ('震','巽'), ('震','乾'), ('震','离'), ('震','艮'), ('巽','艮')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '坎': {
        '五行': '水',
        '卦序': ['坎为水', '水泽节', '水雷屯', '水火既济', '泽火革', '雷火丰', '地火明夷', '地水师'],
        '上下卦': [('坎','坎'), ('兑','坎'), ('震','坎'), ('离','坎'), ('离','兑'), ('离','震'), ('离','坤'), ('坎','坤')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '艮': {
        '五行': '土',
        '卦序': ['艮为山', '山火贲', '山天大畜', '山泽损', '火泽睽', '天泽履', '风泽中孚', '风山渐'],
        '上下卦': [('艮','艮'), ('离','艮'), ('乾','艮'), ('兑','艮'), ('兑','离'), ('兑','乾'), ('兑','巽'), ('艮','巽')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
    '坤': {
        '五行': '土',
        '卦序': ['坤为地', '地雷复', '地泽临', '地天泰', '雷天大壮', '泽天夬', '水天需', '水地比'],
        '上下卦': [('坤','坤'), ('震','坤'), ('兑','坤'), ('乾','坤'), ('乾','震'), ('乾','兑'), ('乾','坎'), ('坤','坎')],
        '世位': [5, 0, 1, 2, 3, 4, 3, 2],
    },
}

# 构建快速查找表
HEXAGRAM_DB = {}
for palace_name, palace_info in PALACE_CHART.items():
    palace_wx = palace_info['五行']
    for i, gua_name in enumerate(palace_info['卦序']):
        shang, xia = palace_info['上下卦'][i]
        shi_pos = palace_info['世位'][i]
        ying_pos = (shi_pos + 3) % 6
        shi_yao_type = '本宫' if i == 0 else ['一世','二世','三世','四世','五世','游魂','归魂'][i-1]
        HEXAGRAM_DB[gua_name] = {
            '宫': palace_name, '五行': palace_wx,
            '上卦': shang, '下卦': xia,
            '世位': shi_pos, '应位': ying_pos, '卦型': shi_yao_type,
        }

# ============================================================
# 六神
# ============================================================
LIUSHEN_ORDER = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

RIUGAN_LIUSHEN_START = {
    '甲': 0, '乙': 0, '丙': 1, '丁': 1, '戊': 2,
    '己': 3, '庚': 4, '辛': 4, '壬': 5, '癸': 5,
}

# ============================================================
# 五行生克
# ============================================================
TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI_LIST = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

SHENG = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}

def get_liuqin(yao_wx, palace_wx):
    if yao_wx == palace_wx: return '兄弟'
    generate = {'金':'土','水':'金','木':'水','火':'木','土':'火'}
    if generate[palace_wx] == yao_wx: return '父母'
    if generate[yao_wx] == palace_wx: return '子孙'
    overcome = {'金':'火','水':'土','木':'金','火':'水','土':'木'}
    if overcome[palace_wx] == yao_wx: return '官鬼'
    if overcome[yao_wx] == palace_wx: return '妻财'
    return '??'

def wuxing_relation(wo, ta):
    if wo == ta: return '同'
    generate = {'金':'土','水':'金','木':'水','火':'木','土':'火'}
    if generate[wo] == ta: return '生我'
    if generate[ta] == wo: return '我生'
    overcome = {'金':'火','水':'土','木':'金','火':'水','土':'木'}
    if overcome[wo] == ta: return '克我'
    if overcome[ta] == wo: return '我克'
    return '??'

# ============================================================
# 起卦
# ============================================================
def cast_coins():
    heads = sum(random.randint(0, 1) for _ in range(3))
    if heads == 3: return 9
    elif heads == 0: return 6
    elif heads == 2: return 7
    else: return 8

def cast_hexagram():
    return [cast_coins() for _ in range(6)]

def values_to_binary(values):
    return [1 if v in (7, 9) else 0 for v in values]

def get_trigram(yaos):
    return next((n for n, b in BAGUA.items() if b == tuple(yaos)), None)

def get_hexagram_name(y6):
    xia = get_trigram(y6[0:3])
    shang = get_trigram(y6[3:6])
    for name, info in HEXAGRAM_DB.items():
        if info['下卦'] == xia and info['上卦'] == shang:
            return name
    return None

# ============================================================
# 干支与空亡
# ============================================================
def get_ganzhi_today(dt=None):
    if dt is None: dt = datetime.datetime.now()
    base = datetime.date(2000, 1, 1)  # 2000-01-01 = 甲辰日
    target = dt.date() if isinstance(dt, datetime.datetime) else dt
    days = (target - base).days
    # 2000-01-01 甲辰: 天干甲(0), 地支辰(4)
    tg_idx = (0 + days) % 10
    dz_idx = (4 + days) % 12
    return TIANGAN[tg_idx], DIZHI_LIST[dz_idx]

def get_kongwang(ri_tg, ri_dz):
    tg_idx = TIANGAN.index(ri_tg)
    dz_idx = DIZHI_LIST.index(ri_dz)
    xun_start = (dz_idx - tg_idx) % 12
    return (DIZHI_LIST[(xun_start + 10) % 12], DIZHI_LIST[(xun_start + 11) % 12])

def get_month_dizhi(dt=None):
    if dt is None: dt = datetime.datetime.now()
    m = dt.month
    return {1:'丑',2:'寅',3:'卯',4:'辰',5:'巳',6:'午',7:'未',8:'申',9:'酉',10:'戌',11:'亥',12:'子'}.get(m, '子')

CHONG = {'子':'午','丑':'未','寅':'申','卯':'酉','辰':'戌','巳':'亥',
         '午':'子','未':'丑','申':'寅','酉':'卯','戌':'辰','亥':'巳'}

def is_yuepo(yao_dz, yue_dz):
    return CHONG.get(yao_dz) == yue_dz

def is_rikong(yao_dz, kongwang):
    return yao_dz in kongwang

# ============================================================
# 装卦 (核心)
# ============================================================
def assemble_hexagram(values, question="", dt=None):
    if dt is None: dt = datetime.datetime.now()

    yinyang = values_to_binary(values)
    has_dong = any(v in (6, 9) for v in values)

    bianyinyang = list(yinyang)
    moving_indices = []
    for i, v in enumerate(values):
        if v == 9:
            bianyinyang[i] = 0
            moving_indices.append(i)
        elif v == 6:
            bianyinyang[i] = 1
            moving_indices.append(i)

    ben_gua = get_hexagram_name(yinyang)
    bian_gua = get_hexagram_name(bianyinyang) if has_dong else None

    if ben_gua is None or ben_gua not in HEXAGRAM_DB:
        return {'error': f'无法识别卦象', 'yinyang': yinyang}

    info = HEXAGRAM_DB[ben_gua]
    palace_name = info['宫']
    palace_wx = info['五行']

    ri_tg, ri_dz = get_ganzhi_today(dt)
    yue_dz = get_month_dizhi(dt)
    kongwang = get_kongwang(ri_tg, ri_dz)

    liushen_start = RIUGAN_LIUSHEN_START.get(ri_tg, 0)
    liushen = [LIUSHEN_ORDER[(liushen_start + i) % 6] for i in range(6)]

    xia_gua, shang_gua = info['下卦'], info['上卦']
    yao_list = []
    for i in range(6):
        gua = xia_gua if i < 3 else shang_gua
        tg_idx = 0 if i < 3 else 1
        tg = NAYUE_TIANGAN[gua][tg_idx]
        if i < 3:
            dz = NAYUE_DIZHI_INNER[gua][i]
        else:
            dz = NAYUE_DIZHI_OUTER[gua][i - 3]
        yao_wx = DIZHI_WUXING[dz]
        liuqin = get_liuqin(yao_wx, palace_wx)
        is_moving = i in moving_indices
        is_kong = is_rikong(dz, kongwang)
        is_po = is_yuepo(dz, yue_dz)
        markers = []
        if i == info['世位']: markers.append('世')
        if i == info['应位']: markers.append('应')
        if is_moving: markers.append('动')
        if is_kong: markers.append('空')
        if is_po: markers.append('月破')

        yao_list.append({
            '位置': i, '爻位名': ['初爻','二爻','三爻','四爻','五爻','上爻'][i],
            '天干': tg, '地支': dz, '五行': yao_wx,
            '六亲': liuqin, '六神': liushen[i],
            '世应': '世' if i == info['世位'] else ('应' if i == info['应位'] else ''),
            '动爻': is_moving, '空亡': is_kong, '月破': is_po,
            '标记': markers, '阴阳': yinyang[i], '爻值': values[i],
        })

    bian_info = None
    if bian_gua and bian_gua in HEXAGRAM_DB:
        bd = HEXAGRAM_DB[bian_gua]
        bian_yaos = []
        for i in range(6):
            gua = bd['下卦'] if i < 3 else bd['上卦']
            tg = NAYUE_TIANGAN[gua][0 if i < 3 else 1]
            if i < 3:
                dz = NAYUE_DIZHI_INNER[gua][i]
            else:
                dz = NAYUE_DIZHI_OUTER[gua][i - 3]
            wx = DIZHI_WUXING[dz]
            bian_yaos.append({'位置': i, '天干': tg, '地支': dz, '五行': wx, '六亲': get_liuqin(wx, bd['五行']), '阴阳': bianyinyang[i]})
        bian_info = {'卦名': bian_gua, '宫': bd['宫'], '五行': bd['五行'], '爻象': bian_yaos}

    return {
        '问题': question, '时间': dt.strftime('%Y-%m-%d %H:%M'),
        '日干支': ri_tg + ri_dz, '月建': yue_dz, '空亡': kongwang,
        '本卦': ben_gua, '变卦': bian_gua,
        '宫': palace_name, '宫五行': palace_wx, '卦型': info['卦型'],
        '爻象': yao_list, '变卦详情': bian_info,
        '动爻位': moving_indices, '世位': info['世位'], '应位': info['应位'],
    }

# ============================================================
# 输出
# ============================================================
def format_hexagram_brief(result):
    """简略排盘（默认）"""
    if 'error' in result: return f"错误: {result['error']}"

    lines = []
    lines.append("=" * 52)
    lines.append("  六爻排盘")
    lines.append("=" * 52)
    if result['问题']:
        lines.append(f"  占事: {result['问题']}")
    lines.append(f"  时间: {result['时间']}")
    lines.append(f"  日辰: {result['日干支']}  月建: {result['月建']}建  空亡: {', '.join(result['空亡'])}")
    lines.append(f"  本卦: {result['本卦']} ({result['宫']}宫{result['卦型']})")
    if result['变卦']:
        lines.append(f"  变卦: {result['变卦']}")
    lines.append("")
    lines.append(f"  {'爻位':<5} {'六神':<5} {'六亲':<5} {'干支':<5} {'五行':<3} {'世应':<2}  卦象")
    lines.append("  " + "-" * 50)
    for yao in reversed(result['爻象']):
        gc = yao['天干'] + yao['地支']
        symbol = '━━━' if yao['阴阳'] == 1 else '━ ━'
        if yao['爻值'] == 9: symbol = '━━○'
        elif yao['爻值'] == 6: symbol = '━×━'
        mark = ' '.join(yao['标记'])
        lines.append(f"  {yao['六神']:<5} {yao['六亲']:<5} {gc:<5} {yao['五行']:<3} {yao['世应']:<2}  {symbol}  {mark}")
    lines.append("")

    shi = result['爻象'][result['世位']]
    ying = result['爻象'][result['应位']]
    lines.append(f"  世: {shi['六亲']} {shi['天干']}{shi['地支']}({shi['五行']})  应: {ying['六亲']} {ying['天干']}{ying['地支']}({ying['五行']})")
    lines.append("")

    kong = [y for y in result['爻象'] if y['空亡']]
    po = [y for y in result['爻象'] if y['月破']]
    if kong:
        lines.append("  空亡爻: " + ", ".join(f"{y['六亲']}{y['地支']}" for y in kong))
    if po:
        lines.append("  月破爻: " + ", ".join(f"{y['六亲']}{y['地支']}" for y in po))
    if result['动爻位']:
        lines.append("  动爻: " + ", ".join(
            f"{['初','二','三','四','五','上'][i]}爻({result['爻象'][i]['六亲']}{result['爻象'][i]['地支']})"
            for i in result['动爻位']
        ))

    lines.append("=" * 52)
    return "\n".join(lines)


YAO_VALUE_NAMES = {
    6: '老阴 (阴动爻, 阴→阳变)',
    7: '少阳 (静阳爻)',
    8: '少阴 (静阴爻)',
    9: '老阳 (阳动爻, 阳→阴变)',
}

def format_hexagram(result):
    if 'error' in result: return f"错误: {result['error']}"

    lines = []

    # ===== 第一步：起卦 =====
    lines.append("=" * 58)
    lines.append("  【第一步】起卦（三枚铜钱法）")
    lines.append("=" * 58)
    if result['问题']:
        lines.append(f"  占事: {result['问题']}")
    lines.append(f"  时间: {result['时间']}")
    lines.append("")

    for i, yao in enumerate(result['爻象']):
        val = yao['爻值']
        dong = ' → 将变' if yao['动爻'] else ''
        lines.append(f"  第{['一','二','三','四','五','六'][i]}掷: {val} → {YAO_VALUE_NAMES[val]}{dong}")
    lines.append("")

    # 六爻列图
    lines.append("  六爻排列（从下往上）:")
    for i, yao in enumerate(result['爻象']):
        symbol = '━━━' if yao['阴阳'] == 1 else '━ ━'
        if yao['爻值'] == 9: symbol = '━━○'
        elif yao['爻值'] == 6: symbol = '━×━'
        dong = ' (动)' if yao['动爻'] else ''
        yy = '阳' if yao['阴阳'] == 1 else '阴'
        lines.append(f"    {['初','二','三','四','五','上'][i]}爻: {symbol}  {yy}{dong}")
    lines.append("")

    # ===== 第二步：定卦 =====
    lines.append("-" * 58)
    lines.append("  【第二步】定卦名")
    lines.append("-" * 58)

    yaos_bin = [y['阴阳'] for y in result['爻象']]
    xia_bin = tuple(yaos_bin[0:3])
    shang_bin = tuple(yaos_bin[3:6])
    xia_gua = next((n for n, b in BAGUA.items() if b == xia_bin), '?')
    shang_gua = next((n for n, b in BAGUA.items() if b == shang_bin), '?')

    lines.append(f"  下卦(初二三爻): {xia_bin[0]}{xia_bin[1]}{xia_bin[2]} → {xia_gua}卦")
    lines.append(f"  上卦(四五上爻): {shang_bin[0]}{shang_bin[1]}{shang_bin[2]} → {shang_gua}卦")
    lines.append(f"  上{shang_gua}下{xia_gua} → {result['本卦']}")
    lines.append(f"  归属: {result['宫']}宫{result['卦型']}, 宫五行属{result['宫五行']}")
    lines.append("")

    # ===== 第三步：纳甲 =====
    lines.append("-" * 58)
    lines.append("  【第三步】纳甲（配天干地支）")
    lines.append("-" * 58)
    lines.append("  口诀: 乾金甲子外壬午, 坤土乙未外癸丑")
    lines.append("        震木庚子外庚午, 巽木辛丑外辛未")
    lines.append("        坎水戊寅外戊申, 离火己卯外己酉")
    lines.append("        艮土丙辰外丙戌, 兑金丁巳外丁亥")
    lines.append("")

    for i, yao in enumerate(result['爻象']):
        pos = ['初爻','二爻','三爻','四爻','五爻','上爻'][i]
        gc = yao['天干'] + yao['地支']
        wx = yao['五行']
        gua = xia_gua if i < 3 else shang_gua
        nei_wai = '内卦' if i < 3 else '外卦'
        lines.append(f"  {pos}: {nei_wai}{gua} → {yao['天干']}{yao['地支']}({wx})")
    lines.append("")

    # ===== 第四步：安六亲 =====
    lines.append("-" * 58)
    lines.append("  【第四步】安六亲")
    lines.append("-" * 58)
    lines.append(f"  宫五行: {result['宫五行']}（作为'我'）")
    lines.append("  规则: 同我=兄弟, 生我=父母, 我生=子孙, 我克=妻财, 克我=官鬼")
    lines.append("")

    for i, yao in enumerate(result['爻象']):
        pos = ['初爻','二爻','三爻','四爻','五爻','上爻'][i]
        gc = yao['天干'] + yao['地支']
        wx = yao['五行']
        lq = yao['六亲']
        palace_wx = result['宫五行']
        generate = {'金':'土','水':'金','木':'水','火':'木','土':'火'}
        overcome = {'金':'火','水':'土','木':'金','火':'水','土':'木'}
        if wx == palace_wx:
            reason = f"{wx}同{palace_wx}"
        elif generate[palace_wx] == wx:
            reason = f"{wx}生{palace_wx} → 生我"
        elif generate[wx] == palace_wx:
            reason = f"{palace_wx}生{wx} → 我生"
        elif overcome[palace_wx] == wx:
            reason = f"{wx}克{palace_wx} → 克我"
        elif overcome[wx] == palace_wx:
            reason = f"{palace_wx}克{wx} → 我克"
        else:
            reason = ""
        lines.append(f"  {pos}: {gc}({wx}) — {reason} → {lq}")
    lines.append("")

    # ===== 第五步：安六神 =====
    lines.append("-" * 58)
    lines.append("  【第五步】安六神")
    lines.append("-" * 58)
    ri_tg = result['日干支'][0]
    lines.append(f"  日干: {ri_tg}")
    start_map = {'甲':'青龙','乙':'青龙','丙':'朱雀','丁':'朱雀',
                 '戊':'勾陈','己':'螣蛇','庚':'白虎','辛':'白虎',
                 '壬':'玄武','癸':'玄武'}
    lines.append(f"  {ri_tg}日 → 初爻起{start_map.get(ri_tg, '?')}, 依次排列")
    lines.append("")

    for i, yao in enumerate(result['爻象']):
        pos = ['初爻','二爻','三爻','四爻','五爻','上爻'][i]
        lines.append(f"  {pos}: {yao['六神']}")
    lines.append("")

    # ===== 第六步：定世应 =====
    lines.append("-" * 58)
    lines.append("  【第六步】定世应")
    lines.append("-" * 58)
    shi = result['爻象'][result['世位']]
    ying = result['爻象'][result['应位']]
    lines.append(f"  {result['本卦']}为{result['卦型']}")
    lines.append(f"  世位: {['初','二','三','四','五','上'][result['世位']]}爻 — {shi['六亲']} {shi['天干']}{shi['地支']}({shi['五行']})")
    lines.append(f"  应位: {['初','二','三','四','五','上'][result['应位']]}爻 — {ying['六亲']} {ying['天干']}{ying['地支']}({ying['五行']})")
    lines.append("")

    # ===== 第七步：查空亡月破 =====
    lines.append("-" * 58)
    lines.append("  【第七步】查空亡、月破")
    lines.append("-" * 58)
    lines.append(f"  日辰: {result['日干支']}")
    lines.append(f"  空亡: {', '.join(result['空亡'])}")
    lines.append(f"  月建: {result['月建']}建")
    lines.append("")

    kong = [y for y in result['爻象'] if y['空亡']]
    po = [y for y in result['爻象'] if y['月破']]
    if kong:
        lines.append("  ★ 空亡爻:")
        for y in kong:
            lines.append(f"    {y['爻位名']}: {y['六亲']} {y['天干']}{y['地支']}({y['五行']})")
    else:
        lines.append("  无空亡爻")
    if po:
        lines.append("  ★ 月破爻:")
        for y in po:
            lines.append(f"    {y['爻位名']}: {y['六亲']} {y['天干']}{y['地支']}({y['五行']})")
    else:
        lines.append("  无月破爻")
    lines.append("")

    # ===== 第八步：变卦 =====
    if result['变卦详情']:
        lines.append("-" * 58)
        lines.append("  【第八步】变卦")
        lines.append("-" * 58)
        bd = result['变卦详情']
        lines.append(f"  动爻变化后 → {bd['卦名']} ({bd['宫']}宫)")
        lines.append("")
        lines.append(f"  {'爻位':<5} {'六亲':<5} {'干支':<5} {'五行':<3}  变化")
        lines.append("  " + "-" * 40)
        for i, y in enumerate(bd['爻象']):
            pos = ['初爻','二爻','三爻','四爻','五爻','上爻'][i]
            gc = y['天干'] + y['地支']
            orig = result['爻象'][i]
            if i in result['动爻位']:
                orig_yy = '阳' if orig['阴阳'] == 1 else '阴'
                new_yy = '阳' if y['阴阳'] == 1 else '阴'
                change_str = f"{orig_yy}→{new_yy} (动变)"
            else:
                change_str = "不变"
            lines.append(f"  {pos:<5} {y['六亲']:<5} {gc:<5} {y['五行']:<3}  {change_str}")
        lines.append("")
    elif not result['变卦']:
        lines.append("-" * 58)
        lines.append("  【第八步】变卦")
        lines.append("-" * 58)
        lines.append("  六爻皆静(无动爻), 不变卦")
        lines.append("")

    # ===== 最终排盘汇总 =====
    lines.append("=" * 58)
    lines.append("  【排盘汇总】")
    lines.append("=" * 58)
    lines.append(f"  占事: {result['问题'] or '未说明'}")
    lines.append(f"  本卦: {result['本卦']} ({result['宫']}宫{result['卦型']})")
    if result['变卦']:
        lines.append(f"  变卦: {result['变卦']}")
    lines.append(f"  日辰: {result['日干支']}  月建: {result['月建']}建  空亡: {', '.join(result['空亡'])}")
    lines.append("")

    lines.append(f"  {'爻位':<5} {'六神':<5} {'六亲':<5} {'干支':<5} {'五行':<3} {'世应':<2}  卦象")
    lines.append("  " + "-" * 52)
    for yao in reversed(result['爻象']):
        gc = yao['天干'] + yao['地支']
        symbol = '━━━' if yao['阴阳'] == 1 else '━ ━'
        if yao['爻值'] == 9: symbol = '━━○'
        elif yao['爻值'] == 6: symbol = '━×━'
        mark = ' '.join(yao['标记'])
        lines.append(f"  {yao['六神']:<5} {yao['六亲']:<5} {gc:<5} {yao['五行']:<3} {yao['世应']:<2}  {symbol}  {mark}")
    lines.append("")

    lines.append("  【世应关系】")
    rel = wuxing_relation(shi['五行'], ying['五行'])
    sy_map = {'生我':'应生世 → 外部对我有利','我生':'世生应 → 我需要付出',
              '克我':'应克世 → 外部环境压制','我克':'世克应 → 我能掌控局面',
              '同':'世应比和 → 彼此均势'}
    lines.append(f"  {sy_map.get(rel, rel)}")
    lines.append("")
    lines.append("=" * 58)
    return "\n".join(lines)

# ============================================================
# 保存记录
# ============================================================
def get_records_dir():
    """获取 records 目录路径（脚本同级的 records/ 目录）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 如果在 scripts/ 子目录中，上一级就是项目根目录
    if os.path.basename(script_dir) == 'scripts':
        project_dir = os.path.dirname(script_dir)
    else:
        project_dir = script_dir
    records_dir = os.path.join(project_dir, 'records')
    os.makedirs(records_dir, exist_ok=True)
    return records_dir

def save_record(result):
    """保存排盘结果到 records/ 目录"""
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    question = result.get('问题', '').strip()
    # 文件名: 时间_占事.json
    safe_q = question[:20] if question else '无题'
    filename = f"{ts}_{safe_q}.json"
    filepath = os.path.join(get_records_dir(), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return filepath

# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description='六爻纳甲占卜引擎')
    parser.add_argument('-q', '--question', default='', help='所问之事')
    parser.add_argument('-c', '--coins', nargs=6, type=int, help='六爻值(6/7/8/9) 初爻在前')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--full', action='store_true', help='输出完整八步推导')
    parser.add_argument('--no-save', action='store_true', help='不保存记录到 records/ 目录')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--date', type=str, default=None)
    args = parser.parse_args()

    if args.seed is not None: random.seed(args.seed)
    dt = datetime.datetime.strptime(args.date, '%Y-%m-%d') if args.date else None
    values = args.coins if args.coins else cast_hexagram()
    if args.coins and len(args.coins) != 6:
        print("错误: 需要6个爻值"); sys.exit(1)

    result = assemble_hexagram(values, question=args.question, dt=dt)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.full:
        print(format_hexagram(result))
    else:
        print(format_hexagram_brief(result))

    # 自动保存记录
    if not args.no_save:
        try:
            filepath = save_record(result)
            print(f"\n  [记录已保存: {filepath}]")
        except Exception as e:
            print(f"\n  [保存失败: {e}]")

if __name__ == '__main__':
    main()
