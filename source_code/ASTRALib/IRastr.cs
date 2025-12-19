using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace ASTRALib;

[ComImport]
[CompilerGenerated]
[Guid("84B0508C-ABC9-11D3-B740-00500454CF3F")]
[TypeIdentifier]
public interface IRastr
{
	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(2)]
	void Load([In] RG_KOD kd, [In][MarshalAs(UnmanagedType.BStr)] string Name, [In][MarshalAs(UnmanagedType.BStr)] string shabl);

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(3)]
	RastrRetCode rgm([In][MarshalAs(UnmanagedType.BStr)] string param);

	void _VtblGap1_3();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(13)]
	void Save([In][MarshalAs(UnmanagedType.BStr)] string Name, [In][MarshalAs(UnmanagedType.BStr)] string templ);

	[DispId(19)]
	Tables Tables
	{
		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(19)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	void _VtblGap2_6();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(25)]
	void NewFile([MarshalAs(UnmanagedType.BStr)] string shabl);

	void _VtblGap3_30();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(54)]
	RastrRetCode step_ut([In][MarshalAs(UnmanagedType.BStr)] string param);

	void _VtblGap4_5();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(60)]
	void ApplyVariant([In] int num, [In] double start_time = 0.0, [In] double end_time = 1000000.0, [In] int applied = 0);

	void _VtblGap5_66();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(128)]
	[return: MarshalAs(UnmanagedType.Interface)]
	FWDynamic FWDynamic();

	void _VtblGap6_2();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(131)]
	[return: MarshalAs(UnmanagedType.Struct)]
	object GetChainedGraphSnapshot([MarshalAs(UnmanagedType.BStr)] string table, [MarshalAs(UnmanagedType.BStr)] string Field, int nIndex, int SnapshotFileIndex);

	void _VtblGap7_14();

	[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
	[DispId(146)]
	RastrRetCode LAPNUSMZU([MarshalAs(UnmanagedType.BStr)] string param);
}
