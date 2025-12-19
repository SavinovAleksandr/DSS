using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[ComImport]
[CompilerGenerated]
[InterfaceType(2)]
[Guid("84B0508D-ABC9-11D3-B740-00500454CF3F")]
[TypeIdentifier]
public interface _IRastrEvents
{
	void _VtblGap1_3();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(4)]
	void OnLog([In] LogErrorCodes Code, [In] int Level, [In] int StageId, [In][MarshalAs(UnmanagedType.BStr)] string TableName, [In] int TableIndex, [In][MarshalAs(UnmanagedType.BStr)] string Description, [In][MarshalAs(UnmanagedType.BStr)] string FormName);
}
