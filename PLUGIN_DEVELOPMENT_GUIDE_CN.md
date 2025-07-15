# 插件开发指南 (PLUGIN_DEVELOPMENT_GUIDE_CN.md)

本指南旨在帮助开发者为 `TestPlatformExample` 项目创建新的插件。

## 1. 基本要求

- **.NET 版本**: 推荐使用 .NET 8，与主示例项目保持一致。
- **开发工具**: Visual Studio 2022 或其他兼容的 .NET IDE (如 VS Code)。

## 2. 创建插件项目

1.  **新建类库项目**:
    *   启动 Visual Studio 或使用 .NET CLI。
    *   创建一个新的 .NET 类库 (Class Library) 项目。例如，命名为 `MyCustomPlugin`。
    *   确保项目目标框架为 `net8.0` (或与 `CorePlatform.dll` 兼容的版本)。

2.  **添加对 `CorePlatform` 的引用**:
    *   您的插件需要实现 `CorePlatform.IPlugin` 接口。为此，您必须引用 `CorePlatform` 项目或其编译后的 `CorePlatform.dll`。
    *   **方式一：项目引用 (推荐，如果插件与主解决方案一起开发)**:
        编辑您的插件项目文件 (`.csproj`)，添加如下项目引用。请根据您的目录结构调整相对路径。
        ```xml
        <ItemGroup>
          <ProjectReference Include="..\CorePlatform\CorePlatform.csproj" />
          <!-- 假设 MyCustomPlugin 文件夹与 CorePlatform 文件夹同级 -->
        </ItemGroup>
        ```
    *   **方式二：DLL引用**:
        如果您将 `CorePlatform.dll` 作为单独的文件分发，可以在项目中添加对该 DLL 的引用。
        ```xml
        <ItemGroup>
          <Reference Include="CorePlatform.dll">
            <HintPath>..\Path\To\CorePlatform.dll</HintPath> <!-- 提供 CorePlatform.dll 的实际路径 -->
          </Reference>
        </ItemGroup>
        ```
        **注意**: 如果采用 DLL 引用，请确保在部署插件时，`CorePlatform.dll` 也被正确地复制到 `WinFormsUI` 的 `Plugins` 目录中 (详见部署步骤)。

## 3. 实现 `IPlugin` 接口

在您的插件项目中，创建一个公共类，并实现 `CorePlatform.IPlugin` 接口。

```csharp
using System;
using CorePlatform; // 确保 using CorePlatform 命名空间

namespace MyCustomPlugin
{
    public class MyPlugin : IPlugin
    {
        private Action<string>? _hostLogCallback; // 用于接收宿主程序的日志回调

        public string Name => "我的自定义插件"; // 插件名称

        public string Description => "这是一个自定义插件的简单示例。"; // 插件描述

        // 插件加载时调用
        public void Load()
        {
            // 初始化插件资源
            Console.WriteLine($"{Name} 已加载。"); // 也可以使用 _hostLogCallback 记录日志，但此时可能尚未设置
        }

        // 插件卸载时调用
        public void Unload()
        {
            // 释放插件资源
            _hostLogCallback?.Invoke($"{Name} 已卸载。");
            Console.WriteLine($"{Name} 已卸载。");
        }

        // 执行插件定义的测试（或主要功能）
        public void RunTest(Action<string> logCallback)
        {
            _hostLogCallback = logCallback; // 保存宿主提供的日志回调实例

            _hostLogCallback?.Invoke($"插件 '{Name}': 开始执行测试...");

            // 模拟测试步骤
            try
            {
                System.Threading.Thread.Sleep(500); // 模拟工作
                _hostLogCallback?.Invoke($"插件 '{Name}': 步骤 1 完成。");
                System.Threading.Thread.Sleep(1000); // 模拟更多工作
                _hostLogCallback?.Invoke($"插件 '{Name}': 步骤 2 完成。");
                _hostLogCallback?.Invoke($"插件 '{Name}': 测试成功结束。");
            }
            catch (Exception ex)
            {
                _hostLogCallback?.Invoke($"插件 '{Name}': 测试执行期间发生错误: {ex.Message}");
            }
        }
    }
}
```

## 4. 构建插件

