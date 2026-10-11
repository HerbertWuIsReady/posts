#!/usr/bin/env python3
"""post.wechat.md -> 微信公众号内联样式 HTML

用法:
    python to_html.py content/20261011-slug
    python to_html.py content/20261011-slug/post.wechat.md

微信编辑器会剥掉 <style>、class 和 id,并且重置继承。所以每个元素都必须
自带完整 inline style —— 这是本脚本存在的全部理由。所有数值来自 theme.yaml,
不要在本文件里写死样式。
"""
import argparse, html, json, re, sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TOKEN = "\x00C{}\x00"


# ---------------------------------------------------------------- 样式
def build_styles(t):
    b, h1, h2 = t["body"], t["h1"], t["h2"]
    ins, cap, dv = t["insight"], t["caption"], t["divider"]
    cd, tb, ac = t["code"], t["table"], t["accent"]["color"]
    fs, fg, lh, gap = b["font_size"], b["color"], b["line_height"], b["para_spacing"]
    text = f"font-size:{fs};color:{fg};line-height:{lh};"

    S = {
        "wrap":     f"{text}padding:0 {b['side_padding']};word-break:break-word;",
        "p":        f"margin:0 0 {gap} 0;{text}",
        "h1":       (f"margin:{h1['margin_top']} 0 {h1['margin_bottom']} 0;padding-left:12px;"
                     f"border-left:{h1['rule_width']} solid {h1['rule_color']};"
                     f"font-size:{h1['font_size']};font-weight:{h1['font_weight']};"
                     f"color:{h1['color']};line-height:1.4;"),
        "h2":       (f"margin:{h2['margin_top']} 0 {h2['margin_bottom']} 0;"
                     f"font-size:{h2['font_size']};font-weight:{h2['font_weight']};"
                     f"color:{h2['color']};line-height:1.5;"),
        "strong":   f"font-weight:700;color:{h1['color']};",
        "accent":   f"color:{ac};font-weight:600;",
        "sup":      f"font-size:12px;color:{ac};",
        "insight":  (f"margin:{ins['margin']} 0;padding:{ins['padding']};"
                     f"background:{ins['background']};"
                     f"border-left:{ins['border_left']} solid {ins['border_color']};"
                     f"border-radius:{ins['radius']};"),
        "ins_p":    f"margin:0 0 10px 0;{text}",
        "ins_last": f"margin:0;{text}",
        "divider":  (f"margin:{dv['margin']} 0;height:{dv['height']};"
                     f"background:{dv['color']};line-height:0;font-size:0;"),
        "li":       f"margin:0 0 10px 0;padding-left:1.5em;text-indent:-1.5em;{text}",
        "ul":       f"margin:0 0 {gap} 0;",
        "marker":   f"color:{ac};",
        "pre_wrap": f"margin:0 0 {gap} 0;overflow-x:auto;",
        "pre":      (f"margin:0;padding:{cd['padding']};background:{cd['background']};"
                     f"border-radius:{cd['radius']};font-size:{cd['font_size']};"
                     f"font-family:{cd['font_family']};color:{cd['color']};"
                     f"line-height:1.6;white-space:pre;"),
        "icode":    (f"padding:2px 5px;background:{cd['background']};border-radius:3px;"
                     f"font-size:{cd['font_size']};font-family:{cd['font_family']};"
                     f"color:{cd['color']};"),
        "img_wrap": f"margin:{ins['margin']} 0;",
        "img_ph":   (f"padding:28px 12px;background:{ins['background']};"
                     f"border:1px dashed {tb['border_color']};border-radius:{ins['radius']};"
                     f"text-align:center;font-size:13px;color:{cap['color']};line-height:1.7;"),
        "img_name": f"font-size:12px;color:{cap['color']};font-family:{cd['font_family']};",
        "caption":  (f"margin-top:{cap['margin_top']};font-size:{cap['font_size']};"
                     f"color:{cap['color']};text-align:{cap['align']};line-height:1.6;"),
        "tb_wrap":  f"margin:0 0 {gap} 0;overflow-x:auto;",
        "table":    (f"width:100%;border-collapse:collapse;font-size:{tb['font_size']};"
                     f"color:{fg};line-height:1.6;"),
        "th":       (f"padding:8px 10px;border:1px solid {tb['border_color']};"
                     f"background:{tb['header_bg']};font-weight:600;text-align:left;"),
        "td":       f"padding:8px 10px;border:1px solid {tb['border_color']};",
        "ref":      f"margin:0 0 6px 0;font-size:13px;color:{cap['color']};line-height:1.7;word-break:break-all;",
    }
    return S


