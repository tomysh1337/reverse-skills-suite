# JNI / VMP / ZKM / Native 反混淆公开资料汇总

检索日期：2026-09-28  
目标样本：`NP-analysis/original/NP.apk`  说明：本文件只记录公开资料、工具和可复现方法，不下载第三方样本，也不把公开文章中的宣传性描述当成已验证事实。

## 阅读规则

- **高**：公开源代码或可独立构建的实验项目，README 给出了输入、运行方式和预期输出。
- **中**：文章给出了源码片段、调用链或调试过程，但依赖特定 Android/ART/Windows 版本，需在本地 fixture 上复核。
- **低**：只有二次转载、下载页或无法核验的工具宣传；可用于发现关键词，不能作为结论证据。
- **可复现**只表示方法可在相同平台/版本上重做，不表示能对任意 APK 或任意保护器成功恢复。

## GitHub：JNI 动态注册与运行时捕获

| 项目 | URL | 核心方法 | 可信度 / 可复现性 |
|---|---|---|---|
| fridaRegstNtv | <https://github.com/deathmemory/fridaRegstNtv> | Frida 观察 `RegisterNatives`，输出类名、方法名、签名、函数指针、所属 SO、模块基址和偏移。适合先建立 Java native 声明到 ELF 地址的映射表。 | 高；README 有示例日志和构建说明。依赖 Frida/ART 版本，需 Android 设备或模拟器。 |
| hook_ArtMethod_RegisterNative | <https://github.com/jiyulany/hook_ArtMethod_RegisterNative> | 在 ART 的 `ArtMethod::RegisterNative` 处捕获注册，覆盖应用自实现注册路径；可与 `RegisterNatives` 双重采集互证。 | 中高；提供脚本和 native 库。README 依赖 root、SELinux 配置和特定 ART 布局，跨版本需重新定位符号。 |
| JNI-Frida-Hook | <https://github.com/Areizen/JNI-Frida-Hook> | Frida 观察指定 SO 的 `JNI_OnLoad` 和 JNI 调用，支持按库/函数筛选。适合检查库加载顺序和二次调用点。 | 高；仓库含 `agent.js`、依赖和使用说明。需要 Frida 工具链和运行中的 Android 进程。 |
| frida-android-jni-hooking | <https://github.com/0x3xploit/frida-android-jni-hooking> | 脚本列出已加载 native 库和 JNI 函数，并按目标库进行 hook；适合作为 JNI 边界扫描器的原型。 | 中高；包含 sample scripts。对隐藏/动态注册函数仍要配合 `RegisterNatives` 采集。 |
| frida_qbdi_hook | <https://github.com/Taardisaa/frida_qbdi_hook> | Frida + QBDI 对 AArch64 的 `JNI_OnLoad` 做指令级跟踪，用于观察初始化阶段的寄存器、调用和控制流。 | 中高；README 明确需要物理设备、QBDI SO、root 和 Frida。可复现，但 ABI/系统版本耦合较强。 |
| fake_invoke | <https://github.com/Ylarod/fake_invoke> | 在 IDA 调试器中伪造/重放 `JNI_OnLoad`，把目标 SO 放入可控进程，以便静态工具观察注册和初始化逻辑。 | 中；方法对初始化副作用大的库很有用，但需要按样本改造 invoke 进程和 JNI 环境。 |
| android_analysis | <https://github.com/xbyl1234/android_analysis> | 集成 native hook、JNI trace、TLS/SSL 观察和 Frida 辅助脚本；适合快速搭建运行时证据收集层。 | 中；README 有构建和部署步骤，功能较杂，需逐项审计脚本，不能把其网络模块当作本项目必需依赖。 |
| android-jni-tracer | <https://github.com/KimJaeHwan/android-jni-tracer> | 面向 Android SO 的 JNI 调用 hook 和日志记录，适合批量生成 JNI 调用样本。 | 中高；项目定位清晰。需要在目标 Android 版本上验证 JNI 表偏移和注入方式。 |
| AgentDroid-v1- | <https://github.com/zhanghui123/AgentDroid-v1-> | AI 辅助的 Native Security Research 框架，包含 JNI trace、anti-debug/anti-hook 检测、SO dump 和脚本生成的编排思路。 | 中；适合作为统一调度器的设计参考，具体自动化结果需要逐项复核。 |

