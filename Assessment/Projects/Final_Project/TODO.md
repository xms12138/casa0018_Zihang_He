# EchoLume — Project TODO

按模块列出未完成项与所需图表/文件。打勾即完成。

---

## 1. Firmware（`arduino/echolume/echolume.ino`）

- [ ] **[阻塞]** 接入 WS2812B：`Adafruit_NeoPixel` 库 + 引脚定义（D2 或 D3 待定）
- [ ] 状态 → 颜色映射：
  - `STATE_OFF` → 全灭
  - `STATE_GENERAL` → 白光
  - `STATE_READING` → 暖黄
  - `STATE_SLEEP` → 暗红呼吸（需要在 loop 里做非阻塞 fade）
- [ ] 上电自检：开机闪两下确认硬件正常
- [ ] **检查 `CONFIDENCE_THRESHOLD`**：当前代码 `0.75`，但 baseline 评估表用 `0.6` / `0.5`。统一阈值或在实验日志里说明阈值漂移
- [ ] Serial 调试：除状态切换外，加 `best_label / best_value` 周期性输出（DEBUG 宏控制开关）
- [ ] 在 `experiments/exp_log.md` 里记录上板验证结果（推理耗时、内存、串口截图）

---

## 2. Edge Impulse / 模型

- [ ] 把 `edge_impulse/dsp_config.json` 从 EI Studio 导出参数填实（目前是空 `{}`）
- [ ] 补 `edge_impulse/model_metadata.md`：项目链接、Project ID、最近一次 train/sync 时间
- [ ] 决定是否做对比实验，候选维度（**未承诺数量**，每多一组都要有动机）：
  - DSP：MFCC vs MFE / 不同 coef 数 / 不同 frame stride
  - 架构：1D CNN vs 2D CNN / Conv 通道数加倍
  - 量化：float32 vs INT8 直接对比（已有 INT8，缺 float32 baseline）
  - 数据增强：完整增强 vs 关闭增强
- [ ] 任何新实验：在 `experiments/exp_log.md` 追加，在 `experiments/comparison_table.md` 加一列

---

## 3. 数据相关图表（`report_figures/01_data/`）

- [ ] `class_distribution.png` — 6 类样本数柱状图（已有数字，画即可）
- [ ] `sample_duration_hist.png` — 每类样本时长分布
- [ ] `waveform_examples.png` — 每类挑 1 条样本的波形图（4×1 或 2×3 拼图）
- [ ] `mfcc_turn_on_vs_off.png` — `turn_on` 与 `turn_off` 的 MFCC 时间轴对比（直接支撑 §7 局限性 1）
- [ ] `recording_setup.jpg` — 录音环境照片（设备、距离、房间），说明数据采集条件

---

## 4. 方法/系统图表（`report_figures/02_methods/`）

- [ ] `system_overview.png` — Mic → MFCC → CNN → State Machine → WS2812B 框图
- [ ] `model_architecture.png` — 模型结构图（Conv8 → Conv16 → Flatten → Dense6 + 输入维度标注）
- [ ] `state_machine.png` — §6 状态转移图（drawio / mermaid 导出）

---

## 5. Baseline 实验图表（`report_figures/03_experiments/baseline/`）

- [ ] `training_curves.png` — Loss & accuracy（train vs val）双子图
- [ ] `confusion_matrix_val.png` — 验证集混淆矩阵
- [ ] `confusion_matrix_test_int8.png` — 测试集 INT8 混淆矩阵（threshold 0.6）
- [ ] `per_class_f1.png` — 每类 precision / recall / F1 柱状图
- [ ] `threshold_sweep.png` — 阈值 0.3–0.9 vs accuracy / FPR / FNR 曲线（直接支撑 §7 局限性 5）
- [ ] `ei_studio_metrics.png` — EI Studio 截图（on-device 性能 4ms/12.5KB/46.4KB/258ms）

> 后续实验：每加一组，在 `report_figures/03_experiments/exp_<name>/` 下复刻同一套图，便于横向比较。

---

## 6. 真机测试图表（`report_figures/04_testing/`）

- [ ] 设计测试协议：每个关键词 × N 次 × M 种环境（安静 / 背景音乐 / 多人）
- [ ] `live_test_confusion.png` — 真机测试结果混淆矩阵
- [ ] `failure_cases.md` + 对应音频片段（如能录到）—— 反思章节素材
- [ ] 真机测试视频片段（也用于 3 分钟视频）

---

## 7. 硬件图表（`report_figures/05_hardware/` + `docs/hardware_setup.md`）

- [ ] BOM 表（型号、数量、来源）— 填到 `docs/hardware_setup.md`
- [ ] `wiring_diagram.png` — Fritzing 或手绘接线图（Nano + WS2812B + 电源）
- [ ] `device_photo.jpg` — 实物正面 + 侧面照
- [ ] `enclosure_render.png` — 3D 外壳渲染图
- [ ] `enclosure.stl` — 放在 `docs/` 或 `hardware/`（视后续是否新建目录）
- [ ] 3D 打印：参数（材料、层高、填充率）记录到 `hardware_setup.md`

---

## 8. 报告（`report/report.md`，1500 字 ±20%）

按 9 个章节推进，建议顺序：

- [ ] **Methods（先写，骨架最稳）** — Application Overview + Data + Model
- [ ] **Experiments** — baseline 已有结果先成稿，对比实验后补
- [ ] **Results and Observations** — 含 critical reflection 的 5 条（已在 CLAUDE.md §7）
- [ ] **Introduction** — 末写，避免反复改
- [ ] **Research Question** — 1–2 句
- [ ] **Bibliography** — 同步填 `report/references.bib`（核心引用：Warden 2018 / Reddy 2019 / Zhang 2017）
- [ ] **Declaration of Authorship** — 签名 + 日期
- [ ] 字数核查 + 导出 PDF（VSCode Markdown PDF 扩展）

---

## 9. 视频（3 分钟，30%）

- [ ] 故事板：开场（问题 / 用户场景，~30s）→ 技术（~90s）→ 演示（~45s）→ 反思（~15s）
- [ ] 拍摄：真机操作镜头、串口输出、训练曲线、混淆矩阵
- [ ] 配音 / 字幕脚本
- [ ] 剪辑 + 上传

---

## 10. 提交前检查清单

- [ ] `report.md` 字数在 1200–1800 之间
- [ ] 所有图都有 caption + figure number，正文有引用
- [ ] `references.bib` 全部引用都在正文出现
- [ ] `git status` 干净（CLAUDE.md / .claude / .claudeignore 仍被 .gitignore 屏蔽）
- [ ] GitHub 仓库 README 指向 report PDF
- [ ] Moodle 上传 PDF + 视频
- [ ] Edge Impulse 项目设为 public 或在 metadata 里给出可访问链接

---

## 阻塞依赖图（粗）

```
WS2812B 接线 ──► firmware 灯光控制 ──► 真机测试 ──► 视频拍摄
                                          │
                                          └► 04_testing 图表
对比实验决策 ──► 实验执行 ──► 03_experiments/exp_*/ 图表 ──► 报告 Experiments 章
                                                              │
                                                              └► Results & Reflection
```

最关键路径：**WS2812B 接线 → firmware 灯光 → 真机测试**。这条不通，视频和 testing 章节都没法做。
