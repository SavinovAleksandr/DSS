using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[ComImport]
[CompilerGenerated]
[Guid("708E3897-3EF5-4BEC-B0C5-F5B13A8D448B")]
[TypeIdentifier]
public interface IFWDynamic
{
	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(1)]
	RastrRetCode Run();

	void _VtblGap1_2();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(4)]
	RastrRetCode RunEMSmode();

	[DispId(5)]
	DFWSyncLossCause SyncLossCause
	{
		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(5)]
		get;
	}

	void _VtblGap2_1();

	[DispId(7)]
	double TimeReached
	{
		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(7)]
		get;
	}

	[DispId(8)]
	string ResultMessage
	{
		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(8)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}
}
