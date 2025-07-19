using System.Collections.Generic;
using CorePlatform.Data;

namespace RobotPTE.UI
{
    public class PathManager
    {
        public List<PathSequence> PathSequences { get; } = new List<PathSequence>();

        public void AddPathSequence(PathSequence sequence)
        {
            PathSequences.Add(sequence);
        }

        public void RemovePathSequence(string sequenceId)
        {
            PathSequences.RemoveAll(s => s.Id == sequenceId);
        }
    }
}