编译您的插件项目，生成 DLL 文件 (例如，`MyCustomPlugin.dll`)。
通常，此 DLL 会在项目的 `bin/Debug/net8.0/` 或 `bin/Release/net8.0/` 目录下。

## 5. 部署插件到 `WinFormsUI`

1.  **找到 `WinFormsUI` 的运行目录**:
    这是 `WinFormsUI.exe` 所在的目录。如果您从 Visual Studio 运行，它通常是 `TestPlatformExample/WinFormsUI/bin/Debug/net8.0/` 或 `TestPlatformExample/WinFormsUI/bin/Release/net8.0/`。

2.  **创建 `Plugins` 文件夹**:
    在 `WinFormsUI` 的运行目录下，创建一个名为 `Plugins` 的子文件夹 (如果尚不存在)。

3.  **复制插件文件**:
    *   将您的插件 DLL (例如 `MyCustomPlugin.dll`) 复制到上述 `Plugins` 文件夹中。
    *   **重要**: 同时需要将 `CorePlatform.dll` 复制到此 `Plugins` 文件夹中。
        *   如果您的插件项目通过**项目引用**链接到 `CorePlatform`，则 `CorePlatform.dll` 通常会自动复制到您插件的输出目录中。您可以将您插件输出目录中的 `MyCustomPlugin.dll` 和 `CorePlatform.dll` 一起复制到 `WinFormsUI/Plugins/` 目录下。
        *   如果您的插件项目通过**DLL引用**链接到 `CorePlatform.dll`，则需要手动确保 `CorePlatform.dll` 与您的插件 DLL 一起位于 `Plugins` 文件夹中。

4.  **复制其他依赖项 (如果需要)**:
    如果您的插件依赖于任何其他第三方库 (并且这些库不是 .NET 运行时的一部分，也不是 `WinFormsUI` 主程序本身提供的)，您也需要将这些依赖 DLL 复制到 `Plugins` 文件夹或 `WinFormsUI` 的主运行目录中，以便 .NET 运行时能够找到它们。

## 6. 运行和测试

启动 `WinFormsUI` 应用程序。点击 "Load Plugins" (或类似) 按钮。应用程序的日志区域应显示您的插件被发现和加载的消息。随后，您可以通过 "Run Plugin Tests" 按钮来执行插件的 `RunTest` 方法。

## 7. 使插件支持脚本调用 (Making Plugins Scriptable)

平台提供了一个C#脚本执行引擎，允许用户通过编写脚本与已加载的插件进行交互。为了使您的插件能够被脚本调用，您需要实现 `CorePlatform.IScriptablePlugin` 接口。

**7.1 `IScriptablePlugin` 接口**

`IScriptablePlugin` 接口继承自 `IPlugin`，并额外定义了以下方法：

```csharp
namespace CorePlatform
{
    public interface IScriptablePlugin : IPlugin
    {
        // 执行从脚本传递过来的命令
        string? ExecuteScriptCommand(string commandName, string parameters);

        // 获取插件支持的脚本命令列表
        string[] GetAvailableScriptCommands(); // 新增方法
    }
}
```

**7.2 实现 `ExecuteScriptCommand` 方法**

在您的插件类中，除了实现 `IPlugin` 的成员外，还需实现 `ExecuteScriptCommand` 方法。

```csharp
// (确保您的插件类声明实现了 IScriptablePlugin)
// public class MyPlugin : IScriptablePlugin
// { ... }

public string? ExecuteScriptCommand(string commandName, string parameters)
{
    // 插件内部日志，可选
    Console.WriteLine($"插件 '{this.Name}': 收到脚本命令 '{commandName}'，参数: '{parameters}'");

    switch (commandName.ToLowerInvariant()) // 命令名称不区分大小写
    {
        case "getstatus":
            // 实现获取状态的逻辑
            return "状态: 一切正常";
        case "startevent":
            // 实现启动某个事件的逻辑，参数可能包含事件配置
            // bool success = PerformStartEvent(parameters);
            // return success ? "事件已启动" : "错误: 启动事件失败";
            return $"命令 'startevent' (参数: '{parameters}') 已被调用。请在插件中实现具体逻辑。";
        case "echoparam":
            return $"插件 '{this.Name}' 回显参数: {parameters}";
        // 在此添加更多命令分支
        default:
            return $"错误: 插件 '{this.Name}' 不支持命令 '{commandName}'。";
    }
}
```

