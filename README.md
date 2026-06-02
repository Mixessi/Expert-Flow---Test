# Expert-Flow---Test

for 专家访谈提效

## Skills

### ⚽ football-tactics — 足球技战术分析

项目级 Claude Code skill，把零散的比赛信息转化为**解说 + 科普风格**的技战术分析报告。

- **支持输入**：文字/比赛描述、数据/统计表格(CSV/JSON)、比赛截图/视频画面、阵型图/战术板
- **分析框架**：进攻组织 / 攻防转换 / 防守组织 / 守防转换（四阶段循环）
- **风格**：先讲人话再上术语，有画面感、讲因果、结论先行

目录结构：

```
.claude/skills/football-tactics/
├── SKILL.md                      # 主入口：触发条件、分析流程、风格要求
├── references/
│   ├── analysis-framework.md     # 四阶段框架 + 各类输入处理 + 数据指标速查
│   ├── formations.md             # 常见阵型图鉴与克制思路
│   └── tactical-concepts.md      # 战术术语词典（科普式）
└── templates/
    └── report-template.md        # 解说/科普风格报告模板
```

**用法**：直接向 Claude 描述比赛、贴数据、传截图或战术板，或提问"为什么这么踢""怎么破解这套战术"，skill 会自动触发。
