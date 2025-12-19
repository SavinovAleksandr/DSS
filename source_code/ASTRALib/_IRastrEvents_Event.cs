using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[ComImport]
[CompilerGenerated]
[ComEventInterface(typeof(_IRastrEvents), typeof(_IRastrEvents))]
[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib._IRastrEvents_Event")]
public interface _IRastrEvents_Event
{
	void _VtblGap1_6();

	event _IRastrEvents_OnLogEventHandler OnLog;
}