**7.3 脚本如何调用**

在C#脚本中，可以通过全局的 `Host` 对象（`ScriptingHost` 类的实例）调用插件的命令。由于脚本引擎现在默认包含更多常用的 .NET 命名空间 (如 `System.IO`, `System.Text`, `System.Collections.Generic` 等) 和程序集引用，您可以直接在脚本中使用这些功能，而无需额外配置。

`Host` 对象提供的主要方法有：
- `Host.Log("消息")` 或 `Host.print("消息")`: 向主界面日志区域输出消息。
- `Host.ListPluginNames()`: 列出当前所有已加载插件的名称。
- `Host.ExecutePluginCommand("插件名称", "命令名称", "参数字符串")`: 执行指定插件的命令。

```csharp
// 脚本示例:
Host.print("尝试执行插件 'Sample Test Plugin' 的 'GetStatus' 命令...");
// Host.Log() 同样可用。 Host.print() 是一个方便的别名。

string pluginName = "Sample Test Plugin"; // 确保此名称与插件的 Name 属性一致
string? status = Host.ExecutePluginCommand(pluginName, "GetStatus", null); // GetStatus 命令不需要参数

if (status != null) {
    Host.print($"'{pluginName}' 的状态: {status}");
} else {
    Host.print($"未能获取 '{pluginName}' 的状态，或命令没有返回值。");
}

// 调用另一个命令，例如 SamplePlugin 中的 "Echo"
string? echoParams = "来自脚本的你好！";
string? echoResponse = Host.ExecutePluginCommand(pluginName, "Echo", echoParams);
Host.print($"'{pluginName}' Echo 命令的回应: {echoResponse ?? "null"}");

// 如果需要使用 MessageBox (System.Windows.Forms 命名空间已默认导入，如果宿主是WinForms程序)
// MessageBox.Show("这是一个来自脚本的提示框!", "脚本提示");
```

**7.4 `ExecuteScriptCommand` 实现建议**

*   **命令分发**: 使用 `switch` 语句（通常基于 `commandName.ToLowerInvariant()`）来处理不同的命令。
*   **参数解析**: `parameters` 是一个字符串。您的插件需要负责解析这个字符串以获取有用的数据。可以约定简单的格式（如逗号分隔），或者对于复杂数据，推荐使用JSON字符串，然后在插件中进行反序列化。
*   **返回值**: 方法返回 `string?`。这个字符串会传递回脚本，并可能由脚本记录或处理。确保返回有意义的信息，包括成功状态或错误详情。
*   **错误处理**: 在方法内部实现健壮的错误处理。如果命令执行失败，返回描述错误的字符串。
*   **日志**: 虽然 `ScriptingHost` 会记录命令的调用和返回，插件内部也可以使用 `Console.WriteLine` 或其他日志机制进行更详细的诊断。

**7.5 声明插件支持的脚本命令 (Declaring Supported Script Commands)**

为了让脚本编写者更容易发现您的插件支持哪些命令，您应该在实现了 `IScriptablePlugin` 接口的插件中，同时实现 `GetAvailableScriptCommands()` 方法。

```csharp
// IScriptablePlugin 接口中的 GetAvailableScriptCommands 方法定义:
// namespace CorePlatform {
//     public interface IScriptablePlugin : IPlugin {
//         // ... ExecuteScriptCommand ...
//         string[] GetAvailableScriptCommands();
//     }
// }
```

此方法应返回一个字符串数组，其中每个字符串都是您的插件通过 `ExecuteScriptCommand` 方法支持的一个 `commandName`。

**示例 (在 `SamplePlugin` 的 `MyPlugin.cs` 中):**
```csharp
public string[] GetAvailableScriptCommands()
{
    return new string[] { "GetStatus", "Echo", "Add" };
}
```
当插件被加载后，主程序可以通过调用此方法获取命令列表，并在“插件信息 (Plugin Info)”窗口中展示给用户。这极大地提高了插件脚本功能的可发现性。

---
遵循这些步骤，您应该能够成功开发并集成新的插件到 `TestPlatformExample` 平台中。
