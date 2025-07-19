namespace CorePlatform.Interfaces
{
    public interface IPlugin
    {
        string Name { get; }
        string Description { get; }
        void Load();
        void Unload();
        void RunTest(Action<string> logCallback);
    }

    public interface IScriptablePlugin : IPlugin
    {
        string? ExecuteScriptCommand(string commandName, string parameters);
        string[] GetAvailableScriptCommands();
    }

    public interface I3DSceneManager
    {
        void AddWorkpieceModel(object model);
        void RemoveWorkpieceModel(string modelId);
        void UpdateWorkpieceModel(object model);
        void AddPathSequence(object sequence);
        void RemovePathSequence(string sequenceId);
        void UpdatePathSequence(object sequence);
        void SetRobotConfiguration(object robotConfig);
        void UpdateRobotPose(string robotId, object newPose);
        void ResetCamera();
        void ZoomExtents();
    }

    public interface I3DInteractionProvider
    {
        void RegisterClickListener(Action<string> onObjectClicked);
        void UnregisterClickListener(Action<string> onObjectClicked);
        string PickObjectAtScreenCoordinate(double screenX, double screenY);
        void SetInteractionMode(InteractionMode mode);
    }

    public enum InteractionMode
    {
        Navigate,
        Select,
        DrawPath
    }
}