# ---------------------------------------------------------------- 行内
def inline(s, S, links):
    spans = []

    def grab(m):
        spans.append(m.group(1))
        return TOKEN.format(len(spans) - 1)

    s = re.sub(r"`([^`]+)`", grab, s)          # 先抽行内代码,免得里面的 ** == 被解析
    s = html.escape(s, quote=False)

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        if url.startswith(("http://", "https://")):   # 微信禁外链 -> 收进文末参考
            if url not in links:
                links.append(url)
            return f'{label}<sup style="{S["sup"]}">[{links.index(url) + 1}]</sup>'
        return label

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: f'<strong style="{S["strong"]}">{m.group(1)}</strong>', s)
    s = re.sub(r"==(.+?)==", lambda m: f'<span style="{S["accent"]}">{m.group(1)}</span>', s)

    for i, c in enumerate(spans):
        s = s.replace(TOKEN.format(i), f'<code style="{S["icode"]}">{html.escape(c, quote=False)}</code>')
    return s


# ---------------------------------------------------------------- 块级
BLOCK_RE = re.compile(r"(#{1,2}\s|>|!\[|```|[-*+]\s|\d+[.)]\s|-{3,}$|\*{3,}$)")


def is_block(line):
    return bool(BLOCK_RE.match(line.strip())) or "|" in line


def render(lines, S, links, stat):
    out, i, n = [], 0, len(lines)
    while i < n:
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}", s):                       # 分隔线
            out.append(f'<section style="{S["divider"]}"></section>')
            stat["divider"] += 1
            i += 1
            continue

        if s.startswith("```"):                                    # 代码块
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(buf), quote=False)
            out.append(f'<section style="{S["pre_wrap"]}"><pre style="{S["pre"]}">{code}</pre></section>')
            stat["code"] += 1
            continue

        m = re.match(r"(#{1,2})\s+(.*)", s)                        # 标题
        if m:
            key = "h1" if len(m.group(1)) == 1 else "h2"
            out.append(f'<section style="{S[key]}">{inline(m.group(2), S, links)}</section>')
            stat[key] += 1
            i += 1
            continue

        if s.startswith(">"):                                      # 洞察框
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            if buf and re.fullmatch(r"\s*\[!\w+\]\s*", buf[0]):
                buf = buf[1:]
            paras = [p.strip().replace("\n", " ") for p in "\n".join(buf).split("\n\n") if p.strip()]
            inner = "".join(
                f'<p style="{S["ins_last"] if k == len(paras) - 1 else S["ins_p"]}">'
                f'{inline(p, S, links)}</p>'
                for k, p in enumerate(paras))
            out.append(f'<section style="{S["insight"]}">{inner}</section>')
            stat["insight"] += 1
            continue

        m = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", s)           # 图片
        if m:
            cap, path = m.group(1), m.group(2)
            name = html.escape(path.rsplit("/", 1)[-1])
            ph = (f'<section style="{S["img_ph"]}">图片待上传素材库<br/>'
                  f'<span style="{S["img_name"]}">{name}</span></section>')
            cp = f'<section style="{S["caption"]}">{inline(cap, S, links)}</section>' if cap else ""
            out.append(f'<section style="{S["img_wrap"]}">{ph}{cp}</section>')
            stat["image"] += 1
            stat["image_files"].append(path)
            i += 1
            continue

        if "|" in s and i + 1 < n and re.fullmatch(r"[\s:|-]+", lines[i + 1].strip()) \
                and "-" in lines[i + 1]:                           # 表格
            rows = []
            while i < n and "|" in lines[i]:
                rows.append(lines[i])
                i += 1
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            th = "".join(f'<th style="{S["th"]}">{inline(c, S, links)}</th>' for c in cells(rows[0]))
            tr = "".join("<tr>" + "".join(f'<td style="{S["td"]}">{inline(c, S, links)}</td>'
                                          for c in cells(r)) + "</tr>" for r in rows[2:])
            out.append(f'<section style="{S["tb_wrap"]}"><table style="{S["table"]}">'
                       f"<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></section>")
            stat["table"] += 1
            continue

        if re.match(r"([-*+]|\d+[.)])\s+", s):                     # 列表
            rows, cnt = [], 0
            ordered = bool(re.match(r"\d+[.)]\s+", s))
            while i < n and re.match(r"\s*([-*+]|\d+[.)])\s+", lines[i]):
                ln = lines[i]
                depth = 1 if len(ln) - len(ln.lstrip()) >= 2 else 0
                txt = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", ln).strip()
                if ordered and depth == 0:
                    cnt += 1
                    mark = f"{cnt}."
                else:
                    mark = "◦" if depth else "•"
                rows.append(f'<section style="{S["li"]}margin-left:{16 * depth}px;">'
                            f'<span style="{S["marker"]}">{mark}</span>&nbsp;'
                            f"{inline(txt, S, links)}</section>")
                i += 1
            out.append(f'<section style="{S["ul"]}">' + "".join(rows) + "</section>")
            stat["list"] += 1
            continue

        buf = []                                                   # 普通段落
        while i < n and lines[i].strip() and not (buf and is_block(lines[i])):
            buf.append(lines[i].strip())
            i += 1
        out.append(f'<section style="{S["p"]}">{inline(" ".join(buf), S, links)}</section>')
        stat["para"] += 1
    return "\n".join(out)


