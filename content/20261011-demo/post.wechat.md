---
title: Snowflake 怎么把本体论塞进数据仓库
wechat:
  status: draft
  digest: 四个产品、两个发布日、一条主线。
---

# 公司速览：Snowflake 是一家什么公司 {OVERVIEW}

Snowflake 的传统底子是数据仓库 + 数据湖，2024 年开始加 AI。

- 截至 2026 年 1 月 31 日（Q4 FY26 财报）：全球客户 ==13,328 家==（同比 +21%），其中 Forbes Global 2000 占 ==790 家==（同比 +5%）。
- 产品线：Cortex、Horizon Catalog、Semantic Studio、Knowledge Graph。

:::fig 01/07
eyebrow:    COVER · 厂商产品解剖系列 第 4 篇
title:      Snowflake 4 大产品
title:      从企业级湖仓
title-red:  到 AI 智能体
sub:        Horizon Catalog GA · Semantic Studio preview · Knowledge Graph · Cortex Sense preview
line:       4 个产品 · 2 个发布日 · 1 个主线：把 ontology 塞进 warehouse
stat:       4/2/1
stat-label: 产品 / 发布日 / 主线
source:     Snowflake 官方公告 + 官方 Docs + 第三方权威报道
layers:     三层事实分层 62% / 25% / 13% · 25 数据来源 · 2026-09-19
watermark:  公众号 · AI风起兮
caption:    Snowflake 4 大产品 / 从企业级湖仓 / 到 AI 智能体
:::

# 一、Snowflake 的本体论起源，从 Cortex 到 Horizon {SNOWFLAKE}

Cortex 这个 AI 产品家族在 2024 年 6 月的 Snowflake Summit 上第一次成形。但光是「在 warehouse 里跑模型」并不够，真正的痛点是，**AI 智能体需要知道仓库里到底有什么、字段代表什么、跨表关系是什么。**

## 1.1 Horizon Catalog 的官方定位

Horizon Catalog 是 ==2025-11-04== 在 BUILD 大会上 GA 的。它的官方定位，来自 Snowflake 的产品页，

> [!quote]
> Horizon Catalog is the universal AI catalog for Snowflake. It provides a single place for all of your data and AI assets, with built-in governance and context.

它由三个组件构成，根据[官方文档](https://docs.snowflake.com/)，

1. ==Collect==: 把结构化 + 非结构化资产统一收集起来，带 catalog 层的上下文。
2. ==Maintain==: 数据质量 + 自动化的运维监控。
3. ==Extend==: 跨引擎读写能力，因为底层是 Apache Polaris（`Iceberg REST Catalog`）。

> [!insight]
> 把 ontology 塞进 warehouse，本质是让语义层和存储层共用一套治理边界 —— 这是 Snowflake 和 Palantir 路线最大的分野。

## 1.2 与 Palantir 的横向对比

两家没有对称的公开文档，以下对标基于两边的公开文档互证，**非任何一方的官方对标声明**。

| 维度 | Snowflake | Palantir |
|---|---|---|
| ==Object / 实体定义== | Semantic View + KG_NODE，带维度、度量、关系 | Ontology SDK Object Type，声明业务对象 |
| ==Link / 关系定义== | KG_EDGE 显式声明，GraphRAG 提供遍历 | Ontology SDK Link Type，带 cardinality |
| ==治理边界== | RBAC + FGAC + ABAC，Apache Polaris 跨引擎 | Foundry 数据访问角色 + 资源级别 RBAC |

3 个维度对比下来，最显著的差异点是 Snowflake 把治理放在存储层，Palantir 放在应用层。

```sql
-- KG_EDGE 的遍历靠 recursive CTE
WITH RECURSIVE walk AS (SELECT src, dst FROM KG_EDGE WHERE src = 'account:1')
SELECT * FROM walk;
```

![图 2：Horizon Catalog 的三层结构](assets/fig2.png)
