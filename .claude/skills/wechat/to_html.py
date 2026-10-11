#!/usr/bin/env python3
"""post.wechat.md -> 微信公众号内联样式 HTML

用法:  python to_html.py content/<slug>

微信编辑器会剥掉 <style>、class、id，并且重置继承，所以每个元素都必须自带完整
inline style —— 这是本脚本存在的全部理由。所有数值来自 theme.yaml。
"""
import argparse, html, json, re, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
TOK = "\x00C{}\x00"


def build(t):
    b, sec, h2 = t["body"], t["section"], t["h2"]
    ins, quo, lst = t["insight"], t["quote"], t["list"]
    cap, dv, cd, tb, fg = t["caption"], t["divider"], t["code"], t["table"], t["fig"]
    ac, red = t["accent"]["color"], t["accent"]["red"]
    base = (f"font-size:{b['font_size']};color:{b['color']};line-height:{b['line_height']};"
            f"letter-spacing:{b['letter_spacing']};")

    def box(c, italic=False):
        return (f"margin:{c['margin']} 0;padding:{c['padding']};background:{c['background']};"
                f"border-left:{c['border_left']} solid {c['border_color']};"
                f"border-radius:{c['radius']};")

    def box_p(c, italic=False):
        return (f"margin:0;font-size:{b['font_size']};color:{c['text_color']};"
                f"line-height:{b['line_height']};letter-spacing:{b['letter_spacing']};"
                + ("font-style:italic;" if italic else ""))

    return {
        "wrap":   f"{base}padding:0 {b['side_padding']};word-break:break-word;",
        "p":      f"margin:0 0 {b['para_spacing']} 0;{base}",
        # —— 章节标题块（五层，居中）
        "s_rule": (f"margin:{sec['rule_margin']} 0 {sec['rule_margin']} 0;"
                   f"height:{sec['rule_height']};background:{sec['rule_color']};"
                   f"line-height:0;font-size:0;"),
        "s_part": (f"margin:0 0 {sec['part_margin']} 0;text-align:center;"
                   f"font-size:{sec['part_size']};color:{sec['part_color']};"
                   f"letter-spacing:{sec['part_spacing']};font-weight:600;"),
        "s_title": (f"margin:0 0 {sec['title_margin']} 0;text-align:center;"
                    f"font-size:{sec['title_size']};font-weight:{sec['title_weight']};"
                    f"color:{sec['title_color']};letter-spacing:{sec['title_spacing']};"
                    f"line-height:1.45;"),
        "s_tag":  (f"margin:0 0 {sec['tag_margin']} 0;text-align:center;"
                   f"font-size:{sec['tag_size']};color:{sec['tag_color']};"
                   f"letter-spacing:{sec['tag_spacing']};"),
        "s_undw": (f"margin:0 auto {sec['under_margin']} auto;width:{sec['under_width']};"
                   f"height:{sec['under_height']};background:{sec['under_color']};"
                   f"line-height:0;font-size:0;"),
        "h2":     (f"margin:{h2['margin_top']} 0 {h2['margin_bottom']} 0;"
                   f"font-size:{h2['font_size']};font-weight:{h2['font_weight']};"
                   f"color:{h2['color']};line-height:1.5;"),
        "strong": f"font-weight:700;color:{sec['title_color']};",
        "accent": f"color:{ac};font-weight:600;",
        "sup":    f"font-size:11px;color:{ac};",
        "insight": box(ins), "ins_p": box_p(ins),
        "quote":   box(quo), "quo_p": box_p(quo, quo.get("italic", False)),
        # —— 徽章列表
        "ul":     f"margin:0 0 {b['para_spacing']} 0;",
        "li":     (f"margin:0 0 {lst['item_spacing']} 0;padding-left:{lst['indent']};"
                   f"text-indent:-{lst['indent']};{base}"),
        "badge":  (f"display:inline-block;width:{lst['badge_size']};height:{lst['badge_size']};"
                   f"line-height:{lst['badge_size']};border-radius:50%;"
                   f"background:{lst['badge_bg']};color:{lst['badge_color']};"
                   f"text-align:center;font-size:11px;font-weight:700;text-indent:0;"
                   f"vertical-align:middle;margin-right:8px;"),
        "bullet": f"color:{ac};font-weight:700;margin-right:8px;text-indent:0;",
        # —— 代码 / 图 / 线
        "pre_w":  f"margin:0 0 {b['para_spacing']} 0;overflow-x:auto;",
        "pre":    (f"margin:0;padding:{cd['padding']};background:{cd['background']};"
                   f"border-radius:{cd['radius']};font-size:{cd['font_size']};"
                   f"font-family:{cd['font_family']};color:{cd['color']};"
                   f"line-height:1.6;white-space:pre;letter-spacing:0;"),
        "icode":  (f"padding:2px 5px;background:{cd['background']};border-radius:3px;"
                   f"font-size:{cd['font_size']};font-family:{cd['font_family']};"
                   f"color:{cd['color']};letter-spacing:0;"),
        "img_w":  f"margin:{ins['margin']} 0;",
        "img_ph": (f"padding:30px 12px;background:{cd['background']};"
                   f"border:1px dashed {tb['border_color']};border-radius:4px;"
                   f"text-align:center;font-size:13px;color:{cap['color']};line-height:1.7;"),
        "img_nm": f"font-size:12px;color:{cap['color']};font-family:{cd['font_family']};",
        "cap":    (f"margin-top:{cap['margin_top']};font-size:{cap['font_size']};"
                   f"color:{cap['color']};text-align:{cap['align']};line-height:1.6;"),
        "div":    (f"margin:{dv['margin']} 0;height:{dv['height']};background:{dv['color']};"
                   f"line-height:0;font-size:0;"),
        # —— 表格
        "tb_w":   f"margin:0 0 {b['para_spacing']} 0;overflow-x:auto;",
        "table":  (f"width:100%;border-collapse:collapse;font-size:{tb['font_size']};"
                   f"color:{b['color']};line-height:1.7;letter-spacing:0;"),
        "th":     (f"padding:10px 12px;background:{tb['header_bg']};color:{tb['header_color']};"
                   f"font-weight:700;text-align:left;border:1px solid {tb['header_bg']};"),
        "td":     f"padding:10px 12px;border:1px solid {tb['border_color']};",
        "td_z":   (f"padding:10px 12px;border:1px solid {tb['border_color']};"
                   f"background:{tb['stripe_bg']};"),
        "td1":    f"color:{tb['first_col_color']};font-weight:700;",
        # —— 信息图卡片
        "fig":    (f"margin:{fg['margin']} 0;padding:{fg['padding']};"
                   f"background:{fg['background']};border:1px solid {fg['border_color']};"),
        "f_eye":  (f"margin:0 0 16px 0;font-size:{fg['eyebrow_size']};color:{fg['eyebrow_color']};"
                   f"letter-spacing:{fg['eyebrow_spacing']};"),
        "f_tit":  (f"margin:0 0 4px 0;font-size:{fg['title_size']};font-weight:700;"
                   f"color:{fg['title_color']};font-family:{fg['title_family']};line-height:1.3;"),
        "f_red":  (f"margin:0 0 4px 0;font-size:{fg['title_size']};font-weight:700;"
                   f"color:{red};font-family:{fg['title_family']};line-height:1.3;"),
        "f_sub":  (f"margin:14px 0 0 0;font-size:{fg['sub_size']};color:{fg['sub_color']};"
                   f"line-height:1.6;"),
        "f_hr":   f"margin:14px 0;height:1px;background:{fg['border_color']};line-height:0;font-size:0;",
        "f_line": f"font-size:{fg['sub_size']};color:{fg['title_color']};font-weight:600;line-height:1.6;",
        "f_stat": (f"font-size:{fg['stat_size']};color:{fg['stat_color']};font-weight:700;"
                   f"line-height:1.1;text-align:right;font-family:{fg['title_family']};"),
        "f_slab": f"font-size:10px;color:{fg['sub_color']};text-align:right;margin-top:4px;",
        "f_src":  (f"font-size:{fg['source_size']};color:{fg['source_color']};line-height:1.6;"),
        "f_num":  (f"font-size:{fg['source_size']};color:{fg['source_color']};text-align:right;"),
        "f_cell": "padding:0;border:0;vertical-align:bottom;",
        "f_mark": (f"font-size:12px;color:{fg['sub_color']};text-align:right;"
                   f"margin-bottom:4px;letter-spacing:1px;"),
    }


