using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[CompilerGenerated]
[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib._IRastrEvents_OnLogEventHandler")]
public delegate void _IRastrEvents_OnLogEventHandler([In] LogErrorCodes Code, [In] int Level, [In] int StageId, [In][MarshalAs(UnmanagedType.BStr)] string TableName, [In] int TableIndex, [In][MarshalAs(UnmanagedType.BStr)] string Description, [In][MarshalAs(UnmanagedType.BStr)] string FormName);
