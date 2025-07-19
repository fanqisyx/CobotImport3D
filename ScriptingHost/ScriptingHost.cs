using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CorePlatform.Interfaces;
using Microsoft.CodeAnalysis.CSharp.Scripting;
using Microsoft.CodeAnalysis.Scripting;

namespace ScriptingHost
{
    public class ScriptingHost
    {
        private readonly List<IPlugin> _plugins;

        public ScriptingHost(List<IPlugin> plugins)
        {
            _plugins = plugins;
        }

        public async Task<object?> ExecuteScript(string script)
        {
            var globals = new ScriptingHostGlobals
            {
                Host = new HostApi(_plugins)
            };

            var options = ScriptOptions.Default.WithReferences(typeof(HostApi).Assembly, typeof(IPlugin).Assembly);
            var result = await CSharpScript.EvaluateAsync(script, options, globals);
            return result;
        }
    }

    public class HostApi
    {
        private readonly List<IPlugin> _plugins;

        public HostApi(List<IPlugin> plugins)
        {
            _plugins = plugins;
        }

        public void print(string message)
        {
            Console.WriteLine(message);
        }

        public string[] ListPluginNames()
        {
            return _plugins.Select(p => p.Name).ToArray();
        }

        public string? ExecutePluginCommand(string pluginName, string commandName, string parameters)
        {
            var plugin = _plugins.OfType<IScriptablePlugin>().FirstOrDefault(p => p.Name == pluginName);
            return plugin?.ExecuteScriptCommand(commandName, parameters);
        }
    }

    public class ScriptingHostGlobals
    {
        public HostApi? Host { get; set; }
    }
}
