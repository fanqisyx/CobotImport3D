namespace CorePlatform.Data
{
    public struct Vector3D
    {
        public double X { get; set; }
        public double Y { get; set; }
        public double Z { get; set; }

        public Vector3D(double x, double y, double z)
        {
            X = x;
            Y = y;
            Z = z;
        }
    }

    public struct Quaternion
    {
        public double W { get; set; }
        public double X { get; set; }
        public double Y { get; set; }
        public double Z { get; set; }

        public Quaternion(double w, double x, double y, double z)
        {
            W = w;
            X = x;
            Y = y;
            Z = z;
        }
    }

    public struct Pose
    {
        public Vector3D Position { get; set; }
        public Quaternion Orientation { get; set; }

        public Pose(Vector3D position, Quaternion orientation)
        {
            Position = position;
            Orientation = orientation;
        }
    }

    public class ProjectFile
    {
        public int Version { get; set; } = 1;
        public string? ProjectName { get; set; }
        public string? Description { get; set; }
        public DateTime CreationTime { get; set; }
        public DateTime LastModifiedTime { get; set; }
        public WorkpieceModel? Workpiece { get; set; }
        public List<PathSequence> PathSequences { get; set; } = new List<PathSequence>();
        public RobotConfiguration? RobotConfig { get; set; }
    }

    public class WorkpieceModel
    {
        public string? ModelId { get; set; }
        public string? Name { get; set; }
        public string? FilePath { get; set; }
        public string? FileFormat { get; set; }
        public Pose Offset { get; set; }
    }

    public class PathSequence
    {
        public string? Id { get; set; }
        public string? Name { get; set; }
        public bool IsVisible { get; set; } = true;
        public List<PathSegment> Segments { get; set; } = new List<PathSegment>();
    }

    public class PathSegment
    {
        public string? Id { get; set; }
        public string? Name { get; set; }
        public PathSegmentType Type { get; set; }
        public List<PathPoint> Points { get; set; } = new List<PathPoint>();
        public IOConfiguration? IOConfig { get; set; }
    }

    public enum PathSegmentType
    {
        Point,
        Line,
        Spline,
        FollowSurface
    }

    public class PathPoint
    {
        public string? Id { get; set; }
        public Pose Pose { get; set; }
        public string? Description { get; set; }
    }

    public class IOConfiguration
    {
        public List<IOEvent> StartEvents { get; set; } = new List<IOEvent>();
        public List<IOEvent> EndEvents { get; set; } = new List<IOEvent>();
    }

    public class IOEvent
    {
        public IOType Type { get; set; }
        public string? TagName { get; set; }
        public string? Value { get; set; }
        public int DelayMs { get; set; }
        public string? Description { get; set; }
    }

    public enum IOType
    {
        DigitalOutput,
        DigitalInput,
        AnalogOutput,
        TcpCommand,
        ModbusWrite
    }

    public class RobotConfiguration
    {
        public string? RobotBrand { get; set; }
        public string? RobotModel { get; set; }
        public string? SerialNumber { get; set; }
        public List<Joint> Joints { get; set; } = new List<Joint>();
        public ToolDefinition? Tool { get; set; }
    }

    public class Joint
    {
        public string? Name { get; set; }
        public JointType Type { get; set; }
        public double MinLimit { get; set; }
        public double MaxLimit { get; set; }
    }

    public enum JointType
    {
        Revolute,
        Prismatic
    }

    public class ToolDefinition
    {
        public string? ToolName { get; set; }
        public Pose ToolCenterPointOffset { get; set; }
        public double ToolWeight { get; set; }
        public Vector3D CenterOfMassOffset { get; set; }
    }
}
