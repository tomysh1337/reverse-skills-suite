# AndroidReverse101 可复用流程

本参考将 [Evil0ctal/AndroidReverse101](https://github.com/Evil0ctal/AndroidReverse101) 的公开课程结构提炼为可调度步骤。内容根据主分支提交 [`9b72d20439155893ab2ce1b8af56af41c17d0411`](https://github.com/Evil0ctal/AndroidReverse101/commit/9b72d20439155893ab2ce1b8af56af41c17d0411) 检查，避免复制课程原文。

## 来源与许可证

- 仓库：[AndroidReverse101](https://github.com/Evil0ctal/AndroidReverse101)
- 课程目录：[AndroidReverse101/](https://github.com/Evil0ctal/AndroidReverse101/tree/main/AndroidReverse101)
- 课程 README：[README.md](https://github.com/Evil0ctal/AndroidReverse101/blob/main/README.md)
- 许可证：[LICENSE](https://github.com/Evil0ctal/AndroidReverse101/blob/main/LICENSE)
- 许可证结论：根目录为 **MIT License**，版权声明为 `Copyright (c) 2025 Evil0ctal`。引用、改编和再分发本参考时保留来源链接、版权声明和 MIT 许可文本；本套件不复制课程正文或仓库内 APK。
- `Crackmes/` 含练习 APK。其样本不自动纳入本套件发布物，除非另行确认每个样本的分发条款。
- 仓库没有发现独立于根目录的第二份许可证；第三方工具（IDA、Frida、Ghidra、apktool 等）仍以各自许可证和安装条款为准。

## 课程覆盖到调度阶段的映射

| 阶段 | 来源章节（相对路径） | 可复用主题 | 调度输出 |
|---|---|---|---|
| 基础与运行时 | `第一阶段_计算机基础_逆向概论/Day_9_Android_CPU_架构解析.md` 至 `Day_19_Android_APP_安全机制.md` | ARM/ARM64、Dalvik/ART、APK 加载、进程/权限、ELF、Native 调试和 Android 安全机制 | `reports/runtime-baseline.md`、ABI/ART 版本记录、工具版本 |
| APK/DEX | `第二阶段_APK逆向基础/Day_21_APK_文件结构解析.md` 至 `Day_26_APK_重新打包_签名.md` | APK ZIP、Manifest、DEX、Smali、JADX/apktool/baksmali/dex2jar、打包和签名验证 | `reports/apk-fingerprint.json`、`reports/dex-inventory.csv`、`reports/package-check.md` |
| 动态分析 | `第二阶段_APK逆向基础/Day_27_动态调试入门.md` 至 `Day_31_Xposed_入门.md` | ADB/logcat、Frida Java/Native hook、GDB/LLDB、JNI 边界和 Xposed 适配 | `reports/runtime-events.jsonl`、`reports/jni-map.csv`、`reports/module-map.csv` |
| 混淆/加固 | `第二阶段_APK逆向基础/Day_34_Android_代码混淆与解混淆.md`、`Day_40_Android_加固原理.md`、`Day_41_解密加固_APK_初级.md` | ProGuard/R8/DexGuard 识别、壳/运行时 DEX、Frida/GDB 采集和静态复核 | `reports/obfuscation-features.json`、`reports/dynamic-dex.csv`、`reports/dex-hashes.csv` |
| Native/挑战 | `第二阶段_APK逆向基础/Day_30_逆向_JNI_和_Native_方法.md`、`第三阶段_高级逆向_CTF挑战/Day_60_深入分析_CTF_逆向挑战.md`、`Day_100_终极挑战_逆向一个完整_APP.md` | SO/ELF、IDA/Ghidra/objdump、JNI/native 调用、网络/日志/行为关联 | `reports/native-functions.csv`、`reports/call-traces.jsonl`、`reports/analysis-summary.md` |

课程中的 `Day_28` 文件实际名为 `Day_28_使用_Frida_Hook_Java_方法.md`；调度器按实际文件名解析，不依赖标题文字。

## 工具硬门禁和证据矩阵

“硬门禁”表示缺少工具或证据时该阶段只能是 `BLOCKED`/`PARTIAL`，不能晋级为完整反混淆。课程中出现的绕过、修改或重打包示例仅作为实验流程，调度器始终在复制样本和独立输出目录中运行。

| 流程 ID | 任务 | 必需工具 | 硬门禁证据 | 通过后状态 |
|---|---|---|---|---|
| AR101-01 | 样本指纹与设备基线 | `sha256sum`/`Get-FileHash`、`zipinfo`/`7z`、`adb`（动态时） | 原 APK SHA-256、文件清单、ABI、Android API/ART 版本、命令日志 | `fingerprinted` |
| AR101-02 | Manifest/APK 结构 | `apktool`、`aapt2` 或 `apkanalyzer` | Manifest 解码、组件/权限表、资源和 DEX 清单，输入哈希与工具版本 | `apk-indexed` |
| AR101-03 | Java/DEX 反编译 | `jadx`；必要时 `baksmali`、`dex2jar`、CFR/Vineflower | 每个 DEX 的哈希、源码/Smali 输出、反编译日志、失败类清单 | `managed-partial` |
| AR101-04 | ELF/SO 静态分析 | `readelf`、`objdump`、`nm`，以及 Ghidra/IDA/radare2/rizin 中至少一个 | ELF 头/段/导入导出、函数清单、关键函数反编译或注释地址、分析数据库/命令日志 | `native-indexed` |
| AR101-05 | Java 运行时追踪 | `adb`、Frida；可选 Xposed | 进程包名、脚本哈希、Java 类/方法/参数摘要、logcat、设备信息 | `java-observed` |
| AR101-06 | JNI 动态注册 | Frida `RegisterNatives`/`ArtMethod::RegisterNative` hook；必要时 GDB/LLDB | 类名、方法名、签名、函数指针、模块基址、RVA、线程、调用栈、运行时间戳 | `jni-mapped` |
| AR101-07 | Native 动态边界 | Frida `Interceptor`、GDB/LLDB；AArch64 指令跟踪可用 QBDI | `JNI_OnLoad`/`.init_array`/关键导出进入退出、模块映射、页权限变化、输入输出摘要 | `native-observed` |
| AR101-08 | 加固/运行时 DEX | Frida、GDB/LLDB、APKiD；必要时 FRIDA-DEXDump | 运行时 DEX 路径/哈希、加载事件、内存范围、静态 DEX 对照和采集脚本日志 | `runtime-dex-captured` |
| AR101-09 | 混淆映射与验证 | JADX/ASM/Threadtear 或等价 pass、`javap`/DEX 校验器 | 前后字节码哈希、映射 CSV、字符串/控制流变换证据、回放结果 | `managed-reconstructed` |
| AR101-10 | 导出/重打包回归 | `apktool`/smali、`zipalign`、`apksigner`、`keytool` | 修改包独立哈希、签名证书指纹、安装/启动日志；不得宣称仍具有原签名 | `package-verified` |

### 门禁规则

- AR101-01 至 AR101-04 可在离线主机完成，但只产生静态状态；不含运行时映射。
- AR101-05 至 AR101-08 必须有 Android 模拟器或设备。MuMu 只有在 `adb devices` 可见、包安装成功且 logcat 可收集时才算满足门禁。
- AR101-06 没有 `RegisterNatives`/`ArtMethod::RegisterNative` 事件时，不得将 Java native 声明与 native 地址自动配对。
- AR101-08 只有内存 dump 没有 DEX 哈希、加载事件和静态对照时，状态保持 `runtime-dex-captured-partial`。
- AR101-09 只能使用有映射或有运行时行为证据的重命名；启发式名称必须标记 `heuristic`。
- AR101-10 的签名是测试包签名，不等于原始发行签名；原 APK 始终保持不变。
- 任何 JNI/native/VM 方法仍为 stub、opaque dispatcher 或未解释的 `vmInterpret` 调用时，最终状态保持 `PARTIAL`。

## 可执行调度模板

```yaml
source:
  repository: Evil0ctal/AndroidReverse101
  commit: 9b72d20439155893ab2ce1b8af56af41c17d0411
  license: MIT
  license_notice_required: true

stages:
  - id: AR101-01
    tools: [hash, zipinfo, adb]
    evidence: [apk_sha256, file_manifest, abi, art_version]
  - id: AR101-02
    tools: [apktool, aapt2]
    evidence: [manifest_xml, permissions, components, dex_inventory]
  - id: AR101-03
    tools: [jadx, baksmali, dex2jar]
    evidence: [dex_hashes, sources, smali, decompile_log]
  - id: AR101-04
    tools: [readelf, objdump, ghidra_or_ida_or_r2]
    evidence: [elf_headers, imports, functions, callgraphs]
  - id: AR101-05
    tools: [adb, frida]
    evidence: [process, script_hash, java_events, logcat]
  - id: AR101-06
    tools: [frida, art_symbol_resolver]
    evidence: [class, method, signature, fnptr, module, rva, backtrace]
  - id: AR101-07
    tools: [frida, gdb_or_lldb]
    evidence: [jni_onload, init_array, memory_maps, page_protection]
  - id: AR101-08
    tools: [frida, apkid, dex_dump_optional]
    evidence: [runtime_dex_hash, load_event, memory_range, static_match]
  - id: AR101-09
    tools: [asm_pass, bytecode_verifier]
    evidence: [mapping_csv, before_after_hash, replay_results]
  - id: AR101-10
    tools: [apktool, zipalign, apksigner, keytool]
    evidence: [derived_apk_hash, cert_fingerprint, install_log]
```

## 与完整反混淆门的关系

AndroidReverse101 提供的是学习和实验流程，不是“完整恢复”证明。调度器必须继续满足根技能中的 `FULL_DEOBF_COMPLETE` 门：所有 DEX、JNI 注册、native 函数体、VM handler、动态加载代码和关键行为都有对应证据；任何缺失工具、缺失运行时或未解释 native/VM 边界都保持 `PARTIAL`，并记录下一步证据需求。
