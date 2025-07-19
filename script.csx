Host.print("Hello from script!");
var plugins = Host.ListPluginNames();
foreach (var p in plugins)
{
    Host.print($"Plugin: {p}");
}

var status = Host.ExecutePluginCommand("Sample Plugin", "getstatus", "");
Host.print($"Status from sample plugin: {status}");

var echo = Host.ExecutePluginCommand("Sample Plugin", "echo", "Hello from script!");
Host.print($"Echo from sample plugin: {echo}");
