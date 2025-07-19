using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;

namespace RobotPTE.UI;

public partial class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override async void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow();
        }

        var pluginManager = new PluginManager();
        pluginManager.LoadPlugins("Plugins");

        var scriptingManager = new ScriptingManager(pluginManager);
        await scriptingManager.RunScript("script.csx");

        base.OnFrameworkInitializationCompleted();
    }
}
