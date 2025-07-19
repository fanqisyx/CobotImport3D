using System;
using CorePlatform.Interfaces;

namespace Plugin.RobotCommunicator
{
    public class RobotCommunicatorPlugin : IPlugin
    {
        public string Name => "Robot Communicator Plugin";
        public string Description => "A plugin for communicating with robots.";

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