### 对 NP 样本的直接用法

1. 先用 `fridaRegstNtv` 和 `hook_ArtMethod_RegisterNative` 采集 `np.manager.Protect`、`McpHttpServer` 等类的注册三元组 `(name, signature, fnPtr)`，保存模块基址和 `fnPtr - base`。
2. 用 `frida_qbdi_hook` 或等价指令跟踪记录 `libnpprotect.so` 的 `JNI_OnLoad`、`classesInit0..9` 和 `vmInterpret` 调用边界。
3. 用 `fake_invoke` 的隔离进程思路处理只在库初始化阶段出现的注册；输出必须包含调用栈、线程、模块和时间戳，避免把静态猜测当成恢复结果。

## GitHub：VMP / 虚拟机保护

| 项目 | URL | 核心方法 | 可信度 / 可复现性 |
|---|---|---|---|
| VMProtect-devirtualization | <https://github.com/JonathanSalwan/VMProtect-devirtualization> | 对 VMProtect 3.x 纯函数采用动态执行、符号执行和 LLVM lifting，按输入输出约束恢复等价逻辑。README 明确列出纯函数、MBA 和多基本块示例及局限。 | 高；研究型代码和案例完整。目标主要是 Windows x64 VMProtect，不能直接套到 Android `libnpvmp.so`。 |
| VMProtect-2-Reverse-Engineering | <https://github.com/CKCat/VMProtect-2-Reverse-Engineering> | 配套 VMProtect 2 架构分析和静态分析文章，仓库收集虚拟机布局、handler 和辅助代码。 | 中高；适合学习 VM 状态、VIP/VSP、handler 映射。版本针对 VMP2，跨版本需要重新建立特征。 |
| NoVmp | <https://github.com/can1357/NoVmp> | 基于 VTIL 的 VMProtect x64 3.0--3.5 静态去虚拟化，把 handler/字节码提升为中间表示并可选重编译。 | 高；项目边界和版本写得明确。平台是 x64 PE，不是 Android ELF。 |
| titan-1 | <https://github.com/gmh5225/titan-1> | Triton 仿真和符号执行，按 Triton AST 模式匹配 VM handler，传播虚拟寄存器和栈状态。 | 中高；算法路线清楚，适合作为 handler 语义匹配器的参考；仓库状态和目标版本需本地验证。 |

### 适用边界

这些 VMP 工具针对 Windows PE/x64。NP 的 `libnpvmp.so` 是 Android ELF/ART 保护层，不能把 VMP 项目报告直接写成“已恢复”。可移植的部分是：VM 状态建模、handler 分类、动态轨迹到 IR、等价性测试和置信度记录；平台相关的部分必须在 Android AArch64/ARMv7 上重新实现。

## GitHub：Native 混淆、样本和基础设施

| 项目 | URL | 核心方法 | 可信度 / 可复现性 |
|---|---|---|---|
| ObfuScan | <https://github.com/kundan0575/ObfuScan> | 面向 Android APK 的 native SO 预扫描，定位混淆、loader 和高价值分析目标。适合作为统一特征检查器的规则来源。 | 中；仓库公开，但需要实际运行规则并检查误报率。 |
| Incognito | <https://github.com/aleisalem/Incognito> | Android 逆向挑战样本，native 代码使用 Tigress 混淆，适合验证控制流平坦化/不透明谓词检测。 | 中高；是可控实验 fixture，先审查构建说明再使用。 |
| android-inline-hook | <https://github.com/bytedance/android-inline-hook> | Android ARM/ARM64 通用 inline hook 库，提供运行时函数观察和短跳板能力。不是反混淆器，但可作为 native 证据采集后端。 | 高；成熟开源库。需要按 Android linker、PAC/BTI 和 ABI 版本测试。 |
| rizin | <https://github.com/rizinorg/rizin> | ELF/ARM/AArch64 静态分析、反汇编、脚本和分析数据库。适合作为无 IDA 环境的批处理后端。 | 高；通用工具，需结合符号、字符串和动态证据。 |
| radare2 | <https://github.com/radareorg/radare2> | `rabin2`/`r2`/脚本化 ELF 分析，适合批量提取导入、导出、重定位、字符串和函数边界。 | 高；通用工具，复杂 VM 代码仍需要人工确认。 |

