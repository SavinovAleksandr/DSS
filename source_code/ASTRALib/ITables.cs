using System.Collections;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[ComImport]
[CompilerGenerated]
[Guid("A44744E0-ADCE-11D5-A75D-005004526FE6")]
[DefaultMember("Item")]
[TypeIdentifier]
public interface ITables : IEnumerable
{
	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(0)]
	[return: MarshalAs(UnmanagedType.Struct)]
	object Item([In][MarshalAs(UnmanagedType.Struct)] object Index);
}
