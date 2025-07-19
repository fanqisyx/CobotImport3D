using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using CorePlatform.Interfaces;

namespace RobotPTE.UI
{
    public class PluginManager
    {
        public List<IPlugin> Plugins { get; } = new List<IPlugin>();

        public void LoadPlugins(string path)
        {
            if (!Directory.Exists(path))
            {
                return;
            }

            var pluginAssemblies = Directory.GetFiles(path, "*.dll");

            foreach (var assemblyFile in pluginAssemblies)
            {
                var assembly = Assembly.LoadFrom(assemblyFile);
                var pluginTypes = assembly.GetTypes().Where(t => typeof(IPlugin).IsAssignableFrom(t) && !t.IsInterface);

                foreach (var pluginType in pluginTypes)
                {
                    var plugin = (IPlugin?)Activator.CreateInstance(pluginType);
                    if (plugin != null)
                    {
                        Plugins.Add(plugin);
                        plugin.Load();
                    }
                }
            }
        }
    }
}