## CSDN：JNI 动态注册

以下链接用于补充中文讲解和版本差异。文章质量差异较大，带“中”或“低”的条目必须用 GitHub 源码或 Android 源码交叉验证。

| 标题 | URL | 方法摘要 | 可信度 / 可复现性 |
|---|---|---|---|
| 逆向实战：如何用 Frida 揪出 Android SO 里隐藏的动态注册 JNI 函数 | <https://blog.csdn.net/weixin_30819163/article/details/95879663> | 对比 hook `RegisterNatives`、ART `ArtMethod::RegisterNative` 和 RuntimeCallbacks 三条路径，强调输出类名、签名、函数地址。 | 中；方法方向正确，需按本机 ART 符号和 Frida 版本复核。 |
| frida-registernatives 获取 so 层动态注册函数 | <https://blog.csdn.net/weixin_38387147/article/details/123177137> | 通过 Frida 监控 `libart.so` 的 `RegisterNatives`，打印注册过程。 | 中高；主题集中，适合与 GitHub fridaRegstNtv 互证。 |
| 使用 frida 获取 jni 动态注册函数的地址 | <https://blog.csdn.net/weixin_42486644/article/details/90312019> | 旧 Dalvik 路径通过 `dvmCallJNIMethod` 追踪 native 方法地址并解析 Method 结构。 | 中；对 Dalvik/早期系统有参考价值，现代 ART 不应直接套用。 |
| JNI 方法注册源码分析（JNI_OnLoad/动态注册/静态注册/方法替换） | <https://blog.csdn.net/stven_king/article/details/124482484> | 从 `JNI_OnLoad`、`FindClass`、`JNINativeMethod` 和 `RegisterNatives` 解释注册链。 | 中；适合建立源码级基线，实际 hook 仍需平台验证。 |
| 安卓逆向_6：NDK 开发 JNI、静态注册、JNI_OnLoad 动态注册 | <https://blog.csdn.net/freeking101/article/details/106044591> | 展示静态/动态注册、签名和加载流程，为测试 fixture 提供最小实现。 | 中；基础示例可复现，文章较旧。 |

## CSDN：VMP / 虚拟化保护

| 标题 | URL | 方法摘要 | 可信度 / 可复现性 |
|---|---|---|---|
| VMP 3.10+ 逆向分析：从虚拟机保护原理到实战破解 | <https://blog.csdn.net/weixin_33811539/article/details/89686688> | 讨论 VM 指令、handler、虚拟寄存器、动态跟踪、IDAPython 和硬件断点。 | 中；适用于 Windows VMP 语境，不能直接证明 Android `libnpvmp.so` 兼容。 |
| Mergen 实战案例：VMProtect 虚拟函数的高效反混淆全过程 | <https://blog.csdn.net/gitblog_00463/article/details/153505525> | 描述 LLVM IR 优化、汇编解析、handler 翻译和控制流重构。 | 低到中；需要核验 Mergen 版本、源码和示例输入，文章描述不能替代实验。 |
| Android 混合加固实战：VMP 与 Dex2C 技术解析与逆向对抗 | <https://blog.csdn.net/weixin_30650039/article/details/97290760> | 讨论 Dex2C/JNI 桥接、内存 dump、指令集和跨层数据流关联。 | 中；概念与 NP 的保护层相近，但样本、版本和脚本需独立验证。 |
| VMPDump 深度解析：如何突破 VMProtect 3.X x64 的代码虚拟化屏障 | <https://blog.csdn.net/gitblog_00562/article/details/141704549> | 以 VTIL 为中心描述动态转储、stub 识别、提升和导入修复。 | 低到中；先核对工具仓库和版本，再纳入调度器。 |

