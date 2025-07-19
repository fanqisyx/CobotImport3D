using System;
using CorePlatform.Interfaces;

namespace Plugin.IO
{
    public class IOPlugin : IPlugin
    {
        public string Name => "IO Plugin";
        public string Description => "A plugin for handling IO events.";

        public void Load()
        {
            Console.WriteLine($"{Name} loaded.");
        }

        public void Unload()
        {
            Console.WriteLine($"{Name} unloaded.");
        }

        public void RunTest(Action<string> logCallback)
        {
            logCallback($"{Name} test started.");
            logCallback($"{Name} test finished.");
        }
    }
}
