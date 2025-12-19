using System.Collections;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[ComImport]
[CompilerGenerated]
[DefaultMember("Item")]
[Guid("7E534FE3-B0C6-11D5-A75D-005004526FE6")]
[TypeIdentifier]
public interface ICols : IEnumerable
{
	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(0)]
	[return: MarshalAs(UnmanagedType.Struct)]
	object Item([In][MarshalAs(UnmanagedType.Struct)] object Index);
}