## CSDN：ZKM / Java 字节码反混淆

| 标题 | URL | 方法摘要 | 可信度 / 可复现性 |
|---|---|---|---|
| Threadtear：一款多功能 Java 代码反混淆工具套件 | <https://blog.csdn.net/weixin_47083537/article/details/106946037> | 介绍 Threadtear 的任务链，覆盖字节码清理、访问反混淆、字符串反混淆和调试；文中明确提到 ZKM、Stringer 和 Android。 | 中高；工具本身可查源代码，需锁定提交版本并用测试 JAR 验证每个 pass。 |
| Java 反混淆工具 flaming-shame：还原字节码符号、字符串与控制流 | <https://blog.csdn.net/weixin_28832121/article/details/164440095> | 以 ASM 构建结构图，结合名称熵、字符串解密模式和控制流重建。 | 中；适合启发式规则设计，反射、自修改和运行时解密场景仍需动态证据。 |
| 【亲测免费】Threadtear：Java 多功能的反混淆工具 | <https://blog.csdn.net/gitblog_01065/article/details/141416245> | Threadtear 的安装、任务顺序和 ZKM/Stringer 兼容性说明。 | 中；与其他转载重复，作为工具入口而非独立证据。 |

## CSDN：Native/OLLVM 分析

| 标题 | URL | 方法摘要 | 可信度 / 可复现性 |
|---|---|---|---|
| 实战指南：用 Frida 动态分析 OLLVM 混淆的 Android Native 代码 | <https://blog.csdn.net/weixin_29324877/article/details/158780823> | 通过 Frida 追踪控制流平坦化、状态变量、JNI 边界和内存 dump，再结合循环识别还原算法。 | 中；思路适合作为运行时阶段参考，脚本需在本机 ABI 上复现。 |
| 安卓逆向静态分析工具链全解析与应用实践 | <https://blog.csdn.net/weixin_30423065/article/details/162981627> | 串联 apktool/JADX/IDA/rabin2、多 DEX 和 SO 分析，强调调用链、字符串和控制流证据。 | 中；工具链描述实用，具体结论需要输入样本重跑。 |
| 【安全】【技术分析】android 反混淆分析记录 | <https://blog.csdn.net/weixin_39020940/article/details/82956543> | 记录 Android 类名/方法名重命名和工具辅助分析。 | 中低；缺乏统一基准和可执行脚本，适合关键词参考。 |

## 统一特征检查器设计

### 静态检查项

1. **APK/DEX**：多 DEX、`System.loadLibrary`、native 方法数量、`Protect`/`VM`/`classesInit*` 命名、字符串池 XOR/RC4/AES 形态、极高标识符熵、异常的 synthetic/bridge 方法比例。
2. **ELF**：`JNI_OnLoad`、`RegisterNatives`/`FindClass`/`GetMethodID` 导入或调用指针表、`dlopen`/`dlsym`/`mprotect`、`ptrace`、`/proc/self/maps`/`/proc/*/status`、可执行匿名映射、RWX 段、`.init_array` 初始化数量、剥离符号和高熵只读段。
3. **VM/解释器**：大规模间接跳转、固定状态结构、VIP/VSP/虚拟栈读写、handler 表、单一解释器入口被大量调用、解码循环和自修改代码；输出候选特征与证据地址，禁止直接命名为“VMP”。
4. **ZKM/Java**：类/方法名熵、异常控制流、反射调用密度、字符串解密调用图、`invokedynamic`/自定义属性异常、控制流平坦化的 dispatcher/状态变量。Threadtear/ASM pass 必须记录前后字节码哈希。