def inline(s, S, links):
    sp = []
    s = re.sub(r"`([^`]+)`", lambda m: (sp.append(m.group(1)), TOK.format(len(sp) - 1))[1], s)
    s = html.escape(s, quote=False)

    def lk(m):
        label, url = m.group(1), html.unescape(m.group(2))
        if url.startswith(("http://", "https://")):
            if url not in links:
                links.append(url)
            return f'{label}<sup style="{S["sup"]}">[{links.index(url) + 1}]</sup>'
        return label

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lk, s)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: f'<strong style="{S["strong"]}">{m.group(1)}</strong>', s)
    s = re.sub(r"==(.+?)==", lambda m: f'<span style="{S["accent"]}">{m.group(1)}</span>', s)
    for i, c in enumerate(sp):
        s = s.replace(TOK.format(i), f'<code style="{S["icode"]}">{html.escape(c, quote=False)}</code>')
    return s


def fig_card(fields, num, S, links, st):
    g = lambda k: fields.get(k, [])
    one = lambda k: (fields.get(k) or [""])[0]
    o = [f'<section style="{S["fig"]}">']
    if one("eyebrow"):
        o.append(f'<section style="{S["f_eye"]}">{inline(one("eyebrow"), S, links)}</section>')
    for t in g("title"):
        o.append(f'<section style="{S["f_tit"]}">{inline(t, S, links)}</section>')
    for t in g("title-red"):
        o.append(f'<section style="{S["f_red"]}">{inline(t, S, links)}</section>')
    if one("sub"):
        o.append(f'<section style="{S["f_sub"]}">{inline(one("sub"), S, links)}</section>')
    if one("line") or one("stat"):
        o.append(f'<section style="{S["f_hr"]}"></section>')
        stat = ""
        if one("stat"):
            stat = f'<section style="{S["f_stat"]}">{inline(one("stat"), S, links)}</section>'
            if one("stat-label"):
                stat += f'<section style="{S["f_slab"]}">{inline(one("stat-label"), S, links)}</section>'
        o.append('<table style="width:100%;border-collapse:collapse;"><tr>'
                 f'<td style="{S["f_cell"]}width:62%;"><section style="{S["f_line"]}">'
                 f'{inline(one("line"), S, links)}</section></td>'
                 f'<td style="{S["f_cell"]}">{stat}</td></tr></table>')
    o.append(f'<section style="{S["f_hr"]}"></section>')
    src = f'SOURCE · {inline(one("source"), S, links)}' if one("source") else "&nbsp;"
    if one("layers"):
        src += f'<br/>{inline(one("layers"), S, links)}'
    right = f'<section style="{S["f_num"]}">FIG {num}</section>'
    if one("watermark"):
        right = (f'<section style="{S["f_mark"]}">{inline(one("watermark"), S, links)}</section>'
                 + right)
    o.append('<table style="width:100%;border-collapse:collapse;"><tr>'
             f'<td style="{S["f_cell"]}"><section style="{S["f_src"]}">{src}</section></td>'
             f'<td style="{S["f_cell"]}width:34%;">{right}</td>'
             "</tr></table>")
    o.append("</section>")
    if one("caption"):
        o.append(f'<section style="{S["cap"]}">{inline(one("caption"), S, links)}</section>')
    st["fig"] += 1
    return "".join(o)


