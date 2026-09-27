// Runtime evidence collector for an Android test emulator. It records JNI_OnLoad,
// RegisterNatives, library loads, and DEX loads; it does not alter return values.
'use strict';

const out = [];
function record(kind, data) {
  const row = { ts: Date.now(), kind, ...data };
  out.push(row);
  send(row);
}

function hookExport(moduleName, symbol, onEnter) {
  const address = Module.findExportByName(moduleName, symbol);
  if (address) Interceptor.attach(address, { onEnter(args) { onEnter.call(this, args); } });
}

['libart.so', 'libnativehelper.so'].forEach((moduleName) => {
  hookExport(moduleName, 'RegisterNatives', function (args) {
    record('RegisterNatives', { module: moduleName, clazz: args[0].toString(), methods: args[1].toString(), count: args[2].toInt32() });
  });
});

['libdl.so', null].forEach((moduleName) => {
  hookExport(moduleName, 'dlopen', function (args) {
    record('dlopen', { module: moduleName, path: args[0].readCString(), flags: args[1].toInt32() });
  });
});

Process.enumerateModules().forEach((m) => record('module_initial', { name: m.name, base: m.base.toString(), size: m.size, path: m.path }));
record('collector_ready', { pid: Process.id, arch: Process.arch });