### 动态证据项

- `RegisterNatives` / `ArtMethod::RegisterNative` 的类名、方法名、签名、函数指针、模块基址、偏移、线程和调用栈。
- `JNI_OnLoad`、`.init_array`、`classesInit0..9`、`vmInterpret` 的进入/返回、参数摘要和内存页权限变化。
- 代码解密或加载后的内存映像哈希、DEX 加载事件、函数调用轨迹和重复执行的一致性。
- 每个恢复项必须关联静态地址、动态事件和验证用输入/输出；只有伪代码或单次轨迹时，状态应为 `partial`。

### 结果等级

- `observed`：只观察到字符串、导入或调用点。
- `mapped`：JNI 方法已映射到模块和偏移，有动态注册证据。
- `lifted`：native/VM 指令已提升到可审查 IR/伪代码，并有多组输入输出验证。
- `reconstructed`：控制流、数据流、异常和跨层调用均通过回放或等价性测试。
- `full-deobf`：所有高价值 Java/JNI/native/VM 边界达到 `reconstructed`，无 `opaque` 方法；否则必须标记剩余边界，不能使用 full-deobf 标签。

## 统一调度器和 20+80 任务制度

建议调度器以证据为中心，而不是按文件数量宣布完成：

1. `triage`：APK、DEX、ELF、ABI、保护标记和环境检查。
2. `java`：JADX/ASM/Threadtear 字符串、控制流和类图 pass。
3. `jni`：静态 JNI 声明、动态 `RegisterNatives`、`JNI_OnLoad` 和 ART 版本适配。
4. `native`：rabin2/radare2/Ghidra 函数边界、导入、初始化、反调试和 VM 候选识别。
5. `dynamic`：本地 Android 沙盒或用户提供的 MuMu/AVD，采集注册、内存页、DEX 和调用轨迹。
6. `lift`：对已采集 VM handler 做 IR lifting、符号/具体执行和输入输出等价性测试。
7. `synthesis`：汇总映射、证据、未恢复项和可复现命令，生成报告与审计日志。

并行控制可采用“20 个一级 worker + 最多 80 个二级任务”的逻辑队列，实际并发受 `agents.max_threads=200` 和 `max_depth=2` 限制。每个任务必须提交 `input_hash`、工具版本、命令、输出路径、证据地址、状态等级和失败原因；父任务只合并有证据的结果。动态阶段没有 Android 设备/模拟器时应保持 `blocked_on_runtime`，不能把 JADX 或 Ghidra 的猜测源码提升为 native 完整恢复。

## 对本项目的优先级

1. 先用 GitHub 的 `fridaRegstNtv`、`hook_ArtMethod_RegisterNative` 和 `frida_qbdi_hook` 生成 `libnpprotect.so` 的真实 JNI 映射和 `vmInterpret` 调用轨迹。
2. 再用 Ghidra/radare2 对每个映射偏移建立函数摘要；对 VM 解释器按状态结构、handler 表和解码循环分组。
3. 对 Java 层用 Threadtear/ASM 风格 pass 处理字符串和控制流，并以原始 DEX 哈希、修改后 DEX 哈希和运行结果做回归。
4. 若用户提供 MuMu/AVD，动态 worker 负责捕获加载后 DEX、代码页和注册表；否则交付应明确列出 `opaque native` 和 `blocked_on_runtime`。

## 参考可信度结论

GitHub 源码项目是本调度器的主要可执行依据；CSDN 文章用于中文概念、版本差异和关键词补充。所有涉及 VMP 的资料大多针对 Windows PE/x64，不能直接证明 Android ELF 保护层可用；所有涉及 ART 内部结构的资料都需要按系统版本重新定位。任何报告只有在动态映射、native lifting 和多组行为验证完成后，才可标记 `full-deobf`。
