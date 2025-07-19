using System;
using System.IO;
using System.Threading.Tasks;
using ScriptingHost;

namespace RobotPTE.UI
{
    public class ScriptingManager
    {
        private readonly ScriptingHost.ScriptingHost _scriptingHost;

        public ScriptingManager(PluginManager pluginManager)
        {
            _scriptingHost = new ScriptingHost.ScriptingHost(pluginManager.Plugins);
        }

        public async Task RunScript(string scriptPath)
        {
            if (!File.Exists(scriptPath))
            {
                Console.WriteLine($"Script file not found: {scriptPath}");
                return;
            }

            var script = File.ReadAllText(scriptPath);
            var result = await _scriptingHost.ExecuteScript(script);
            Console.WriteLine($"Script result: {result}");
        }
    }
}