BLK = re.compile(r"(#{1,2}\s|>|!\[|```|:::|[-*+]\s|\d+[.)]\s|-{3,}$|\*{3,}$)")


def render(lines, S, links, st):
    out, i, n, part = [], 0, len(lines), 0
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue

        if s.startswith(":::fig"):                                   # 信息图卡片
            num = s[6:].strip() or f"{st['fig'] + 1:02d}"
            i += 1
            f = {}
            while i < n and not lines[i].strip().startswith(":::"):
                m = re.match(r"\s*([\w-]+)\s*[:：]\s*(.*)", lines[i])
                if m:
                    f.setdefault(m.group(1), []).append(m.group(2).strip())
                i += 1
            i += 1
            out.append(fig_card(f, num, S, links, st))
            continue

        if re.fullmatch(r"-{3,}|\*{3,}", s):                          # 分隔线
            out.append(f'<section style="{S["div"]}"></section>')
            st["div"] += 1; i += 1; continue

        if s.startswith("```"):                                       # 代码块
            i += 1; buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append(f'<section style="{S["pre_w"]}"><pre style="{S["pre"]}">'
                       f'{html.escape(chr(10).join(buf), quote=False)}</pre></section>')
            st["code"] += 1; continue

        m = re.match(r"#\s+(.*)", s)                                  # 章节标题块
        if m:
            part += 1
            txt = m.group(1)
            tag = ""
            mt = re.search(r"\{([^}]*)\}\s*$", txt)
            if mt:
                tag = mt.group(1).strip(); txt = txt[:mt.start()].strip()
            out.append(f'<section style="{S["s_rule"]}"></section>'
                       f'<section style="{S["s_part"]}">PART {part:02d}</section>'
                       f'<section style="{S["s_title"]}">{inline(txt, S, links)}</section>'
                       + (f'<section style="{S["s_tag"]}">—{html.escape(tag)}</section>' if tag else "")
                       + f'<section style="{S["s_undw"]}"></section>')
            st["h1"] += 1; i += 1; continue

        m = re.match(r"##\s+(.*)", s)                                 # 小节标题
        if m:
            out.append(f'<section style="{S["h2"]}">{inline(m.group(1), S, links)}</section>')
            st["h2"] += 1; i += 1; continue

        if s.startswith(">"):                                         # 洞察框 / 原文引用
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            kind = "insight"
            if buf and re.fullmatch(r"\s*\[!(\w+)\]\s*", buf[0]):
                kind = re.fullmatch(r"\s*\[!(\w+)\]\s*", buf[0]).group(1).lower()
                buf = buf[1:]
            kind = kind if kind in ("insight", "quote") else "insight"
            ps = [p.strip().replace("\n", " ") for p in "\n".join(buf).split("\n\n") if p.strip()]
            pk = "ins_p" if kind == "insight" else "quo_p"
            inner = "".join(f'<p style="{S[pk]}{"" if k == len(ps)-1 else "margin-bottom:10px;"}">'
                            f'{inline(p, S, links)}</p>' for k, p in enumerate(ps))
            out.append(f'<section style="{S[kind]}">{inner}</section>')
            st[kind] += 1; continue

        m = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", s)              # 真实图片
        if m:
            cp, path = m.group(1), m.group(2)
            nm = html.escape(path.rsplit("/", 1)[-1])
            out.append(f'<section style="{S["img_w"]}"><section style="{S["img_ph"]}">'
                       f'图片待上传素材库<br/><span style="{S["img_nm"]}">{nm}</span></section>'
                       + (f'<section style="{S["cap"]}">{inline(cp, S, links)}</section>' if cp else "")
                       + "</section>")
            st["img"] += 1; st["img_files"].append(path); i += 1; continue

        if "|" in s and i + 1 < n and re.fullmatch(r"[\s:|-]+", lines[i + 1].strip()) \
                and "-" in lines[i + 1]:                              # 表格
            rows = []
            while i < n and "|" in lines[i]:
                rows.append(lines[i]); i += 1
            cel = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            th = "".join(f'<th style="{S["th"]}">{inline(c, S, links)}</th>' for c in cel(rows[0]))
            body = ""
            for k, r in enumerate(rows[2:]):
                base = S["td_z"] if k % 2 else S["td"]
                body += "<tr>" + "".join(
                    f'<td style="{base}{S["td1"] if j == 0 else ""}">{inline(c, S, links)}</td>'
                    for j, c in enumerate(cel(r))) + "</tr>"
            st["cols"] = max(st["cols"], len(cel(rows[0])))
            out.append(f'<section style="{S["tb_w"]}"><table style="{S["table"]}">'
                       f"<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></section>")
            st["table"] += 1; continue

        if re.match(r"([-*+]|\d+[.)])\s+", s):                        # 列表
            rows, cnt = [], 0
            ordered = bool(re.match(r"\d+[.)]\s+", s))
            while i < n and re.match(r"\s*([-*+]|\d+[.)])\s+", lines[i]):
                ln = lines[i]
                dep = 1 if len(ln) - len(ln.lstrip()) >= 2 else 0
                txt = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", ln).strip()
                if ordered and dep == 0:
                    cnt += 1
                    mk = f'<span style="{S["badge"]}">{cnt}</span>'
                else:
                    mk = f'<span style="{S["bullet"]}">{"◦" if dep else "•"}</span>'
                rows.append(f'<section style="{S["li"]}margin-left:{18 * dep}px;">'
                            f"{mk}{inline(txt, S, links)}</section>")
                i += 1
            out.append(f'<section style="{S["ul"]}">' + "".join(rows) + "</section>")
            st["list"] += 1; continue

        buf = []                                                      # 普通段落
        while i < n and lines[i].strip() and not (buf and BLK.match(lines[i].strip())):
            buf.append(lines[i].strip()); i += 1
        out.append(f'<section style="{S["p"]}">{inline(" ".join(buf), S, links)}</section>')
        st["para"] += 1
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target"); ap.add_argument("--theme", default=str(HERE / "theme.yaml"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    tgt = Path(a.target)
    src = tgt if tgt.is_file() else tgt / "post.wechat.md"
    if not src.exists():
        sys.exit(f"找不到 {src}")

    S = build(yaml.safe_load(Path(a.theme).read_text(encoding="utf-8")))
    txt = src.read_text(encoding="utf-8")
    fm, body = {}, txt
    if txt.startswith("---"):
        p = txt.split("---", 2)
        if len(p) == 3:
            try:
                fm, body = yaml.safe_load(p[1]) or {}, p[2].lstrip("\n")
            except yaml.YAMLError:
                pass

    links = []
    st = dict(h1=0, h2=0, para=0, insight=0, quote=0, list=0, table=0, code=0,
              img=0, fig=0, div=0, cols=0, img_files=[])
    art = render(body.splitlines(), S, links, st)
    if links:
        art += (f'\n<section style="{S["div"]}"></section>'
                f'<section style="{S["h2"]}">参考</section>'
                + "".join(f'<section style="{S["f_src"]}margin-bottom:6px;word-break:break-all;">'
                          f"[{i+1}] {html.escape(u)}</section>" for i, u in enumerate(links)))

    wx = fm.get("wechat") or {}
    title = wx.get("title") or fm.get("title") or src.parent.name
    page = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f"<title>{html.escape(str(title))}</title>\n"
            "<style>html{background:#eceff3}body{box-sizing:border-box;margin:0 auto;"
            "max-width:677px;padding:28px 20px;background:#fff;font-family:-apple-system,"
            'BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB",sans-serif}</style>\n'
            f'</head>\n<body>\n<section style="{S["wrap"]}">\n{art}\n</section>\n</body>\n</html>\n')

    out = src.parent / "out" / "wechat.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")

    if a.json:
        print(json.dumps({"out": str(out), "links": links, **st}, ensure_ascii=False, indent=2))
    else:
        print(f"→ {out}")
        print(f"  章节 {st['h1']} · 小节 {st['h2']} · 段落 {st['para']} · 卡片 {st['fig']} · "
              f"洞察框 {st['insight']} · 原文引用 {st['quote']} · 列表 {st['list']} · "
              f"表格 {st['table']}(最宽 {st['cols']} 列) · 代码 {st['code']}")
        if st["cols"] > 3:
            print(f"  ⚠ 表格 {st['cols']} 列，手机端会横向溢出，建议拆表或改分层列表")
        for p in st["img_files"]:
            print(f"  需手动上传素材库: {p}")
        if links:
            print(f"  外链 {len(links)} 条已收进文末「参考」")


if __name__ == "__main__":
    main()