# ---------------------------------------------------------------- 主流程
def split_front_matter(txt):
    if txt.startswith("---"):
        parts = txt.split("---", 2)
        if len(parts) == 3:
            try:
                return yaml.safe_load(parts[1]) or {}, parts[2].lstrip("\n")
            except yaml.YAMLError:
                pass
    return {}, txt


def main():
    ap = argparse.ArgumentParser(description="post.wechat.md -> 微信内联样式 HTML")
    ap.add_argument("target", help="文章目录,或直接给 post.wechat.md 路径")
    ap.add_argument("--theme", default=str(HERE / "theme.yaml"))
    ap.add_argument("--json", action="store_true", help="统计以 JSON 输出")
    a = ap.parse_args()

    tgt = Path(a.target)
    src = tgt if tgt.is_file() else tgt / "post.wechat.md"
    if not src.exists():
        sys.exit(f"找不到 {src}。先让 wechat-format skill 生成 post.wechat.md。")

    theme = yaml.safe_load(Path(a.theme).read_text(encoding="utf-8"))
    S = build_styles(theme)

    fm, body = split_front_matter(src.read_text(encoding="utf-8"))
    links = []
    stat = dict(h1=0, h2=0, para=0, insight=0, list=0, table=0, code=0,
                image=0, divider=0, image_files=[])

    article = render(body.splitlines(), S, links, stat)

    if links:
        refs = "".join(f'<section style="{S["ref"]}">[{i + 1}] {html.escape(u)}</section>'
                       for i, u in enumerate(links))
        article += (f'\n<section style="{S["divider"]}"></section>'
                    f'<section style="{S["h2"]}">参考</section>{refs}')

    wx = fm.get("wechat") or {}
    title = wx.get("title") or fm.get("title") or src.parent.name
    page = (
        '<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{html.escape(str(title))}</title>\n"
        '<style>html{background:#eceff3}body{box-sizing:border-box;margin:0 auto;max-width:414px;'
        'padding:24px 16px;background:#fff;'
        '-apple-system-font:BlinkMacSystemFont;'
        'font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB",sans-serif}</style>\n'
        "</head>\n<body>\n"
        f'<section style="{S["wrap"]}">\n{article}\n</section>\n'
        "</body>\n</html>\n")

    out = src.parent / "out" / "wechat.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")

    if a.json:
        print(json.dumps({"out": str(out), "links": links, **stat}, ensure_ascii=False, indent=2))
    else:
        print(f"→ {out}")
        print(f"  一级标题 {stat['h1']} · 二级标题 {stat['h2']} · 段落 {stat['para']} · "
              f"洞察框 {stat['insight']} · 列表 {stat['list']} · 表格 {stat['table']} · "
              f"代码块 {stat['code']} · 分隔线 {stat['divider']}")
        if stat["image_files"]:
            print(f"  需手动上传素材库的图 {len(stat['image_files'])} 张:")
            for p in stat["image_files"]:
                print(f"    - {p}")
        if links:
            print(f"  外链 {len(links)} 条已收进文末「参考」(微信正文禁外链)")


if __name__ == "__main__":
    main()
