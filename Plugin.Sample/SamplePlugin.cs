using System;
using CorePlatform.Interfaces;

namespace Plugin.Sample
{
    public class SamplePlugin : IScriptablePlugin
    {
        public string Name => "Sample Plugin";
        public string Description => "A sample plugin for testing.";

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

        public string? ExecuteScriptCommand(string commandName, string parameters)
        {
            switch (commandName.ToLower())
            {
                case "getstatus":
                    return "OK";
                case "echo":
                    return parameters;
                default:
                    return $"Unknown command: {commandName}";
            }
        }

        public string[] GetAvailableScriptCommands()
        {
            return new[] { "getstatus", "echo" };
        }
    }
}
