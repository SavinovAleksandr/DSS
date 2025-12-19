using System;
using System.CodeDom.Compiler;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Configuration;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Resources;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Markup;
using System.Windows.Threading;
using ASTRALib;
using Microsoft.Win32;
using OfficeOpenXml;
using OfficeOpenXml.Style;
using OxyPlot;
using OxyPlot.Axes;
using OxyPlot.Legends;
using OxyPlot.Series;
using OxyPlot.Wpf;
using Xls_prjt;
using rst_operations;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.Default | DebuggableAttribute.DebuggingModes.DisableOptimizations | DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints | DebuggableAttribute.DebuggingModes.EnableEditAndContinue)]
[assembly: AssemblyTitle("DynStabSpace")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("DynStabSpace")]
[assembly: AssemblyCopyright("Copyright ©  2025")]
[assembly: AssemblyTrademark("")]
[assembly: ComVisible(false)]
[assembly: ThemeInfo(/*Could not decode attribute arguments.*/)]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: TargetFramework(".NETFramework,Version=v4.7.2", FrameworkDisplayName = ".NET Framework 4.7.2")]
[assembly: AssemblyVersion("1.0.0.0")]
namespace rst_operations
{
	internal class RastrOperations
	{
		private Rastr _rastr;

		public RastrOperations()
		{
			_rastr = (Rastr)Activator.CreateInstance(Marshal.GetTypeFromCLSID(new Guid("EFC5E4AD-A3DD-11D3-B73F-00500454CF3F")));
		}

		~RastrOperations()
		{
			_rastr = null;
		}

		public static string FindTemplatePathWithExtension(string extension)
		{
			if (!Directory.Exists(Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\\RastrWIN3\\SHABLON\\"))
			{
				return null;
			}
			string[] files = Directory.GetFiles(Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\\RastrWIN3\\SHABLON\\");
			return files.FirstOrDefault((string filename) => Path.GetExtension(filename) == extension && Path.GetFileNameWithoutExtension(filename) != "базовый режим мт");
		}

		public void Load(string file)
		{
			string shabl = FindTemplatePathWithExtension(Path.GetExtension(file));
			_rastr.NewFile(shabl);
			_rastr.Load(RG_KOD.RG_REPL, file, FindTemplatePathWithExtension(Path.GetExtension(file)));
		}

		public void LoadTemplate(string _extension)
		{
			_rastr.NewFile(FindTemplatePathWithExtension(_extension));
		}

		public void Save(string file)
		{
			_rastr.Save(file, FindTemplatePathWithExtension(Path.GetExtension(file)));
		}

		public void Add(string file)
		{
			_rastr.Load(RG_KOD.RG_ADD, file, FindTemplatePathWithExtension(Path.GetExtension(file)));
		}

		public bool rgm(string _param = "", dynamic _iterations = null, dynamic _voltage = null)
		{
			table table = (dynamic)_rastr.Tables.Item("com_regim");
			col col = (dynamic)table.Cols.Item("it_max");
			col col2 = (dynamic)table.Cols.Item("dv_min");
			if (_iterations != null)
			{
				((ICol)col).set_Z(0, (object)_iterations);
			}
			if (_voltage != null)
			{
				((ICol)col2).set_Z(0, (object)_voltage);
			}
			return _rastr.rgm(_param) == RastrRetCode.AST_OK;
		}

		public int AddTableRow(string table)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table);
			table2.AddRow();
			return table2.Size - 1;
		}

		public void SetLineForUostCalc(int id1, int id2, double r, double x, double L)
		{
			table table = (dynamic)_rastr.Tables.Item("vetv");
			col col = (dynamic)table.Cols.Item("r");
			col col2 = (dynamic)table.Cols.Item("x");
			double num = L * r / 100.0;
			double num2 = L * x / 100.0;
			((ICol)col).set_Z(id1, (object)num);
			((ICol)col).set_Z(id2, (object)(r - num));
			((ICol)col2).set_Z(id1, (object)num2);
			((ICol)col2).set_Z(id2, (object)(x - num2));
			_rastr.rgm("");
		}

		public void ChangeRXForUostCalc(int x_id, double x, int r_id = 0, double r = -1.0)
		{
			table table = (dynamic)_rastr.Tables.Item("DFWAutoActionScn");
			col col = (dynamic)table.Cols.Item("Formula");
			((ICol)col).set_Z(x_id, (object)x.ToString().Replace(",", "."));
			if (r != -1.0)
			{
				((ICol)col).set_Z(r_id, (object)r.ToString().Replace(",", "."));
			}
		}

		public List<int> Selection(string table, string selection = "")
		{
			table table2 = (dynamic)_rastr.Tables.Item(table ?? "");
			table2.SetSel(selection ?? "");
			int num = ((ITable)table2).get_FindNextSel(-1);
			List<int> list = new List<int>();
			while (num != -1)
			{
				list.Add(num);
				num = ((ITable)table2).get_FindNextSel(num);
			}
			return list;
		}

		public bool ApplyVariant(int num, string file)
		{
			Load(file);
			_rastr.ApplyVariant(num);
			return rgm();
		}

		public dynamic getVal(string table, string col, string selection)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table);
			col col2 = (dynamic)table2.Cols.Item(col);
			table2.SetSel(selection ?? "");
			int num = ((ITable)table2).get_FindNextSel(-1);
			return (num != -1) ? ((ICol)col2).get_Z(num) : null;
		}

		public dynamic getVal(string table, string col, int index)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table);
			col col2 = (dynamic)table2.Cols.Item(col);
			return ((ICol)col2).get_Z(index);
		}

		public void setVal(string table, string col, int index, dynamic val)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table);
			col col2 = (dynamic)table2.Cols.Item(col);
			((ICol)col2).set_Z(index, (object)val);
		}

		public bool setVal(string table, string col, string selection, dynamic val)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table ?? "");
			col col2 = (dynamic)table2.Cols.Item(col ?? "");
			table2.SetSel(selection ?? "");
			int num = ((ITable)table2).get_FindNextSel(-1);
			if (num != -1)
			{
				((ICol)col2).set_Z(num, (object)val);
			}
			return num != -1;
		}

		public void setValВyCalc(string table, string col, string selection, dynamic val)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table);
			col col2 = (dynamic)table2.Cols.Item(col);
			table2.SetSel(selection);
			col2.Calc(val);
		}

		public void CreateScnFromLpn(string lpn_file, string lpn, string scn_file, string file = "")
		{
			LoadTemplate(".vrn");
			Load(lpn_file);
			table table = (dynamic)_rastr.Tables.Item("var_mer");
			col col = (dynamic)table.Cols.Item("Num");
			col col2 = (dynamic)table.Cols.Item("Type");
			table.AddRow();
			((ICol)col).set_Z(0, (object)1);
			((ICol)col2).set_Z(0, (object)1);
			_rastr.LAPNUSMZU("1" + lpn);
			Add(scn_file);
			if (file != "")
			{
				Save(file);
			}
		}

		public double Run_Ut()
		{
			table table = (dynamic)_rastr.Tables.Item("vetv");
			table table2 = (dynamic)_rastr.Tables.Item("ut_common");
			col col = (dynamic)table2.Cols.Item("sum_kfc");
			for (RastrRetCode rastrRetCode = _rastr.step_ut("i"); rastrRetCode == RastrRetCode.AST_OK; rastrRetCode = _rastr.step_ut("z"))
			{
			}
			return (dynamic)((ICol)col).get_Z(0);
		}

		public double Step(double _step = 1.0, bool init = true)
		{
			RastrRetCode rastrRetCode = RastrRetCode.AST_OK;
			table table = (dynamic)_rastr.Tables.Item("ut_common");
			col col = (dynamic)table.Cols.Item("sum_kfc");
			if (init)
			{
				rastrRetCode = _rastr.step_ut("i");
			}
			setVal("ut_common", "kfc", 0, _step);
			rastrRetCode = _rastr.step_ut("z");
			return (dynamic)((ICol)col).get_Z(0);
		}

		public void DynSettings()
		{
			table table = (dynamic)_rastr.Tables.Item("com_dynamics");
			col col = (dynamic)table.Cols.Item("MaxResultFiles");
			col col2 = (dynamic)table.Cols.Item("SnapAutoLoad");
			col col3 = (dynamic)table.Cols.Item("SnapMaxCount");
			((ICol)col).set_Z(0, (object)1);
			((ICol)col2).set_Z(0, (object)1);
			((ICol)col3).set_Z(0, (object)1);
		}

		public DynamicResult RunDynamic(bool _ems = false, double _MaxTime = -1.0)
		{
			DynamicResult result = default(DynamicResult);
			table table = (dynamic)_rastr.Tables.Item("com_dynamics");
			col col = (dynamic)table.Cols.Item("Tras");
			double num = (dynamic)((ICol)col).get_Z(0);
			LoadTemplate(".dfw");
			if (_ems && _MaxTime != -1.0)
			{
				((ICol)col).set_Z(0, (object)_MaxTime);
			}
			FWDynamic fWDynamic = _rastr.FWDynamic();
			RastrRetCode rastrRetCode = (_ems ? fWDynamic.RunEMSmode() : fWDynamic.Run());
			result.IsSuccess = rastrRetCode == RastrRetCode.AST_OK;
			result.IsStable = fWDynamic.SyncLossCause == DFWSyncLossCause.SYNC_LOSS_NONE;
			result.ResultMessage = ((fWDynamic.ResultMessage == "") ? " - " : fWDynamic.ResultMessage);
			result.TimeReached = fWDynamic.TimeReached;
			((ICol)col).set_Z(0, (object)num);
			return result;
		}

		public double FindCrtTime(double precision, double max_time)
		{
			double num = max_time;
			LoadTemplate(".dfw");
			ResetCrtTime(max_time);
			FWDynamic fWDynamic = _rastr.FWDynamic();
			RastrRetCode rastrRetCode = fWDynamic.RunEMSmode();
			if (fWDynamic.SyncLossCause != DFWSyncLossCause.SYNC_LOSS_NONE)
			{
				double num2 = max_time;
				double num3 = 0.0;
				double num4 = (num2 - num3) * 0.5;
				while (Math.Abs(num4) > precision || fWDynamic.SyncLossCause != DFWSyncLossCause.SYNC_LOSS_NONE)
				{
					num += num4 * (double)((fWDynamic.SyncLossCause == DFWSyncLossCause.SYNC_LOSS_NONE) ? 1 : (-1));
					ResetCrtTime(num);
					fWDynamic = _rastr.FWDynamic();
					rastrRetCode = fWDynamic.RunEMSmode();
					if (fWDynamic.SyncLossCause == DFWSyncLossCause.SYNC_LOSS_NONE)
					{
						num3 = num;
					}
					else
					{
						num2 = num;
					}
					num4 = (num2 - num3) * 0.5;
				}
			}
			return num;
		}

		private void ResetCrtTime(double dt)
		{
			double num = 1.0;
			List<int> list = Selection("DFWAutoActionScn");
			foreach (int item in list)
			{
				string text = getVal("DFWAutoActionScn", "ObjectClass", item);
				if (text == "node")
				{
					setVal("DFWAutoActionScn", "TimeStart", item, num);
					setVal("DFWAutoActionScn", "DT", item, dt);
				}
				else if (text == "vetv")
				{
					setVal("DFWAutoActionScn", "TimeStart", item, num + dt);
					setVal("DFWAutoActionScn", "DT", item, 999);
				}
			}
			setVal("com_dynamics", "Tras", 0, num + dt + 3.0);
		}

		public ShuntKZResult FindShuntKZ(int node, double u_ost, double x_isx, double r_isx = -1.0)
		{
			table table = (dynamic)_rastr.Tables.Item("com_dynamics");
			col col = (dynamic)table.Cols.Item("Tras");
			((ICol)col).set_Z(0, (object)1.1);
			LoadTemplate(".dfw");
			List<string> _prot = new List<string>();
			new ComAwareEventInfo(typeof(_IRastrEvents_Event), "OnLog").AddEventHandler(_rastr, (_IRastrEvents_OnLogEventHandler)delegate(LogErrorCodes Code, int Level, int StageId, string TableName, int TableIndex, string Description, string FormName)
			{
				if (Code == LogErrorCodes.LOG_INFO && Description.Contains("Величина остаточного напряжения в узле"))
				{
					_prot.Add(Description);
				}
			});
			double num = Math.Sqrt(((r_isx != -1.0) ? Math.Pow(r_isx, 2.0) : 0.0) + Math.Pow(x_isx, 2.0));
			double num2 = ((r_isx == -1.0) ? (Math.PI / 2.0) : Math.Atan(x_isx / r_isx));
			if (r_isx == -1.0)
			{
				CreateShuntScn(node, num * Math.Sin(num2));
			}
			else
			{
				CreateShuntScn(node, num * Math.Sin(num2), num * Math.Cos(num2));
			}
			FWDynamic fWDynamic = _rastr.FWDynamic();
			RastrRetCode rastrRetCode = fWDynamic.Run();
			double num3 = Convert.ToDouble(_prot.LastOrDefault().Split(new char[1] { '(' })[1].Split(new char[1] { ',' })[0].Replace(" кВ", "").Replace("Uкз=", "").Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator ?? ""));
			double num4 = getVal("node", "uhom", $"ny={node}");
			while (Math.Abs(num3 - u_ost) > Math.Min(2.0, 0.02 * num4))
			{
				num = num * u_ost / num3;
				if (r_isx == -1.0)
				{
					CreateShuntScn(node, num * Math.Sin(num2));
				}
				else
				{
					CreateShuntScn(node, num * Math.Sin(num2), num * Math.Cos(num2));
				}
				rastrRetCode = fWDynamic.Run();
				num3 = Convert.ToDouble(_prot.LastOrDefault().Split(new char[1] { '(' })[1].Split(new char[1] { ',' })[0].Replace(" кВ", "").Replace("Uкз=", "").Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator ?? ""));
				_prot.Clear();
			}
			return new ShuntKZResult
			{
				r = ((r_isx == -1.0) ? (-1.0) : (num * Math.Cos(num2))),
				x = num * Math.Sin(num2),
				u = num3
			};
		}

		private void CreateShuntScn(int node, double x, double r = -1.0)
		{
			LoadTemplate(".scn");
			table table = (dynamic)_rastr.Tables.Item("DFWAutoActionScn");
			col col = (dynamic)table.Cols.Item("Id");
			col col2 = (dynamic)table.Cols.Item("Type");
			col col3 = (dynamic)table.Cols.Item("Formula");
			col col4 = (dynamic)table.Cols.Item("ObjectClass");
			col col5 = (dynamic)table.Cols.Item("ObjectProp");
			col col6 = (dynamic)table.Cols.Item("ObjectKey");
			col col7 = (dynamic)table.Cols.Item("RunsCount");
			col col8 = (dynamic)table.Cols.Item("TimeStart");
			col col9 = (dynamic)table.Cols.Item("DT");
			table.AddRow();
			((ICol)col).set_Z(0, (object)table.Size);
			((ICol)col2).set_Z(0, (object)1);
			((ICol)col3).set_Z(0, (object)x.ToString().Replace(",", "."));
			((ICol)col4).set_Z(0, (object)"node");
			((ICol)col5).set_Z(0, (object)"x");
			((ICol)col6).set_Z(0, (object)node);
			((ICol)col7).set_Z(0, (object)1);
			((ICol)col8).set_Z(0, (object)1);
			((ICol)col9).set_Z(0, (object)0.06);
			if (r != -1.0)
			{
				table.AddRow();
				((ICol)col).set_Z(1, (object)table.Size);
				((ICol)col2).set_Z(1, (object)1);
				((ICol)col3).set_Z(1, (object)r.ToString().Replace(",", "."));
				((ICol)col4).set_Z(1, (object)"node");
				((ICol)col5).set_Z(1, (object)"r");
				((ICol)col6).set_Z(1, (object)node);
				((ICol)col7).set_Z(1, (object)1);
				((ICol)col8).set_Z(1, (object)1);
				((ICol)col9).set_Z(1, (object)0.06);
			}
		}

		public List<Point> GetPointsFromExitFile(string table, string col, string selection)
		{
			table table2 = (dynamic)_rastr.Tables.Item(table);
			table2.SetSel(selection);
			List<Point> list = new List<Point>();
			int num = ((ITable)table2).get_FindNextSel(-1);
			if (num < 0)
			{
				return list;
			}
			double[,] array = (dynamic)_rastr.GetChainedGraphSnapshot(table, col, num, 0);
			for (int i = 0; i < array.GetLength(0); i++)
			{
				list.Add(new Point(array[i, 1], array[i, 0]));
			}
			return list;
		}
	}
	public struct ShuntKZResult
	{
		public double r;

		public double x;

		public double u;
	}
	public struct DynamicResult
	{
		public string ResultMessage;

		public double TimeReached;

		public bool IsSuccess;

		public bool IsStable;

		public override string ToString()
		{
			return $"Результат: {ResultMessage}\r\nРассчитанное время: {TimeReached}\r\nУспешно: {IsSuccess} \r\nУстойчиво: {IsStable}";
		}
	}
	public class Point
	{
		public double X;

		public double Y;

		public Point(double x, double y)
		{
			X = x;
			Y = y;
		}
	}
}
namespace Xls_prjt
{
	public class ExcelOperations
	{
		private ExcelPackage _excel;

		private ExcelWorksheet _ws;

		public ExcelOperations(string file, dynamic list)
		{
			ExcelPackage.License.SetNonCommercialPersonal("igv");
			FileInfo newFile = new FileInfo(file);
			_excel = new ExcelPackage(newFile);
			_ws = _excel.Workbook.Worksheets[list];
		}

		public ExcelOperations(string list = "Результат")
		{
			ExcelPackage.License.SetNonCommercialPersonal("igv");
			_excel = new ExcelPackage();
			_ws = _excel.Workbook.Worksheets.Add(list);
			_ws.Cells["A1:XFD1048576"].Style.WrapText = true;
		}

		public int SheetCount(string file)
		{
			ExcelPackage.License.SetNonCommercialPersonal("igv");
			FileInfo newFile = new FileInfo(file);
			_excel = new ExcelPackage(newFile);
			return _excel.Workbook.Worksheets.Count;
		}

		public void AddList(string list)
		{
			_ws = _excel.Workbook.Worksheets.Add(list);
			_ws.Cells["A1:XFD1048576"].Style.WrapText = true;
		}

		public void setVal(int i, int j, dynamic val, bool wrap = true)
		{
			_ws.Cells[i, j].Value = (object)val;
			_ws.Cells[i, j].Style.WrapText = wrap;
		}

		public void Wrap(int i, int j, bool wrap = true)
		{
			_ws.Cells[i, j].Style.WrapText = wrap;
		}

		public void setVal(string param, dynamic val)
		{
			_ws.Cells[param].Value = (object)val;
		}

		public string getStr(int i, int j)
		{
			return (_ws.Cells[i, j].Value != null) ? _ws.Cells[i, j].Value.ToString() : "";
		}

		public string getStr(string param)
		{
			return (_ws.Cells[param].Value != null) ? _ws.Cells[param].Value.ToString() : "";
		}

		public int getInt(int i, int j)
		{
			return (_ws.Cells[i, j].Value != null) ? Convert.ToInt32(_ws.Cells[i, j].Value) : 0;
		}

		public int getInt(string param)
		{
			return (_ws.Cells[param].Value != null) ? Convert.ToInt32(_ws.Cells[param].Value) : 0;
		}

		public double getDbl(int i, int j)
		{
			return (_ws.Cells[i, j].Value != null) ? Convert.ToDouble(_ws.Cells[i, j].Value) : 0.0;
		}

		public double getDbl(string param)
		{
			return (_ws.Cells[param].Value != null) ? Convert.ToDouble(_ws.Cells[param].Value) : 0.0;
		}

		public void Save(string file = "")
		{
			if (file != "")
			{
				_excel.SaveAs(new FileInfo(file));
			}
			else
			{
				_excel.SaveAs(new FileInfo(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location) + "\\tmp.xlsx"));
			}
		}

		public void Borders(string param)
		{
			_ws.Cells[param].Style.Border.Top.Style = ExcelBorderStyle.Thin;
			_ws.Cells[param].Style.Border.Bottom.Style = ExcelBorderStyle.Thin;
			_ws.Cells[param].Style.Border.Left.Style = ExcelBorderStyle.Thin;
			_ws.Cells[param].Style.Border.Right.Style = ExcelBorderStyle.Thin;
		}

		public void Borders(int bRow, int bCol, int eRow, int eCol)
		{
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Border.Top.Style = ExcelBorderStyle.Thin;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Border.Bottom.Style = ExcelBorderStyle.Thin;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Border.Left.Style = ExcelBorderStyle.Thin;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Border.Right.Style = ExcelBorderStyle.Thin;
		}

		public void FormatCells(string param, bool bold, bool italic = false)
		{
			_ws.Cells[param].Style.Font.Bold = bold;
			_ws.Cells[param].Style.Font.Italic = italic;
		}

		public void FormatCells(int i, int j, bool bold, bool italic = false)
		{
			_ws.Cells[i, j].Style.Font.Bold = bold;
			_ws.Cells[i, j].Style.Font.Italic = italic;
		}

		public void FormatCells(int bRow, int bCol, int eRow, int eCol, bool bold, bool italic = false)
		{
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Font.Bold = bold;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Font.Italic = italic;
		}

		public void FormatCells(string param, bool bold, bool italic = false, int _color = -329006)
		{
			_ws.Cells[param].Style.Font.Bold = bold;
			_ws.Cells[param].Style.Font.Italic = italic;
			_ws.Cells[param].Style.Fill.PatternType = ExcelFillStyle.Solid;
			_ws.Cells[param].Style.Fill.BackgroundColor.SetColor(Color.FromArgb(_color));
		}

		public void FormatCells(int i, int j, bool bold, bool italic = false, int _color = -329006)
		{
			_ws.Cells[i, j].Style.Font.Bold = bold;
			_ws.Cells[i, j].Style.Font.Italic = italic;
			_ws.Cells[i, j].Style.Fill.PatternType = ExcelFillStyle.Solid;
			_ws.Cells[i, j].Style.Fill.BackgroundColor.SetColor(Color.FromArgb(_color));
		}

		public void FormatCells(int bRow, int bCol, int eRow, int eCol, bool bold, bool italic = false, int _color = -329006)
		{
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Font.Bold = bold;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Font.Italic = italic;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Fill.PatternType = ExcelFillStyle.Solid;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Fill.BackgroundColor.SetColor(Color.FromArgb(_color));
		}

		public void FormatCells(string param, int _color = -329006)
		{
			_ws.Cells[param].Style.Fill.PatternType = ExcelFillStyle.Solid;
			_ws.Cells[param].Style.Fill.BackgroundColor.SetColor(Color.FromArgb(_color));
		}

		public void FormatCells(int i, int j, int _color = -329006)
		{
			_ws.Cells[i, j].Style.Fill.PatternType = ExcelFillStyle.Solid;
			_ws.Cells[i, j].Style.Fill.BackgroundColor.SetColor(Color.FromArgb(_color));
		}

		public void FormatCells(int bRow, int bCol, int eRow, int eCol, int _color = -329006)
		{
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Fill.PatternType = ExcelFillStyle.Solid;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.Fill.BackgroundColor.SetColor(Color.FromArgb(_color));
		}

		public void Merge(string param)
		{
			_ws.Cells[param].Merge = true;
		}

		public void Merge(int bRow, int bCol, int eRow, int eCol, bool hor = false, bool vert = false)
		{
			_ws.Cells[bRow, bCol, eRow, eCol].Merge = true;
			if (hor)
			{
				_ws.Cells[bRow, bCol, eRow, eCol].Style.HorizontalAlignment = ExcelHorizontalAlignment.Center;
			}
			if (vert)
			{
				_ws.Cells[bRow, bCol, eRow, eCol].Style.VerticalAlignment = ExcelVerticalAlignment.Center;
			}
		}

		public void Format(int i, int j, ExcelHorizontalAlignment excelHorizontalAlignment, ExcelVerticalAlignment excelVerticalAlignment, int rotation = 0)
		{
			_ws.Cells[i, j].Style.HorizontalAlignment = excelHorizontalAlignment;
			_ws.Cells[i, j].Style.VerticalAlignment = excelVerticalAlignment;
			_ws.Cells[i, j].Style.TextRotation = rotation;
		}

		public void Format(int bRow, int bCol, int eRow, int eCol, ExcelHorizontalAlignment excelHorizontalAlignment, ExcelVerticalAlignment excelVerticalAlignment, int rotation = 0)
		{
			_ws.Cells[bRow, bCol, eRow, eCol].Style.HorizontalAlignment = excelHorizontalAlignment;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.VerticalAlignment = excelVerticalAlignment;
			_ws.Cells[bRow, bCol, eRow, eCol].Style.TextRotation = rotation;
		}

		public void Font(string name = "Times New Roman", int size = 10)
		{
			_ws.Cells["A1:XFD1048576"].Style.Font.Name = name;
			_ws.Cells["A1:XFD1048576"].Style.Font.Size = size;
		}

		public void FontColor(int i, int j, Color color)
		{
			_ws.Cells[i, j].Style.Font.Color.SetColor(color);
		}

		public bool IsValue(string param)
		{
			return _ws.Cells[param].Value != null;
		}

		public bool IsValue(int i, int j)
		{
			return _ws.Cells[i, j].Value != null;
		}

		public void Width(int col, int width, bool auto = false)
		{
			_ws.Column(col).Width = width;
			if (auto)
			{
				_ws.Column(col).AutoFit();
			}
		}

		public void HideColumn(int col)
		{
			_ws.Column(col).Hidden = true;
		}

		public void Height(int row, int height)
		{
			_ws.Row(row).Height = height;
		}

		public int ValToColor(dynamic value)
		{
			int result = Color.YellowGreen.ToArgb();
			if (value >= 30 && value < 40)
			{
				result = Color.YellowGreen.ToArgb();
			}
			else if (value >= 40 && value < 50)
			{
				result = Color.LightGreen.ToArgb();
			}
			else if (value >= 50 && value < 60)
			{
				result = Color.GreenYellow.ToArgb();
			}
			else if (value >= 60 && value < 70)
			{
				result = Color.Yellow.ToArgb();
			}
			else if (value >= 70 && value < 80)
			{
				result = Color.Orange.ToArgb();
			}
			else if (value >= 80 && value < 90)
			{
				result = Color.SandyBrown.ToArgb();
			}
			else if (value >= 90 && value < 100)
			{
				result = Color.Tomato.ToArgb();
			}
			else if (value >= 100)
			{
				result = Color.OrangeRed.ToArgb();
			}
			else if (value < 30)
			{
				result = Color.White.ToArgb();
			}
			return result;
		}

		public int ValToColorVoltage(dynamic value)
		{
			int result = Color.YellowGreen.ToArgb();
			if (value >= 10 && value <= 15)
			{
				result = Color.GreenYellow.ToArgb();
			}
			else if (value >= 8 && value < 10)
			{
				result = Color.Yellow.ToArgb();
			}
			else if (value >= 6 && value < 8)
			{
				result = Color.Orange.ToArgb();
			}
			else if (value >= 4 && value < 6)
			{
				result = Color.SandyBrown.ToArgb();
			}
			else if (value >= 2.5 && value < 4)
			{
				result = Color.Tomato.ToArgb();
			}
			else if (value <= 2.5)
			{
				result = Color.OrangeRed.ToArgb();
			}
			else if (value > 15)
			{
				result = Color.White.ToArgb();
			}
			return result;
		}

		public int VoltageToColor(dynamic value)
		{
			int result = Color.YellowGreen.ToArgb();
			if (value >= 16)
			{
				result = Color.OrangeRed.ToArgb();
			}
			else if (value >= 14 && value < 16)
			{
				result = Color.Tomato.ToArgb();
			}
			else if (value >= 12 && value < 14)
			{
				result = Color.SandyBrown.ToArgb();
			}
			else if (value >= 10 && value < 12)
			{
				result = Color.Orange.ToArgb();
			}
			else if (value >= 7.5 && value < 10)
			{
				result = Color.Yellow.ToArgb();
			}
			else if (value >= 5 && value < 7.5)
			{
				result = Color.GreenYellow.ToArgb();
			}
			else if (value <= 5)
			{
				result = Color.White.ToArgb();
			}
			return result;
		}
	}
}
namespace DynStabSpace
{
	public class DynStabilityCalc
	{
		private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Пакетный расчет ДУ";

		private BackgroundWorker _w;

		private ObservableCollection<RgmsInfo> RgmsInfo;

		private ObservableCollection<ScnsInfo> ScnsInfo;

		private List<VrnInfo> VrnInf;

		private FileInfo Rems;

		private FileInfo Sechen;

		private FileInfo LAPNU;

		private List<KprInfo> _KprInf;

		private bool SaveGRF;

		private string lpns;

		private bool DynNoPA;

		private bool DynWithPA;

		public bool UseLPN;

		private List<KprInfo> KprInf
		{
			get
			{
				return _KprInf;
			}
			set
			{
				grf = new List<int>();
				foreach (KprInfo item in value)
				{
					if (!grf.Contains(item.Num))
					{
						grf.Add(item.Num);
					}
				}
				grf.OrderBy((int k) => k);
				_KprInf = value;
			}
		}

		private List<int> grf { get; set; }

		public string root => tmp_root;

		public int Max
		{
			get
			{
				int num = (DynNoPA ? 1 : 0) + (DynWithPA ? 1 : 0);
				return RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() * num + 1;
			}
		}

		public DynStabilityCalc(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, List<KprInfo> kprs, FileInfo sechen, FileInfo lapnu, bool save = false, string lpns = "", bool no_pa = true, bool with_pa = false, bool lpn = false)
		{
			if (rgms.Count() == 0 || scns.Count() == 0 || (lpn && sechen.Name == null) || (save && kprs.Count() == 0) || (with_pa && lapnu.Name == null))
			{
				throw new InitialDataException("Не заданы все исходные данные для выполнения пакетного расчета динамической устойчивости!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}" + ((lpn && sechen.Name == null) ? (Environment.NewLine + "Используется файл ПА в формате lpn, но не загружен файл сечений!") : "") + ((lapnu.Name == null && with_pa) ? (Environment.NewLine + "Включен расчет МДП с учетом ПА, но файл ПА отсутствует!") : "") + ((save && kprs.Count() == 0) ? (Environment.NewLine + "Включена опция сохранения графиков, но отсутствует файл графического вывода!") : ""));
			}
			RgmsInfo = rgms;
			ScnsInfo = scns;
			VrnInf = vrns;
			Rems = rems;
			Sechen = sechen;
			LAPNU = lapnu;
			KprInf = kprs;
			SaveGRF = save;
			this.lpns = lpns;
			DynNoPA = no_pa;
			DynWithPA = with_pa;
			UseLPN = lpn;
			_w = sender as BackgroundWorker;
			Directory.CreateDirectory(tmp_root);
		}

		public List<DynResults> Calc()
		{
			int num = 0;
			List<DynResults> list = new List<DynResults>();
			foreach (RgmsInfo item in RgmsInfo)
			{
				List<DynShems> list2 = new List<DynShems>();
				int num2 = RgmsInfo.IndexOf(item) + 1;
				foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
				{
					DynShems dynShems = new DynShems();
					List<Events> list3 = new List<Events>();
					dynShems.ShemeName = item2.Name;
					foreach (ScnsInfo item3 in ScnsInfo)
					{
						int num3 = ScnsInfo.IndexOf(item3) + 1;
						RastrOperations rastrOperations = new RastrOperations();
						rastrOperations.Load(item.Name);
						rastrOperations.DynSettings();
						dynShems.IsStable = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
						if (!dynShems.IsStable)
						{
							break;
						}
						DynamicResult noPaResult = default(DynamicResult);
						DynamicResult withPaResult = default(DynamicResult);
						List<string> list4 = new List<string>();
						List<string> list5 = new List<string>();
						if (DynNoPA)
						{
							rastrOperations.Load(item3.Name);
							rastrOperations.LoadTemplate(".dfw");
							if (SaveGRF)
							{
								noPaResult = rastrOperations.RunDynamic();
								foreach (int _id in grf)
								{
									string text = tmp_root + $"\\Рисунок - {num2}.{item2.Num + 1}.{num3}.{_id}(без ПА).png";
									GetPictures(rastrOperations, KprInf.Where((KprInfo k) => k.Num == _id).ToList(), text);
									list4.Add(text);
								}
							}
							else
							{
								noPaResult = rastrOperations.RunDynamic(_ems: true);
							}
							num++;
							_w.ReportProgress(num);
						}
						if (DynWithPA)
						{
							if (UseLPN)
							{
								rastrOperations.Load(Sechen.Name);
								rastrOperations.CreateScnFromLpn(LAPNU.Name, lpns, item3.Name);
							}
							else
							{
								rastrOperations.Load(item3.Name);
								rastrOperations.Load(LAPNU.Name);
							}
							if (SaveGRF)
							{
								withPaResult = rastrOperations.RunDynamic();
								foreach (int _id2 in grf)
								{
									string text2 = tmp_root + $"\\Рисунок - {num2}.{item2.Num + 1}.{num3}.{_id2}(с ПА).png";
									GetPictures(rastrOperations, KprInf.Where((KprInfo k) => k.Num == _id2).ToList(), text2);
									list5.Add(text2);
								}
							}
							else
							{
								withPaResult = rastrOperations.RunDynamic(_ems: true);
							}
							num++;
							_w.ReportProgress(num);
						}
						list3.Add(new Events
						{
							Name = item3.name,
							NoPaResult = noPaResult,
							WithPaResult = withPaResult,
							NoPaPic = list4,
							WithPaPic = list5
						});
					}
					dynShems.Events = list3;
					list2.Add(dynShems);
				}
				list.Add(new DynResults
				{
					RgName = item.name,
					DynShems = list2
				});
			}
			return list;
		}

		private void GetPictures(RastrOperations _rst, List<KprInfo> _pictures, string _file)
		{
			PlotModel grf = new PlotModel();
			grf.Legends.Add(new Legend
			{
				LegendPosition = LegendPosition.RightBottom,
				LegendPlacement = LegendPlacement.Inside,
				LegendBackground = OxyColors.White,
				LegendBorder = OxyColors.Black
			});
			grf.Axes.Add(new LinearAxis
			{
				Position = AxisPosition.Bottom,
				MajorGridlineStyle = LineStyle.Solid,
				AbsoluteMinimum = 0.0,
				Title = "Время, с",
				AxisTitleDistance = 10.0,
				TitleFontSize = 18.0
			});
			grf.Axes.Add(new LinearAxis
			{
				Position = AxisPosition.Left,
				MajorGridlineStyle = LineStyle.Solid
			});
			PngExporter exp = new PngExporter
			{
				Width = 1200,
				Height = 800
			};
			foreach (KprInfo _picture in _pictures)
			{
				LineSeries lineSeries = new LineSeries
				{
					StrokeThickness = 2.0,
					Title = _picture.Name,
					FontSize = 16.0
				};
				foreach (rst_operations.Point item in _rst.GetPointsFromExitFile(_picture.Table, _picture.Col, _picture.Selection))
				{
					lineSeries.Points.Add(new DataPoint(item.X, item.Y));
				}
				grf.Series.Add(lineSeries);
			}
			((DispatcherObject)Application.Current).Dispatcher.Invoke((Action)delegate
			{
				MemoryStream memoryStream = new MemoryStream();
				exp.Export(grf, memoryStream);
				Image.FromStream((Stream)memoryStream).Save(_file, ImageFormat.Png);
			});
		}
	}
	public class Max_KZ_Time
	{
		private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Предельное время КЗ";

		private BackgroundWorker _w;

		private ObservableCollection<RgmsInfo> RgmsInfo;

		private ObservableCollection<ScnsInfo> ScnsInfo;

		private List<VrnInfo> VrnInf;

		private FileInfo Rems;

		private double CrtTimePrecision;

		private double CrtTimeMax;

		public string root => tmp_root;

		public int Max => RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() + 1;

		public Max_KZ_Time(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, double time_precision, double max_time)
		{
			if (rgms.Count() == 0 || scns.Count() == 0 || max_time == 0.0)
			{
				throw new InitialDataException("Не заданы все исходные данные для определения предельного времени отключения КЗ!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}{Environment.NewLine}" + $"Максимальное время отключения КЗ составляет - {max_time}");
			}
			RgmsInfo = rgms;
			ScnsInfo = scns;
			VrnInf = vrns;
			Rems = rems;
			CrtTimePrecision = time_precision;
			CrtTimeMax = max_time;
			_w = sender as BackgroundWorker;
			Directory.CreateDirectory(tmp_root);
		}

		public List<CrtTimeResults> Calc()
		{
			int num = 0;
			List<CrtTimeResults> list = new List<CrtTimeResults>();
			foreach (RgmsInfo item in RgmsInfo)
			{
				List<CrtShems> list2 = new List<CrtShems>();
				foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
				{
					List<CrtTimes> list3 = new List<CrtTimes>();
					CrtShems crtShems = new CrtShems();
					crtShems.ShemeName = item2.Name;
					foreach (ScnsInfo item3 in ScnsInfo)
					{
						RastrOperations rastrOperations = new RastrOperations();
						rastrOperations.Load(item.Name);
						rastrOperations.Load(item3.Name);
						crtShems.IsStable = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
						if (crtShems.IsStable)
						{
							list3.Add(new CrtTimes
							{
								ScnName = item3.name,
								CrtTime = rastrOperations.FindCrtTime(CrtTimePrecision, CrtTimeMax)
							});
							num++;
							_w.ReportProgress(num);
						}
					}
					crtShems.Times = list3;
					list2.Add(crtShems);
				}
				list.Add(new CrtTimeResults
				{
					RgName = item.name,
					CrtShems = list2
				});
			}
			return list;
		}
	}
	public class MdpStabilityCalc
	{
		private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} МДП ДУ";

		private BackgroundWorker _w;

		private ObservableCollection<RgmsInfo> RgmsInfo;

		private ObservableCollection<ScnsInfo> ScnsInfo;

		private List<VrnInfo> VrnInf;

		private FileInfo Rems;

		private FileInfo VIR;

		private FileInfo Sechen;

		private FileInfo LAPNU;

		private List<SchInfo> SchInf;

		private List<KprInfo> KprInf;

		private string lpns;

		private int SelectedSch;

		private bool DynNoPA;

		private bool DynWithPA;

		public bool UseLPN;

		public string root => tmp_root;

		public int Max
		{
			get
			{
				int num = (DynNoPA ? 1 : 0) + (DynWithPA ? 1 : 0);
				return RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() * num + 1;
			}
		}

		public MdpStabilityCalc(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, FileInfo vir, FileInfo sechen, FileInfo lapnu, List<SchInfo> schs, List<KprInfo> kprs, string lpns = "", int selected_sch = 0, bool no_pa = true, bool with_pa = false, bool lpn = false)
		{
			if (rgms.Count() == 0 || scns.Count() == 0 || vir.Name == null || sechen.Name == null || (lapnu.Name == null && with_pa) || (lpn && sechen.Name == null))
			{
				throw new InitialDataException("Не заданы все исходные данные для определения допустимых перетоков мощности по критерию обеспечения динамической устойчивости генерирующего оборудования!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}" + ((vir.Name == null) ? (Environment.NewLine + "Отсутствует траектория утяжеления!") : "") + ((sechen.Name == null) ? (Environment.NewLine + "Отсутствует файл контролируемых сечений!") : "") + ((lapnu.Name == null && with_pa) ? (Environment.NewLine + "Включен расчет МДП с учетом ПА, но файл ПА отсутствует!") : "") + ((lpn && sechen.Name == null) ? (Environment.NewLine + "Используется файл ПА в формате lpn, но не загружен файл сечений!") : ""));
			}
			RgmsInfo = rgms;
			ScnsInfo = scns;
			VrnInf = vrns;
			Rems = rems;
			VIR = vir;
			Sechen = sechen;
			LAPNU = lapnu;
			SchInf = schs;
			KprInf = kprs;
			this.lpns = lpns;
			SelectedSch = selected_sch;
			DynNoPA = no_pa;
			DynWithPA = with_pa;
			UseLPN = lpn;
			_w = sender as BackgroundWorker;
			Directory.CreateDirectory(tmp_root);
		}

		public List<MdpResults> Calc()
		{
			int num = 0;
			List<MdpResults> list = new List<MdpResults>();
			string text = tmp_root + "\\\\mdp_calc_tmp.rst";
			foreach (RgmsInfo item in RgmsInfo)
			{
				List<MdpShems> list2 = new List<MdpShems>();
				foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
				{
					MdpShems mdpShems = new MdpShems();
					List<MdpEvents> list3 = new List<MdpEvents>();
					mdpShems.ShemeName = item2.Name;
					foreach (ScnsInfo item3 in ScnsInfo)
					{
						RastrOperations rastrOperations = new RastrOperations();
						if (!mdpShems.IsReady)
						{
							rastrOperations.Load(item.Name);
							rastrOperations.DynSettings();
							mdpShems.IsStable = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
							rastrOperations.Save(text);
							mdpShems.IsReady = true;
							if (mdpShems.IsStable)
							{
								rastrOperations.Load(Sechen.Name);
								rastrOperations.Load(VIR.Name);
								mdpShems.Pstart = rastrOperations.getVal("sechen", "psech", SelectedSch);
								mdpShems.MaxStep = rastrOperations.Run_Ut();
								mdpShems.Ppred = rastrOperations.getVal("sechen", "psech", SelectedSch);
								rastrOperations.Load(text);
								rastrOperations.Load(VIR.Name);
								mdpShems.MaxStep = rastrOperations.Step(mdpShems.MaxStep * 0.9);
								double num2 = rastrOperations.getVal("sechen", "psech", SelectedSch);
								while (Math.Abs(num2 - mdpShems.Ppred * 0.9) > 2.0)
								{
									rastrOperations.Load(text);
									rastrOperations.Load(VIR.Name);
									mdpShems.MaxStep = rastrOperations.Step(mdpShems.MaxStep * mdpShems.Ppred * 0.9 / num2);
									num2 = rastrOperations.getVal("sechen", "psech", SelectedSch);
								}
								rastrOperations.Save(text);
							}
						}
						if (!mdpShems.IsStable)
						{
							break;
						}
						List<Values> list4 = new List<Values>();
						List<Values> list5 = new List<Values>();
						List<Values> list6 = new List<Values>();
						List<Values> list7 = new List<Values>();
						double noPaMdp = -1.0;
						double withPaMdp = -1.0;
						double num3 = Math.Max(2.0, Math.Min(10.0, Math.Floor(mdpShems.Ppred * 0.02)));
						if (DynNoPA)
						{
							rastrOperations.Load(text);
							rastrOperations.Load(Sechen.Name);
							rastrOperations.Load(VIR.Name);
							rastrOperations.Load(item3.Name);
							rastrOperations.LoadTemplate(".dfw");
							DynamicResult dynamicResult = rastrOperations.RunDynamic(_ems: true);
							if (dynamicResult.IsSuccess && !dynamicResult.IsStable)
							{
								double num4 = rastrOperations.getVal("sechen", "psech", SelectedSch);
								double num5 = mdpShems.Pstart;
								double num6 = 0.0;
								double num7 = 0.0 - mdpShems.MaxStep;
								double step = num6 + (num7 - num6) * 0.5;
								while (dynamicResult.IsSuccess && (Math.Abs(num4 - num5) > num3 || !dynamicResult.IsStable))
								{
									rastrOperations.Load(text);
									rastrOperations.Load(VIR.Name);
									double num8 = rastrOperations.Step(step);
									dynamicResult = rastrOperations.RunDynamic(_ems: true);
									if (dynamicResult.IsSuccess && dynamicResult.IsStable)
									{
										num7 = num8;
										num5 = rastrOperations.getVal("sechen", "psech", SelectedSch);
									}
									else
									{
										num6 = num8;
										num4 = rastrOperations.getVal("sechen", "psech", SelectedSch);
										if (num6 <= num7 || Math.Floor(num4) <= Math.Floor(num5) + 2.0)
										{
											num7 -= 2.0;
										}
									}
									step = num6 + (num7 - num6) * 0.5;
								}
								noPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
							}
							else if (dynamicResult.IsSuccess && dynamicResult.IsStable)
							{
								noPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
							}
							foreach (SchInfo item4 in SchInf.Where((SchInfo k) => k.Control))
							{
								list4.Add(new Values
								{
									Id = item4.Id,
									Name = item4.Name,
									Value = rastrOperations.getVal("sechen", "psech", item4.Id)
								});
							}
							foreach (KprInfo item5 in KprInf)
							{
								list5.Add(new Values
								{
									Id = item5.Id,
									Name = item5.Name,
									Value = rastrOperations.getVal(item5.Table, item5.Col, item5.Selection)
								});
							}
							num++;
							_w.ReportProgress(num);
						}
						if (DynWithPA)
						{
							rastrOperations.Load(text);
							rastrOperations.Load(Sechen.Name);
							rastrOperations.Load(VIR.Name);
							if (UseLPN)
							{
								rastrOperations.Load(Sechen.Name);
								rastrOperations.CreateScnFromLpn(LAPNU.Name, lpns, item3.Name);
							}
							else
							{
								rastrOperations.Load(item3.Name);
								rastrOperations.Load(LAPNU.Name);
							}
							DynamicResult dynamicResult2 = rastrOperations.RunDynamic(_ems: true);
							if (dynamicResult2.IsSuccess && !dynamicResult2.IsStable)
							{
								double num9 = rastrOperations.getVal("sechen", "psech", SelectedSch);
								double num10 = mdpShems.Pstart;
								double num11 = 0.0;
								double num12 = 0.0 - mdpShems.MaxStep;
								double step2 = num11 + (num12 - num11) * 0.5;
								while (dynamicResult2.IsSuccess && (Math.Abs(num9 - num10) > num3 || !dynamicResult2.IsStable))
								{
									rastrOperations.Load(text);
									rastrOperations.Load(VIR.Name);
									double num13 = rastrOperations.Step(step2);
									if (UseLPN)
									{
										rastrOperations.Load(Sechen.Name);
										rastrOperations.CreateScnFromLpn(LAPNU.Name, lpns, item3.Name);
									}
									else
									{
										rastrOperations.Load(item3.Name);
										rastrOperations.Load(LAPNU.Name);
									}
									dynamicResult2 = rastrOperations.RunDynamic(_ems: true);
									if (dynamicResult2.IsSuccess && dynamicResult2.IsStable)
									{
										num12 = num13;
										num10 = rastrOperations.getVal("sechen", "psech", SelectedSch);
									}
									else
									{
										num11 = num13;
										num9 = rastrOperations.getVal("sechen", "psech", SelectedSch);
										if (num11 <= num12 || Math.Floor(num9) <= Math.Floor(num10) + 2.0)
										{
											num12 -= 2.0;
										}
									}
									step2 = num11 + (num12 - num11) * 0.5;
								}
								withPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
							}
							else if (dynamicResult2.IsSuccess && dynamicResult2.IsStable)
							{
								withPaMdp = rastrOperations.getVal("sechen", "psech", SelectedSch);
							}
							foreach (SchInfo item6 in SchInf.Where((SchInfo k) => k.Control))
							{
								list6.Add(new Values
								{
									Id = item6.Id,
									Name = item6.Name,
									Value = rastrOperations.getVal("sechen", "psech", item6.Id)
								});
							}
							foreach (KprInfo item7 in KprInf)
							{
								list7.Add(new Values
								{
									Id = item7.Id,
									Name = item7.Name,
									Value = rastrOperations.getVal(item7.Table, item7.Col, item7.Selection)
								});
							}
							num++;
							_w.ReportProgress(num);
						}
						list3.Add(new MdpEvents
						{
							Name = item3.name,
							NoPaSechen = list4,
							NoPaKpr = list5,
							WithPaSechen = list6,
							WithPaKpr = list7,
							NoPaMdp = noPaMdp,
							WithPaMdp = withPaMdp
						});
					}
					mdpShems.Events = list3;
					list2.Add(mdpShems);
				}
				list.Add(new MdpResults
				{
					RgName = item.name,
					MdpShems = list2
				});
			}
			File.Delete(text);
			return list;
		}
	}
	public class SchInfo
	{
		public int Id;

		public int Num;

		public string Name;

		public bool Control;
	}
	public class VrnInfo
	{
		public int Id;

		public string Name;

		public bool Deactive;

		public int Num;
	}
	public class KprInfo
	{
		public int Id;

		public int Num;

		public string Name;

		public string Table;

		public string Selection;

		public string Col;
	}
	public class RelayCommand : ICommand
	{
		private Action<object> execute;

		private Func<object, bool> canExecute;

		public event EventHandler CanExecuteChanged
		{
			add
			{
				CommandManager.RequerySuggested += value;
			}
			remove
			{
				CommandManager.RequerySuggested -= value;
			}
		}

		public RelayCommand(Action<object> execute, Func<object, bool> canExecute = null)
		{
			this.execute = execute;
			this.canExecute = canExecute;
		}

		public bool CanExecute(object parameter)
		{
			return canExecute == null || canExecute(parameter);
		}

		public void Execute(object parameter)
		{
			execute(parameter);
		}
	}
	public class RgmsInfo : INotifyPropertyChanged
	{
		private string _name;

		public string Name
		{
			get
			{
				return _name;
			}
			set
			{
				_name = value;
				OnPropertyChanged("Name");
				OnPropertyChanged("name");
			}
		}

		public string name => Path.GetFileNameWithoutExtension(_name);

		public event PropertyChangedEventHandler PropertyChanged;

		public void OnPropertyChanged([CallerMemberName] string prop = "")
		{
			if (this.PropertyChanged != null)
			{
				this.PropertyChanged(this, new PropertyChangedEventArgs(prop));
			}
		}
	}
	public class ScnsInfo : INotifyPropertyChanged
	{
		private string _name;

		public string Name
		{
			get
			{
				return _name;
			}
			set
			{
				_name = value;
				OnPropertyChanged("Name");
				OnPropertyChanged("name");
			}
		}

		public string name => Path.GetFileNameWithoutExtension(_name);

		public event PropertyChangedEventHandler PropertyChanged;

		public void OnPropertyChanged([CallerMemberName] string prop = "")
		{
			if (this.PropertyChanged != null)
			{
				this.PropertyChanged(this, new PropertyChangedEventArgs(prop));
			}
		}
	}
	public class FileInfo : INotifyPropertyChanged
	{
		private string _name;

		public string Name
		{
			get
			{
				return _name;
			}
			set
			{
				_name = value;
				OnPropertyChanged("Name");
				OnPropertyChanged("name");
			}
		}

		public string name => Path.GetFileName(_name);

		public event PropertyChangedEventHandler PropertyChanged;

		public void OnPropertyChanged([CallerMemberName] string prop = "")
		{
			if (this.PropertyChanged != null)
			{
				this.PropertyChanged(this, new PropertyChangedEventArgs(prop));
			}
		}
	}
	public class ShuntKZ
	{
		public int Node;

		public double r1;

		public double x1;

		public double u1;

		public double r2;

		public double x2;

		public double u2;
	}
	public class ShuntResults
	{
		public string RgName;

		public List<Shems> Shems;
	}
	public class Shems
	{
		public string ShemeName;

		public bool IsStable;

		public List<ShuntKZ> Nodes;
	}
	public class CrtTimeResults
	{
		public string RgName;

		public List<CrtShems> CrtShems;
	}
	public class CrtShems
	{
		public string ShemeName;

		public bool IsStable;

		public List<CrtTimes> Times;
	}
	public class CrtTimes
	{
		public string ScnName;

		public double CrtTime;
	}
	public class DynResults
	{
		public string RgName;

		public List<DynShems> DynShems;
	}
	public class DynShems
	{
		public string ShemeName;

		public bool IsStable;

		public List<Events> Events;
	}
	public class Events
	{
		public string Name;

		public DynamicResult NoPaResult;

		public DynamicResult WithPaResult;

		public List<string> NoPaPic;

		public List<string> WithPaPic;
	}
	public class MdpResults
	{
		public string RgName;

		public List<MdpShems> MdpShems;
	}
	public class MdpShems
	{
		public string ShemeName;

		public bool IsReady;

		public bool IsStable;

		public double MaxStep;

		public double Ppred;

		public double Pstart;

		public List<MdpEvents> Events;
	}
	public class MdpEvents
	{
		public string Name;

		public List<Values> NoPaSechen;

		public List<Values> NoPaKpr;

		public double NoPaMdp;

		public List<Values> WithPaSechen;

		public List<Values> WithPaKpr;

		public double WithPaMdp;
	}
	public class Values
	{
		public int Id;

		public string Name;

		public double Value;
	}
	public class UostResults
	{
		public string RgName;

		public List<UostShems> UostShems;
	}
	public class UostShems
	{
		public string ShemeName;

		public bool IsStable;

		public List<UostEvents> Events;
	}
	public class UostEvents
	{
		public string Name;

		public int BeginNode;

		public int EndNode;

		public int Np;

		public double Distance;

		public double BeginUost;

		public double EndUost;

		public List<Values> Values;
	}
	public class Settings : Window, IComponentConnector
	{
		private bool _contentLoaded;

		public Settings()
		{
			InitializeComponent();
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/DynStabSpace;component/settings.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			_contentLoaded = true;
		}
	}
	public class Shunt_KZ
	{
		private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Шунты КЗ";

		private double BaseAngle = 1.471;

		private BackgroundWorker _w;

		private ObservableCollection<RgmsInfo> RgmsInfo;

		private List<VrnInfo> VrnInf;

		private FileInfo Rems;

		private List<ShuntKZ> ShuntKZInf;

		private bool UseSelNodes;

		private bool UseTypeValU;

		private bool CalcOnePhase;

		private bool CalcTwoPhase;

		public string root => tmp_root;

		public int Max
		{
			get
			{
				int num = 0;
				int num2 = (CalcOnePhase ? 1 : 0) + (CalcTwoPhase ? 1 : 0);
				if (!UseSelNodes)
				{
					num = RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ShuntKZInf.Count() * num2;
				}
				else
				{
					RastrOperations rastrOperations = new RastrOperations();
					foreach (RgmsInfo item in RgmsInfo)
					{
						rastrOperations.Load(item.Name);
						num += rastrOperations.Selection("node", "sel = 1").Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * num2;
					}
				}
				return num + 1;
			}
		}

		public Shunt_KZ(object sender, ObservableCollection<RgmsInfo> rgms, List<VrnInfo> vrns, FileInfo rems, List<ShuntKZ> ShuntKZInf, bool sel, bool type, bool one, bool two)
		{
			if (rgms.Count == 0 || (ShuntKZInf.Count() == 0 && !sel) || !(one || two))
			{
				throw new InitialDataException("Не заданы все исходные данные для определения шунтов КЗ!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}" + ((ShuntKZInf.Count() == 0 && !sel) ? (Environment.NewLine + "Отсутствуют узлы в файле задания или отключен чекбокс Использовать отмеченные узлы!") : "") + ((!(one || two)) ? (Environment.NewLine + "Отключены чекбосы расчетов однофазного и двухфазного КЗ!") : ""));
			}
			RgmsInfo = rgms;
			VrnInf = vrns;
			Rems = rems;
			this.ShuntKZInf = ShuntKZInf;
			UseSelNodes = sel;
			UseTypeValU = type;
			CalcOnePhase = one;
			CalcTwoPhase = two;
			_w = sender as BackgroundWorker;
			Directory.CreateDirectory(tmp_root);
		}

		public List<ShuntResults> Calc()
		{
			int num = 0;
			List<ShuntResults> list = new List<ShuntResults>();
			foreach (RgmsInfo item in RgmsInfo)
			{
				List<Shems> list2 = new List<Shems>();
				foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
				{
					List<ShuntKZ> list3 = new List<ShuntKZ>();
					RastrOperations rastrOperations = new RastrOperations();
					rastrOperations.Load(item.Name);
					bool flag = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
					if (flag)
					{
						if (!UseSelNodes)
						{
							foreach (ShuntKZ item3 in ShuntKZInf)
							{
								ShuntKZResult shuntKZResult = default(ShuntKZResult);
								ShuntKZ shuntKZ = new ShuntKZ();
								shuntKZ.Node = item3.Node;
								rastrOperations.rgm();
								double num2 = rastrOperations.getVal("node", "vras", $"ny={item3.Node}");
								if (item3.x1 != -1.0 && (item3.u1 != -1.0 || UseTypeValU) && CalcOnePhase)
								{
									shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u1 != -1.0) ? item3.u1 : (num2 * 0.66), item3.x1, item3.r1);
									shuntKZ.r1 = shuntKZResult.r;
									shuntKZ.x1 = shuntKZResult.x;
									shuntKZ.u1 = shuntKZResult.u;
								}
								else if (item3.x1 == -1.0 && (item3.u1 != -1.0 || UseTypeValU) && CalcOnePhase)
								{
									shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u1 != -1.0) ? item3.u1 : (num2 * 0.66), Math.Sin(BaseAngle), Math.Cos(BaseAngle));
									shuntKZ.r1 = shuntKZResult.r;
									shuntKZ.x1 = shuntKZResult.x;
									shuntKZ.u1 = shuntKZResult.u;
								}
								if (CalcOnePhase)
								{
									num++;
									_w.ReportProgress(num);
								}
								if (item3.x2 != -1.0 && (item3.u2 != -1.0 || UseTypeValU) && CalcTwoPhase)
								{
									shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u2 != -1.0) ? item3.u2 : (num2 * 0.33), item3.x2, item3.r2);
									shuntKZ.r2 = shuntKZResult.r;
									shuntKZ.x2 = shuntKZResult.x;
									shuntKZ.u2 = shuntKZResult.u;
								}
								else if (item3.x2 == -1.0 && (item3.u2 != -1.0 || UseTypeValU) && CalcTwoPhase)
								{
									shuntKZResult = rastrOperations.FindShuntKZ(item3.Node, (item3.u2 != -1.0) ? item3.u2 : (num2 * 0.33), Math.Sin(BaseAngle), Math.Cos(BaseAngle));
									shuntKZ.r2 = shuntKZResult.r;
									shuntKZ.x2 = shuntKZResult.x;
									shuntKZ.u2 = shuntKZResult.u;
								}
								if (CalcTwoPhase)
								{
									num++;
									_w.ReportProgress(num);
								}
								list3.Add(shuntKZ);
							}
						}
						else
						{
							foreach (int item4 in rastrOperations.Selection("node", "sel = 1"))
							{
								ShuntKZResult shuntKZResult2 = default(ShuntKZResult);
								ShuntKZ shuntKZ2 = new ShuntKZ();
								rastrOperations.rgm();
								double num3 = rastrOperations.getVal("node", "vras", item4);
								int node = (shuntKZ2.Node = rastrOperations.getVal("node", "ny", item4));
								shuntKZResult2 = rastrOperations.FindShuntKZ(node, num3 * 0.66, Math.Sin(BaseAngle), Math.Cos(BaseAngle));
								shuntKZ2.r1 = shuntKZResult2.r;
								shuntKZ2.x1 = shuntKZResult2.x;
								shuntKZ2.u1 = shuntKZResult2.u;
								if (CalcOnePhase)
								{
									num++;
									_w.ReportProgress(num);
								}
								shuntKZResult2 = rastrOperations.FindShuntKZ(node, num3 * 0.33, Math.Sin(BaseAngle), Math.Cos(BaseAngle));
								shuntKZ2.r2 = shuntKZResult2.r;
								shuntKZ2.x2 = shuntKZResult2.x;
								shuntKZ2.u2 = shuntKZResult2.u;
								if (CalcTwoPhase)
								{
									num++;
									_w.ReportProgress(num);
								}
								list3.Add(shuntKZ2);
							}
						}
					}
					list2.Add(new Shems
					{
						ShemeName = item2.Name,
						IsStable = flag,
						Nodes = list3
					});
				}
				list.Add(new ShuntResults
				{
					RgName = item.name,
					Shems = list2
				});
			}
			return list;
		}
	}
	public class UostStabilityCalc
	{
		private string tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + $"\\DynStabSpace\\{DateTime.Now:yyyy-MM-dd HH-mm-ss} Uост на границе устойчивости";

		private BackgroundWorker _w;

		private ObservableCollection<RgmsInfo> RgmsInfo;

		private ObservableCollection<ScnsInfo> ScnsInfo;

		private List<VrnInfo> VrnInf;

		private FileInfo Rems;

		private List<KprInfo> KprInf;

		public string root => tmp_root;

		public int Max => RgmsInfo.Count() * VrnInf.Where((VrnInfo k) => !k.Deactive).Count() * ScnsInfo.Count() + 1;

		public UostStabilityCalc(object sender, ObservableCollection<RgmsInfo> rgms, ObservableCollection<ScnsInfo> scns, List<VrnInfo> vrns, FileInfo rems, List<KprInfo> kprs)
		{
			if (rgms.Count() == 0 || scns.Count() == 0)
			{
				throw new InitialDataException("Не заданы все исходные данные для определения остаточного напряжения на шинах энергообъекта при КЗ на границе устойчивости!" + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + $"Загружено расчетных режимов - {rgms.Count()}{Environment.NewLine}" + $"Загружено аварийных процесслов - {scns.Count()}{Environment.NewLine}");
			}
			RgmsInfo = rgms;
			ScnsInfo = scns;
			VrnInf = vrns;
			Rems = rems;
			KprInf = kprs;
			_w = sender as BackgroundWorker;
			Directory.CreateDirectory(tmp_root);
		}

		public List<UostResults> Calc()
		{
			int num = 0;
			List<UostResults> list = new List<UostResults>();
			int num2 = 1;
			foreach (RgmsInfo item in RgmsInfo)
			{
				List<UostShems> list2 = new List<UostShems>();
				foreach (VrnInfo item2 in VrnInf.Where((VrnInfo k) => !k.Deactive))
				{
					bool flag = false;
					List<UostEvents> list3 = new List<UostEvents>();
					foreach (ScnsInfo item3 in ScnsInfo)
					{
						RastrOperations rastrOperations = new RastrOperations();
						rastrOperations.Load(item.Name);
						rastrOperations.DynSettings();
						flag = ((item2.Id == -1) ? rastrOperations.rgm() : rastrOperations.ApplyVariant(item2.Num, Rems.Name));
						if (!flag)
						{
							continue;
						}
						rastrOperations.Load(item3.Name);
						double distance = 100.0;
						string text = "";
						int num3 = 0;
						double time_start = 0.0;
						double num4 = -1.0;
						double num5 = -1.0;
						int r_id = 0;
						int x_id = 0;
						foreach (int item4 in rastrOperations.Selection("DFWAutoActionScn"))
						{
							if (rastrOperations.getVal("DFWAutoActionScn", "ObjectClass", item4) == "vetv")
							{
								text = rastrOperations.getVal("DFWAutoActionScn", "ObjectKey", item4);
								rastrOperations.setVal("DFWAutoActionScn", "State", item4, 1);
							}
							if (rastrOperations.getVal("DFWAutoActionScn", "ObjectClass", item4) == "node")
							{
								num3 = Convert.ToInt32(rastrOperations.getVal("DFWAutoActionScn", "ObjectKey", item4));
								time_start = rastrOperations.getVal("DFWAutoActionScn", "TimeStart", item4);
								rastrOperations.setVal("DFWAutoActionScn", "ObjectKey", item4, num2);
								if (rastrOperations.getVal("DFWAutoActionScn", "ObjectProp", item4) == "r")
								{
									num4 = Convert.ToDouble(rastrOperations.getVal("DFWAutoActionScn", "Formula", item4).Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator));
									r_id = item4;
								}
								if (rastrOperations.getVal("DFWAutoActionScn", "ObjectProp", item4) == "x")
								{
									num5 = Convert.ToDouble(rastrOperations.getVal("DFWAutoActionScn", "Formula", item4).Replace(".", CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator));
									x_id = item4;
								}
							}
						}
						double num6 = ((num4 == -1.0) ? (Math.PI / 2.0) : Math.Atan(num5 / num4));
						double num7 = Math.Sqrt(((num4 != -1.0) ? Math.Pow(num4, 2.0) : 0.0) + Math.Pow(num5, 2.0));
						int num8 = Convert.ToInt32(text.Split(new char[1] { ',' })[0]);
						int num9 = Convert.ToInt32(text.Split(new char[1] { ',' })[1]);
						int num10 = Convert.ToInt32(text.Split(new char[1] { ',' })[2]);
						double num11 = ((num8 == num3) ? 0.1 : 99.9);
						double num12 = 100.0 - num11;
						double r = rastrOperations.getVal("vetv", "r", $"ip = {num8} & iq = {num9} & np = {num10}");
						double x = rastrOperations.getVal("vetv", "x", $"ip = {num8} & iq = {num9} & np = {num10}");
						double num13 = rastrOperations.getVal("vetv", "b", $"ip = {num8} & iq = {num9} & np = {num10}");
						rastrOperations.setVal("vetv", "sta", $"ip = {num8} & iq = {num9} & np = {num10}", 1);
						rastrOperations.setVal("node", "bsh", $"ny = {num8}", num13 / 2.0);
						rastrOperations.setVal("node", "bsh", $"ny = {num9}", num13 / 2.0);
						int num14 = rastrOperations.AddTableRow("node");
						rastrOperations.setVal("node", "ny", num14, num2);
						rastrOperations.setVal("node", "uhom", num14, rastrOperations.getVal("node", "uhom", $"ny = {num3}"));
						int num15 = rastrOperations.AddTableRow("vetv");
						int num16 = rastrOperations.AddTableRow("vetv");
						rastrOperations.setVal("vetv", "ip", num15, num8);
						rastrOperations.setVal("vetv", "iq", num15, num2);
						rastrOperations.setVal("vetv", "ip", num16, num2);
						rastrOperations.setVal("vetv", "iq", num16, num9);
						rastrOperations.rgm();
						rastrOperations.SetLineForUostCalc(num15, num16, r, x, num11);
						DynamicResult dynamicResult = rastrOperations.RunDynamic(_ems: true);
						rastrOperations.SetLineForUostCalc(num15, num16, r, x, num12);
						DynamicResult dynamicResult2 = rastrOperations.RunDynamic(_ems: true);
						if (dynamicResult.IsSuccess && dynamicResult2.IsSuccess && (dynamicResult.IsStable ^ dynamicResult2.IsStable))
						{
							double num17 = (dynamicResult.IsStable ? num11 : num12);
							double num18 = (dynamicResult.IsStable ? num12 : num11);
							double num19 = Math.Abs(num17 - num18) * 0.5;
							rastrOperations.SetLineForUostCalc(num15, num16, r, x, num19);
							DynamicResult dynamicResult3 = rastrOperations.RunDynamic(_ems: true);
							while (dynamicResult3.IsSuccess && (!dynamicResult3.IsStable || Math.Abs(num17 - num18) > 0.5))
							{
								if (dynamicResult3.IsStable)
								{
									num17 = num19;
								}
								else
								{
									num18 = num19;
								}
								num19 += Math.Abs(num18 - num17) * 0.5 * (double)(((dynamicResult.IsStable && dynamicResult3.IsStable) || (!dynamicResult.IsStable && !dynamicResult3.IsStable)) ? 1 : (-1));
								distance = num19;
								rastrOperations.SetLineForUostCalc(num15, num16, r, x, num19);
								dynamicResult3 = rastrOperations.RunDynamic(_ems: true);
							}
						}
						else if (dynamicResult.IsSuccess && !dynamicResult.IsStable && dynamicResult2.IsSuccess && !dynamicResult.IsStable)
						{
							distance = -1.0;
							rastrOperations.SetLineForUostCalc(num15, num16, r, x, (num8 == num3) ? 99.9 : 0.1);
							double num20 = ((num7 > 0.1) ? (num7 * 2.0) : 1.0);
							double num21 = num7;
							if (num4 == -1.0)
							{
								rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6));
							}
							else
							{
								rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6), r_id, num20 * Math.Cos(num6));
							}
							DynamicResult dynamicResult4 = rastrOperations.RunDynamic(_ems: true);
							while (dynamicResult4.IsSuccess && !dynamicResult4.IsStable)
							{
								num21 = num20;
								num20 += ((num7 > 0.1) ? num7 : 1.0);
								if (num4 == -1.0)
								{
									rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6));
								}
								else
								{
									rastrOperations.ChangeRXForUostCalc(x_id, num20 * Math.Sin(num6), r_id, num20 * Math.Cos(num6));
								}
								dynamicResult4 = rastrOperations.RunDynamic(_ems: true);
							}
							while (dynamicResult4.IsSuccess && (!dynamicResult4.IsStable || 1.0 - num21 / num20 > 0.025))
							{
								double num22 = (dynamicResult4.IsStable ? ((num21 - num20) * 0.5) : ((num20 - num21) * 0.5));
								double num23 = num20 + num22;
								if (num4 == -1.0)
								{
									rastrOperations.ChangeRXForUostCalc(x_id, num23 * Math.Sin(num6));
								}
								else
								{
									rastrOperations.ChangeRXForUostCalc(x_id, num23 * Math.Sin(num6), r_id, num23 * Math.Cos(num6));
								}
								dynamicResult4 = rastrOperations.RunDynamic(_ems: true);
								if (dynamicResult4.IsStable)
								{
									num20 = num23;
								}
								else
								{
									num21 = num23;
								}
							}
						}
						List<Values> list4 = new List<Values>();
						double beginUost = -1.0;
						double endUost = -1.0;
						DynamicResult dynamicResult5 = rastrOperations.RunDynamic(_ems: false, time_start + 0.02);
						if (dynamicResult5.IsSuccess && dynamicResult5.IsStable)
						{
							beginUost = (from k in rastrOperations.GetPointsFromExitFile("node", "vras", $"ny = {num8}")
								where k.X == time_start
								select k).FirstOrDefault().Y;
							endUost = (from k in rastrOperations.GetPointsFromExitFile("node", "vras", $"ny = {num9}")
								where k.X == time_start
								select k).FirstOrDefault().Y;
						}
						foreach (KprInfo item5 in KprInf)
						{
							list4.Add(new Values
							{
								Id = item5.Id,
								Name = item5.Name,
								Value = rastrOperations.getVal(item5.Table, item5.Col, item5.Selection)
							});
						}
						list3.Add(new UostEvents
						{
							Name = item3.name,
							Values = list4,
							BeginNode = num8,
							EndNode = num9,
							Np = num10,
							BeginUost = beginUost,
							EndUost = endUost,
							Distance = distance
						});
						num++;
						_w.ReportProgress(num);
					}
					list2.Add(new UostShems
					{
						ShemeName = item2.Name,
						IsStable = flag,
						Events = list3
					});
				}
				list.Add(new UostResults
				{
					RgName = item.name,
					UostShems = list2
				});
			}
			return list;
		}
	}
	internal class InitialDataException : Exception
	{
		public InitialDataException(string message)
			: base(message)
		{
		}
	}
	internal class UserLicenseException : Exception
	{
		public UserLicenseException(string message)
			: base(message)
		{
		}
	}
	internal class UncorrectFileException : Exception
	{
		public UncorrectFileException(string message)
			: base(message)
		{
		}
	}
	public class App : Application
	{
		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			((Application)this).StartupUri = new Uri("MainWindow.xaml", UriKind.Relative);
		}

		[STAThread]
		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public static void Main()
		{
			App app = new App();
			app.InitializeComponent();
			((Application)app).Run();
		}
	}
	public class DataInfo : INotifyPropertyChanged
	{
		private readonly string execution_root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);

		private int _progress;

		private int _max;

		private string _label;

		public bool IsActive;

		public Settings SetWin;

		private RgmsInfo _selectedRGM;

		private ScnsInfo _selectedScn;

		private bool _UseTypeValU;

		private bool _UseSelNodes;

		private bool _DynNoPA;

		private bool _DynWithPA;

		private bool _SaveGRF;

		private RelayCommand _add;

		private RelayCommand _del;

		private RelayCommand _set;

		private RelayCommand _shunt_calc;

		private RelayCommand _time_kz_calc;

		private RelayCommand _dyn_calc;

		private RelayCommand _mdp_calc;

		private RelayCommand _u_ost_calc;

		public int Progress
		{
			get
			{
				return _progress;
			}
			set
			{
				_progress = value;
				OnPropertyChanged("Progress");
			}
		}

		public int Max
		{
			get
			{
				return _max;
			}
			set
			{
				_max = value;
				OnPropertyChanged("Max");
			}
		}

		public string Label
		{
			get
			{
				return _label;
			}
			set
			{
				_label = value;
				OnPropertyChanged("Label");
			}
		}

		public ObservableCollection<RgmsInfo> RgmsInfo { get; set; }

		public RgmsInfo SelectedRgm
		{
			get
			{
				return _selectedRGM;
			}
			set
			{
				_selectedRGM = value;
				OnPropertyChanged("SelectedRgm");
			}
		}

		public ObservableCollection<ScnsInfo> ScnsInfo { get; set; }

		public ScnsInfo SelectedScn
		{
			get
			{
				return _selectedScn;
			}
			set
			{
				_selectedScn = value;
				OnPropertyChanged("SelectedScn");
			}
		}

		public FileInfo Sechen { get; set; }

		public List<SchInfo> SchInf { get; set; }

		public FileInfo VIR { get; set; }

		public FileInfo GRF { get; set; }

		public List<KprInfo> KprInf { get; set; }

		public FileInfo LAPNU { get; set; }

		public FileInfo Rems { get; set; }

		public List<VrnInfo> VrnInf { get; set; }

		public bool UseTypeValU
		{
			get
			{
				return _UseTypeValU;
			}
			set
			{
				_UseTypeValU = value;
				OnPropertyChanged("UseTypeValU");
			}
		}

		public bool UseSelNodes
		{
			get
			{
				return _UseSelNodes;
			}
			set
			{
				_UseSelNodes = value;
				OnPropertyChanged("UseSelNodes");
			}
		}

		public bool CalcOnePhase { get; set; }

		public bool CalcTwoPhase { get; set; }

		public FileInfo ShuntKZ { get; set; }

		public List<ShuntKZ> ShuntKZInf { get; set; }

		public double BaseAngle { get; set; }

		public double CrtTimePrecision { get; set; }

		public double CrtTimeMax { get; set; }

		public int SelectedSch { get; set; }

		public bool DynNoPA
		{
			get
			{
				return _DynNoPA;
			}
			set
			{
				_DynNoPA = value;
				OnPropertyChanged("DynNoPA");
			}
		}

		public bool DynWithPA
		{
			get
			{
				return _DynWithPA;
			}
			set
			{
				_DynWithPA = value;
				OnPropertyChanged("DynWithPA");
			}
		}

		public bool SaveGRF
		{
			get
			{
				return _SaveGRF;
			}
			set
			{
				_SaveGRF = value;
				OnPropertyChanged("SaveGRF");
			}
		}

		public bool UseLPN { get; set; }

		public string tmp_root { get; set; }

		public string lpns { get; set; }

		public List<ShuntResults> ShuntResults { get; set; }

		public List<CrtTimeResults> CrtTimeResults { get; set; }

		public List<DynResults> DynResults { get; set; }

		public List<MdpResults> MdpResults { get; set; }

		public List<UostResults> UostResults { get; set; }

		public RelayCommand Add => _add ?? (_add = new RelayCommand(delegate
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Expected O, but got Unknown
			//IL_0c88: Unknown result type (might be due to invalid IL or missing references)
			OpenFileDialog val = new OpenFileDialog();
			((FileDialog)val).Title = "Выбор файлов";
			((FileDialog)val).Filter = "Rastr|*.rg2;*.rst;*.sch;*.ut2;*.scn;*.vrn;*.kpr;*.csv;*.lpn;*.dwf";
			val.Multiselect = true;
			try
			{
				if (((CommonDialog)val).ShowDialog() == true)
				{
					string[] fileNames = ((FileDialog)val).FileNames;
					foreach (string file in fileNames)
					{
						if ((Path.GetExtension(file) == ".rg2" || Path.GetExtension(file) == ".rst") && !RgmsInfo.Any((RgmsInfo k) => k.Name == file))
						{
							RgmsInfo.Add(new RgmsInfo
							{
								Name = file
							});
						}
						else if (Path.GetExtension(file) == ".scn" && !ScnsInfo.Any((ScnsInfo k) => k.Name == file))
						{
							ScnsInfo.Add(new ScnsInfo
							{
								Name = file
							});
						}
						else if (Path.GetExtension(file) == ".ut2")
						{
							VIR.Name = file;
						}
						else if (Path.GetExtension(file) == ".sch")
						{
							Sechen.Name = file;
							SchInf.Clear();
							RastrOperations rastrOperations = new RastrOperations();
							rastrOperations.Load(file);
							foreach (int item in rastrOperations.Selection("sechen"))
							{
								SchInf.Add(new SchInfo
								{
									Id = item,
									Name = rastrOperations.getVal("sechen", "name", item),
									Num = rastrOperations.getVal("sechen", "ns", item),
									Control = rastrOperations.getVal("sechen", "sta", item)
								});
							}
						}
						else if (Path.GetExtension(file) == ".vrn")
						{
							Rems.Name = file;
							VrnInf.Clear();
							VrnInf.Add(new VrnInfo
							{
								Id = -1,
								Name = "Нормальная схема",
								Num = 0,
								Deactive = false
							});
							RastrOperations rastrOperations2 = new RastrOperations();
							rastrOperations2.Load(file);
							foreach (int item2 in rastrOperations2.Selection("var_mer"))
							{
								VrnInf.Add(new VrnInfo
								{
									Id = item2,
									Name = rastrOperations2.getVal("var_mer", "name", item2),
									Num = rastrOperations2.getVal("var_mer", "Num", item2),
									Deactive = rastrOperations2.getVal("var_mer", "sta", item2)
								});
							}
						}
						else if (Path.GetExtension(file) == ".kpr")
						{
							GRF.Name = file;
							KprInf.Clear();
							RastrOperations rastrOperations3 = new RastrOperations();
							rastrOperations3.Load(file);
							foreach (int item3 in rastrOperations3.Selection("ots_val"))
							{
								KprInf.Add(new KprInfo
								{
									Id = item3,
									Num = rastrOperations3.getVal("ots_val", "Num", item3),
									Name = rastrOperations3.getVal("ots_val", "name", item3),
									Table = rastrOperations3.getVal("ots_val", "tabl", item3),
									Selection = rastrOperations3.getVal("ots_val", "vibork", item3),
									Col = rastrOperations3.getVal("ots_val", "formula", item3)
								});
							}
						}
						else if (Path.GetExtension(file) == ".csv")
						{
							string[] array = File.ReadAllLines(file);
							string[] array2 = array[0].Split(new char[1] { ';' });
							if (array2.Length != 7 || !(array2[0] == "node") || !(array2[1] == "r1") || !(array2[2] == "x1") || !(array2[3] == "u1") || !(array2[4] == "r2") || !(array2[5] == "x2") || !(array2[6] == "u2"))
							{
								throw new UncorrectFileException("Некорректный файл для задания шунтов КЗ");
							}
							string numberDecimalSeparator = CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator;
							string oldValue = ((numberDecimalSeparator == ".") ? "," : ".");
							ShuntKZ.Name = file;
							UseSelNodes = false;
							for (int num = 1; num < array.Count(); num++)
							{
								string[] array3 = array[num].Split(new char[1] { ';' });
								ShuntKZInf.Add(new ShuntKZ
								{
									Node = Convert.ToInt32(array3[0]),
									r1 = ((array3[1] != "" && array3[1] != "0") ? Convert.ToDouble(array3[1].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
									x1 = ((array3[2] != "" && array3[2] != "0") ? Convert.ToDouble(array3[2].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
									u1 = ((array3[3] != "" && array3[3] != "0") ? Convert.ToDouble(array3[3].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
									r2 = ((array3[4] != "" && array3[4] != "0") ? Convert.ToDouble(array3[4].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
									x2 = ((array3[5] != "" && array3[5] != "0") ? Convert.ToDouble(array3[5].Replace(oldValue, numberDecimalSeparator)) : (-1.0)),
									u2 = ((array3[6] != "" && array3[6] != "0") ? Convert.ToDouble(array3[6].Replace(oldValue, numberDecimalSeparator)) : (-1.0))
								});
							}
						}
						else if (Path.GetExtension(file) == ".dwf" || Path.GetExtension(file) == ".lpn")
						{
							DynWithPA = true;
							LAPNU.Name = file;
							UseLPN = Path.GetExtension(file) == ".lpn";
							if (UseLPN)
							{
								RastrOperations rastrOperations4 = new RastrOperations();
								rastrOperations4.Load(file);
								List<int> list = new List<int>();
								foreach (int item4 in rastrOperations4.Selection("LAPNU", "sta = 0"))
								{
									list.Add(rastrOperations4.getVal("LAPNU", "Id", item4));
								}
								lpns = "=" + string.Join(";", list);
							}
						}
					}
				}
			}
			catch (Exception ex)
			{
				MessageBox.Show("Ошибка при выполнении операции!" + Environment.NewLine + Environment.NewLine + ex.Message, "Error", (MessageBoxButton)0, (MessageBoxImage)16);
			}
		}));

		public RelayCommand Del => _del ?? (_del = new RelayCommand(delegate
		{
			RgmsInfo.Remove(_selectedRGM);
			ScnsInfo.Remove(_selectedScn);
		}));

		public RelayCommand Settings => _set ?? (_set = new RelayCommand(delegate
		{
			SetWin = new Settings();
			((FrameworkElement)SetWin).DataContext = this;
			((Window)SetWin).Show();
		}));

		public RelayCommand ShuntCalc => _shunt_calc ?? (_shunt_calc = new RelayCommand(delegate
		{
			if (!IsActive)
			{
				BackgroundWorker backgroundWorker = new BackgroundWorker
				{
					WorkerReportsProgress = true
				};
				backgroundWorker.DoWork += Shunt_KZ;
				backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
				{
					Progress = e.ProgressPercentage;
					Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
				};
				backgroundWorker.RunWorkerCompleted += EventFinish;
				backgroundWorker.RunWorkerAsync();
			}
		}));

		public RelayCommand TimeKzCalc => _time_kz_calc ?? (_time_kz_calc = new RelayCommand(delegate
		{
			if (!IsActive)
			{
				BackgroundWorker backgroundWorker = new BackgroundWorker
				{
					WorkerReportsProgress = true
				};
				backgroundWorker.DoWork += Max_KZ_Time;
				backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
				{
					Progress = e.ProgressPercentage;
					Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
				};
				backgroundWorker.RunWorkerCompleted += EventFinish;
				backgroundWorker.RunWorkerAsync();
			}
		}));

		public RelayCommand DynamicCalc => _dyn_calc ?? (_dyn_calc = new RelayCommand(delegate
		{
			if (!IsActive)
			{
				BackgroundWorker backgroundWorker = new BackgroundWorker
				{
					WorkerReportsProgress = true
				};
				backgroundWorker.DoWork += DynStabilityCalc;
				backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
				{
					Progress = e.ProgressPercentage;
					Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
				};
				backgroundWorker.RunWorkerCompleted += EventFinish;
				backgroundWorker.RunWorkerAsync();
			}
		}));

		public RelayCommand MdpCalc => _mdp_calc ?? (_mdp_calc = new RelayCommand(delegate
		{
			if (!IsActive)
			{
				BackgroundWorker backgroundWorker = new BackgroundWorker
				{
					WorkerReportsProgress = true
				};
				backgroundWorker.DoWork += MdpStabilityCalc;
				backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
				{
					Progress = e.ProgressPercentage;
					Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
				};
				backgroundWorker.RunWorkerCompleted += EventFinish;
				backgroundWorker.RunWorkerAsync();
			}
		}));

		public RelayCommand UostCalc => _u_ost_calc ?? (_u_ost_calc = new RelayCommand(delegate
		{
			if (!IsActive)
			{
				BackgroundWorker backgroundWorker = new BackgroundWorker
				{
					WorkerReportsProgress = true
				};
				backgroundWorker.DoWork += UostStabilityCalc;
				backgroundWorker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e)
				{
					Progress = e.ProgressPercentage;
					Label = $"Выполнено {100.0 * (double)e.ProgressPercentage / (double)Max:F2} %";
				};
				backgroundWorker.RunWorkerCompleted += EventFinish;
				backgroundWorker.RunWorkerAsync();
			}
		}));

		public event PropertyChangedEventHandler PropertyChanged;

		public DataInfo()
		{
			bool flag = File.Exists(execution_root + "\\EPPlus.dll");
			bool flag2 = File.Exists(execution_root + "\\EPPlus.Interfaces.dll");
			bool flag3 = File.Exists(execution_root + "\\OxyPlot.dll");
			bool flag4 = File.Exists(execution_root + "\\OxyPlot.Wpf.dll");
			if (!(flag && flag2 && flag3 && flag4))
			{
				throw new FileNotFoundException("Не обнаружены необходимые для работы DSS библиотеки." + Environment.NewLine + Environment.NewLine + "Результаты проверки:" + Environment.NewLine + "EPPlus.dll - " + (flag ? "Обнаружена" : "Отсутствует") + Environment.NewLine + "EPPlus.Interfaces.dll - " + (flag2 ? "Обнаружена" : "Отсутствует") + Environment.NewLine + "OxyPlot.dll - " + (flag3 ? "Обнаружена" : "Отсутствует") + Environment.NewLine + "OxyPlot.Wpf.dll - " + (flag4 ? "Обнаружена" : "Отсутствует"));
			}
			IsActive = false;
			RgmsInfo = new ObservableCollection<RgmsInfo>();
			ScnsInfo = new ObservableCollection<ScnsInfo>();
			VIR = new FileInfo();
			Sechen = new FileInfo();
			GRF = new FileInfo();
			Rems = new FileInfo();
			SchInf = new List<SchInfo>();
			VrnInf = new List<VrnInfo>
			{
				new VrnInfo
				{
					Id = -1,
					Name = "Нормальная схема",
					Num = 0,
					Deactive = false
				}
			};
			KprInf = new List<KprInfo>();
			LAPNU = new FileInfo();
			UseTypeValU = true;
			UseSelNodes = true;
			CalcOnePhase = true;
			CalcTwoPhase = true;
			ShuntKZ = new FileInfo();
			ShuntKZInf = new List<ShuntKZ>();
			CrtTimePrecision = 0.02;
			CrtTimeMax = 1.0;
			DynNoPA = true;
			DynWithPA = false;
			SaveGRF = false;
			UseLPN = false;
			tmp_root = Environment.GetFolderPath(Environment.SpecialFolder.Personal) + "\\DynStabSpace";
			Directory.CreateDirectory(tmp_root);
			lpns = "";
			SelectedSch = 0;
			ShuntResults = new List<ShuntResults>();
			CrtTimeResults = new List<CrtTimeResults>();
			DynResults = new List<DynResults>();
			MdpResults = new List<MdpResults>();
			UostResults = new List<UostResults>();
			Progress = 0;
			Max = 1;
			Label = "";
		}

		private void UostStabilityCalc(object sender, DoWorkEventArgs e)
		{
			IsActive = true;
			ClearAllResults();
			UostStabilityCalc uostStabilityCalc = new UostStabilityCalc(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, KprInf);
			Max = uostStabilityCalc.Max;
			Progress = 0;
			UostResults = uostStabilityCalc.Calc();
			ResultToFiles(uostStabilityCalc.root);
			e.Result = uostStabilityCalc.root;
			(sender as BackgroundWorker).ReportProgress(Progress + 1);
		}

		private void MdpStabilityCalc(object sender, DoWorkEventArgs e)
		{
			IsActive = true;
			ClearAllResults();
			MdpStabilityCalc mdpStabilityCalc = new MdpStabilityCalc(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, VIR, Sechen, LAPNU, SchInf, KprInf, lpns, SelectedSch, DynNoPA, DynWithPA, UseLPN);
			Max = mdpStabilityCalc.Max;
			Progress = 0;
			MdpResults = mdpStabilityCalc.Calc();
			ResultToFiles(mdpStabilityCalc.root);
			e.Result = mdpStabilityCalc.root;
			(sender as BackgroundWorker).ReportProgress(Progress + 1);
		}

		private void DynStabilityCalc(object sender, DoWorkEventArgs e)
		{
			IsActive = true;
			ClearAllResults();
			DynStabilityCalc dynStabilityCalc = new DynStabilityCalc(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, KprInf, Sechen, LAPNU, SaveGRF, lpns, DynNoPA, DynWithPA, UseLPN);
			Max = dynStabilityCalc.Max;
			Progress = 0;
			DynResults = dynStabilityCalc.Calc();
			ResultToFiles(dynStabilityCalc.root);
			e.Result = dynStabilityCalc.root;
			(sender as BackgroundWorker).ReportProgress(Progress + 1);
		}

		private void Max_KZ_Time(object sender, DoWorkEventArgs e)
		{
			IsActive = true;
			ClearAllResults();
			Max_KZ_Time max_KZ_Time = new Max_KZ_Time(sender, RgmsInfo, ScnsInfo, VrnInf, Rems, CrtTimePrecision, CrtTimeMax);
			Max = max_KZ_Time.Max;
			Progress = 0;
			CrtTimeResults = max_KZ_Time.Calc();
			ResultToFiles(max_KZ_Time.root);
			e.Result = max_KZ_Time.root;
			(sender as BackgroundWorker).ReportProgress(Progress + 1);
		}

		private void Shunt_KZ(object sender, DoWorkEventArgs e)
		{
			IsActive = true;
			ClearAllResults();
			Shunt_KZ shunt_KZ = new Shunt_KZ(sender, RgmsInfo, VrnInf, Rems, ShuntKZInf, UseSelNodes, UseTypeValU, CalcOnePhase, CalcTwoPhase);
			Max = shunt_KZ.Max;
			Progress = 0;
			ShuntResults = shunt_KZ.Calc();
			ResultToFiles(shunt_KZ.root);
			e.Result = shunt_KZ.root;
			(sender as BackgroundWorker).ReportProgress(Progress + 1);
		}

		private void EventFinish(object sender, RunWorkerCompletedEventArgs e)
		{
			//IL_006c: Unknown result type (might be due to invalid IL or missing references)
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			if (e.Error == null)
			{
				MessageBox.Show("Операция выполнена успешно!" + Environment.NewLine + Environment.NewLine + $"Результаты доступны в каталоге {e.Result}", "DSS", (MessageBoxButton)0, (MessageBoxImage)64);
			}
			else
			{
				MessageBox.Show("Ошибка при выполнении операции!" + Environment.NewLine + Environment.NewLine + e.Error.Message, "DSS Algorithm Error", (MessageBoxButton)0, (MessageBoxImage)16);
			}
			Label = "";
			Progress = 0;
			IsActive = false;
		}

		private void ResultToFiles(string root)
		{
			int num = ((ShuntResults.Count() > 0) ? 1 : 0) + ((CrtTimeResults.Count() > 0) ? 2 : 0) + ((DynResults.Count() > 0) ? 3 : 0) + ((MdpResults.Count() > 0) ? 4 : 0) + ((UostResults.Count() > 0) ? 5 : 0);
			int num2 = 2;
			ExcelOperations excelOperations = new ExcelOperations("Результаты расчетов");
			excelOperations.Font();
			excelOperations.setVal(1, 1, "Наименование режима");
			excelOperations.Width(1, 40);
			excelOperations.setVal(1, 2, "Схема сети");
			excelOperations.Width(2, 40);
			switch (num)
			{
			case 1:
				excelOperations.Merge(1, 1, 2, 1, hor: true, vert: true);
				excelOperations.Merge(1, 2, 2, 2, hor: true, vert: true);
				excelOperations.setVal(1, 3, "Номер узла");
				excelOperations.Merge(1, 3, 2, 3, hor: true, vert: true);
				excelOperations.Width(3, 15);
				excelOperations.setVal(1, 4, "Однофазное КЗ");
				excelOperations.Merge(1, 4, 1, 6, hor: true, vert: true);
				excelOperations.setVal(2, 4, "R, Ом");
				excelOperations.Width(4, 15);
				excelOperations.setVal(2, 5, "X, Ом");
				excelOperations.Width(5, 15);
				excelOperations.setVal(2, 6, "U1, кВ");
				excelOperations.Width(6, 15);
				excelOperations.setVal(1, 7, "Двухфазное КЗ");
				excelOperations.Merge(1, 7, 1, 9, hor: true, vert: true);
				excelOperations.setVal(2, 7, "R, Ом");
				excelOperations.Width(7, 15);
				excelOperations.setVal(2, 8, "X, Ом");
				excelOperations.Width(8, 15);
				excelOperations.setVal(2, 9, "U1, кВ");
				excelOperations.Width(9, 15);
				excelOperations.Format(1, 1, 2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
				excelOperations.Borders(1, 1, 2, 9);
				num2++;
				foreach (ShuntResults shuntResult in ShuntResults)
				{
					excelOperations.setVal(num2, 1, shuntResult.RgName);
					int bRow7 = num2;
					foreach (Shems shem in shuntResult.Shems)
					{
						int bRow8 = num2;
						excelOperations.setVal(num2, 2, shem.ShemeName);
						if (shem.IsStable)
						{
							foreach (ShuntKZ node in shem.Nodes)
							{
								excelOperations.setVal(num2, 3, node.Node);
								excelOperations.setVal(num2, 4, $"{node.r1:F3}");
								excelOperations.setVal(num2, 5, $"{node.x1:F3}");
								excelOperations.setVal(num2, 6, $"{node.u1:F1}");
								excelOperations.setVal(num2, 7, $"{node.r2:F3}");
								excelOperations.setVal(num2, 8, $"{node.x2:F3}");
								excelOperations.setVal(num2, 9, $"{node.u2:F1}");
								excelOperations.Format(num2, 3, num2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
								num2++;
							}
						}
						else
						{
							excelOperations.setVal(num2, 3, "Схема не балансируется");
							excelOperations.Merge(num2, 3, num2, 9, hor: true, vert: true);
							num2++;
						}
						excelOperations.Merge(bRow8, 2, num2 - 1, 2, hor: true, vert: true);
					}
					excelOperations.Merge(bRow7, 1, num2 - 1, 1, hor: true, vert: true);
					excelOperations.Borders(bRow7, 1, num2 - 1, 9);
				}
				if (!CalcOnePhase)
				{
					excelOperations.HideColumn(4);
					excelOperations.HideColumn(5);
					excelOperations.HideColumn(6);
				}
				if (!CalcTwoPhase)
				{
					excelOperations.HideColumn(7);
					excelOperations.HideColumn(8);
					excelOperations.HideColumn(9);
				}
				break;
			case 2:
				excelOperations.setVal(1, 3, "Расчетное КЗ");
				excelOperations.Width(3, 40);
				excelOperations.setVal(1, 4, "Предельное время отключения, с");
				excelOperations.Width(4, 15);
				excelOperations.Format(1, 1, 1, 4, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
				excelOperations.Borders(1, 1, 1, 4);
				foreach (CrtTimeResults crtTimeResult in CrtTimeResults)
				{
					excelOperations.setVal(num2, 1, crtTimeResult.RgName);
					int bRow3 = num2;
					foreach (CrtShems crtShem in crtTimeResult.CrtShems)
					{
						int bRow4 = num2;
						excelOperations.setVal(num2, 2, crtShem.ShemeName);
						if (crtShem.IsStable)
						{
							foreach (CrtTimes time in crtShem.Times)
							{
								excelOperations.setVal(num2, 3, time.ScnName);
								excelOperations.setVal(num2, 4, (CrtTimeMax != time.CrtTime) ? $"{time.CrtTime:F3}" : $">{time.CrtTime}");
								num2++;
							}
						}
						else
						{
							excelOperations.setVal(num2, 3, "Схема не балансируется");
							excelOperations.Merge(num2, 3, num2, 4, hor: true, vert: true);
							num2++;
						}
						excelOperations.Merge(bRow4, 2, num2 - 1, 2, hor: true, vert: true);
					}
					excelOperations.Merge(bRow3, 1, num2 - 1, 1, hor: true, vert: true);
					excelOperations.Format(bRow3, 1, num2 - 1, 4, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
					excelOperations.Borders(bRow3, 1, num2 - 1, 4);
				}
				break;
			case 3:
				excelOperations.Merge(1, 1, 2, 1, hor: true, vert: true);
				excelOperations.Merge(1, 2, 2, 2, hor: true, vert: true);
				excelOperations.setVal(1, 3, "Расчетный сценарий");
				excelOperations.Merge(1, 3, 2, 3, hor: true, vert: true);
				excelOperations.Width(3, 15);
				excelOperations.setVal(1, 4, "Без учета действия ПА");
				excelOperations.Merge(1, 4, 1, 6, hor: true, vert: true);
				excelOperations.setVal(2, 4, "Результат расчета ДУ");
				excelOperations.Width(4, 20);
				excelOperations.setVal(2, 5, "Критерий нарушения ДУ");
				excelOperations.Width(5, 40);
				excelOperations.setVal(2, 6, "Рисунок");
				excelOperations.Width(6, 20);
				excelOperations.setVal(1, 7, "С учетом действия ПА");
				excelOperations.Merge(1, 7, 1, 9, hor: true, vert: true);
				excelOperations.setVal(2, 7, "Результат расчета ДУ");
				excelOperations.Width(7, 20);
				excelOperations.setVal(2, 8, "Критерий нарушения ДУ");
				excelOperations.Width(8, 40);
				excelOperations.setVal(2, 9, "Рисунок");
				excelOperations.Width(9, 20);
				excelOperations.Format(1, 1, 2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
				excelOperations.Borders(1, 1, 2, 9);
				num2++;
				foreach (DynResults dynResult in DynResults)
				{
					excelOperations.setVal(num2, 1, dynResult.RgName);
					int bRow5 = num2;
					foreach (DynShems dynShem in dynResult.DynShems)
					{
						int bRow6 = num2;
						excelOperations.setVal(num2, 2, dynShem.ShemeName);
						if (dynShem.IsStable)
						{
							foreach (Events @event in dynShem.Events)
							{
								excelOperations.setVal(num2, 3, @event.Name);
								if (@event.NoPaResult.IsSuccess)
								{
									excelOperations.setVal(num2, 4, @event.NoPaResult.IsStable ? "Устойчиво" : "Неустойчиво");
									excelOperations.setVal(num2, 5, @event.NoPaResult.IsStable ? "-" : @event.NoPaResult.ResultMessage);
									string text = "";
									foreach (string item in @event.NoPaPic)
									{
										text += ((@event.NoPaPic.IndexOf(item) > 0) ? (Environment.NewLine ?? "") : "");
										text += Path.GetFileNameWithoutExtension(item);
									}
									excelOperations.setVal(num2, 6, text);
								}
								if (@event.WithPaResult.IsSuccess)
								{
									excelOperations.setVal(num2, 7, @event.WithPaResult.IsStable ? "Устойчиво" : "Неустойчиво");
									excelOperations.setVal(num2, 8, @event.WithPaResult.IsStable ? "-" : @event.WithPaResult.ResultMessage);
									string text2 = "";
									foreach (string item2 in @event.WithPaPic)
									{
										text2 += ((@event.WithPaPic.IndexOf(item2) > 0) ? (Environment.NewLine ?? "") : "");
										text2 += Path.GetFileNameWithoutExtension(item2);
									}
									excelOperations.setVal(num2, 9, text2);
								}
								excelOperations.Format(num2, 3, num2, 9, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
								num2++;
							}
						}
						else
						{
							excelOperations.setVal(num2, 3, "Схема не балансируется");
							excelOperations.Merge(num2, 3, num2, 9, hor: true, vert: true);
							num2++;
						}
						excelOperations.Merge(bRow6, 2, num2 - 1, 2, hor: true, vert: true);
					}
					excelOperations.Merge(bRow5, 1, num2 - 1, 1, hor: true, vert: true);
					excelOperations.Borders(bRow5, 1, num2 - 1, 9);
				}
				if (!SaveGRF)
				{
					excelOperations.HideColumn(6);
					excelOperations.HideColumn(9);
				}
				if (!DynNoPA)
				{
					excelOperations.HideColumn(4);
					excelOperations.HideColumn(5);
					excelOperations.HideColumn(6);
				}
				if (!DynWithPA)
				{
					excelOperations.HideColumn(7);
					excelOperations.HideColumn(8);
					excelOperations.HideColumn(9);
				}
				break;
			case 4:
			{
				int num6 = SchInf.Where((SchInfo k) => k.Control).Count();
				int num3 = KprInf.Count();
				excelOperations.Merge(1, 1, 3, 1, hor: true, vert: true);
				excelOperations.Merge(1, 2, 3, 2, hor: true, vert: true);
				excelOperations.setVal(1, 3, "Расчетный сценарий");
				excelOperations.Merge(1, 3, 3, 3, hor: true, vert: true);
				excelOperations.Width(3, 15);
				excelOperations.setVal(1, 4, "Без учета действия ПА");
				excelOperations.setVal(2, 4, "МДП, МВт");
				excelOperations.Width(4, 15);
				excelOperations.Merge(2, 4, 3, 4, hor: true, vert: true);
				excelOperations.setVal(1, 5 + num6 + num3, "С учетом действия ПА");
				excelOperations.setVal(2, 5 + num6 + num3, "МДП, МВт");
				excelOperations.Width(5 + num6 + num3, 15);
				excelOperations.Merge(2, 5 + num6 + num3, 3, 5 + num6 + num3, hor: true, vert: true);
				if (num6 > 0)
				{
					int num7 = 0;
					excelOperations.setVal(2, 5, "Перетоки в КС, МВт");
					excelOperations.setVal(2, 6 + num6 + num3, "Перетоки в КС, МВт");
					foreach (SchInfo item3 in SchInf.Where((SchInfo k) => k.Control))
					{
						excelOperations.setVal(3, 5 + num7, item3.Name);
						excelOperations.setVal(3, 6 + num6 + num3 + num7, item3.Name);
						excelOperations.Width(5 + num7, 15);
						excelOperations.Width(6 + num6 + num3 + num7, 15);
						num7++;
					}
					excelOperations.Merge(2, 5, 2, 5 + num7 - 1, hor: true, vert: true);
					excelOperations.Merge(2, 6 + num6 + num3, 2, 6 + num6 + num3 + num7 - 1, hor: true, vert: true);
				}
				if (num3 > 0)
				{
					int num8 = 0;
					excelOperations.setVal(2, 5 + num6, "Контролируемые величины");
					excelOperations.setVal(2, 6 + 2 * num6 + num3, "Контролируемые величины");
					foreach (KprInfo item4 in KprInf)
					{
						excelOperations.setVal(3, 5 + num6 + num8, item4.Name);
						excelOperations.setVal(3, 6 + 2 * num6 + num3 + num8, item4.Name);
						excelOperations.Width(5 + num6 + num8, 15);
						excelOperations.Width(6 + 2 * num6 + num3, 15);
						num8++;
					}
					excelOperations.Merge(2, 5 + num6, 2, 5 + num6 + num8 - 1, hor: true, vert: true);
					excelOperations.Merge(2, 6 + 2 * num6 + num3, 2, 6 + 2 * num6 + num3 + num8 - 1, hor: true, vert: true);
				}
				if (num6 > 0 || num3 > 0)
				{
					excelOperations.Merge(1, 4, 1, 4 + num6 + num3, hor: true, vert: true);
					excelOperations.Merge(1, 5 + num6 + num3, 1, 5 + 2 * num6 + 2 * num3);
				}
				excelOperations.Format(1, 1, 3, 5 + 2 * num6 + 2 * num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
				excelOperations.Borders(1, 1, 3, 5 + 2 * num6 + 2 * num3);
				num2 += 2;
				foreach (MdpResults mdpResult in MdpResults)
				{
					excelOperations.setVal(num2, 1, mdpResult.RgName);
					int bRow9 = num2;
					foreach (MdpShems mdpShem in mdpResult.MdpShems)
					{
						int bRow10 = num2;
						excelOperations.setVal(num2, 2, mdpShem.ShemeName);
						if (mdpShem.IsStable)
						{
							foreach (MdpEvents event2 in mdpShem.Events)
							{
								excelOperations.setVal(num2, 3, event2.Name);
								excelOperations.setVal(num2, 4, $"{event2.NoPaMdp:F0}");
								excelOperations.setVal(num2, 5 + num6 + num3, $"{event2.WithPaMdp:F0}");
								if (num6 > 0)
								{
									for (int num9 = 0; num9 < num6; num9++)
									{
										excelOperations.setVal(num2, 5 + num9, (event2.NoPaSechen.Count() != 0) ? $"{event2.NoPaSechen.ElementAt(num9).Value:F0}" : "");
										excelOperations.setVal(num2, 6 + num6 + num3 + num9, (event2.WithPaSechen.Count() != 0) ? $"{event2.WithPaSechen.ElementAt(num9).Value:F0}" : "");
									}
								}
								if (num3 > 0)
								{
									for (int num10 = 0; num10 < num3; num10++)
									{
										excelOperations.setVal(num2, 5 + num6 + num10, (event2.NoPaKpr.Count() != 0) ? $"{event2.NoPaKpr.ElementAt(num10).Value:F2}" : "");
										excelOperations.setVal(num2, 6 + 2 * num6 + num3 + num10, (event2.WithPaKpr.Count() != 0) ? $"{event2.WithPaKpr.ElementAt(num10).Value:F2}" : "");
									}
								}
								excelOperations.Format(num2, 3, num2, 5 + 2 * num6 + 2 * num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
								num2++;
							}
						}
						else
						{
							excelOperations.setVal(num2, 3, "Схема не балансируется");
							excelOperations.Merge(num2, 3, num2, 5 + 2 * num6 + 2 * num3, hor: true, vert: true);
							num2++;
						}
						excelOperations.Merge(bRow10, 2, num2 - 1, 2, hor: true, vert: true);
					}
					excelOperations.Merge(bRow9, 1, num2 - 1, 1, hor: true, vert: true);
					excelOperations.Borders(bRow9, 1, num2 - 1, 5 + 2 * num6 + 2 * num3);
				}
				if (!DynNoPA)
				{
					for (int num11 = 4; num11 <= 4 + num6 + num3; num11++)
					{
						excelOperations.HideColumn(num11);
					}
				}
				if (!DynWithPA)
				{
					for (int num12 = 5 + num6 + num3; num12 <= 5 + 2 * num6 + 2 * num3; num12++)
					{
						excelOperations.HideColumn(num12);
					}
				}
				break;
			}
			case 5:
			{
				int num3 = KprInf.Count();
				excelOperations.Merge(1, 1, 2, 1, hor: true, vert: true);
				excelOperations.Merge(1, 2, 2, 2, hor: true, vert: true);
				excelOperations.setVal(1, 3, "Расчетный сценарий");
				excelOperations.Width(3, 15);
				excelOperations.Merge(1, 3, 2, 3, hor: true, vert: true);
				excelOperations.setVal(1, 4, "ЛЭП");
				excelOperations.setVal(2, 4, "Узел начала");
				excelOperations.Width(4, 15);
				excelOperations.setVal(2, 5, "Узел конца");
				excelOperations.Width(5, 15);
				excelOperations.setVal(2, 6, "Np");
				excelOperations.Width(6, 7);
				excelOperations.Merge(1, 4, 1, 6, hor: true, vert: true);
				excelOperations.setVal(1, 7, "Область устойчивости, %");
				excelOperations.Width(7, 15);
				excelOperations.Merge(1, 7, 2, 7, hor: true, vert: true);
				excelOperations.setVal(1, 8, "Остаточное напряжение в узлах ЛЭП, кВ");
				excelOperations.setVal(2, 8, "Узел начала");
				excelOperations.Width(8, 15);
				excelOperations.setVal(2, 9, "Узел конца");
				excelOperations.Width(9, 15);
				excelOperations.Merge(1, 8, 1, 9, hor: true, vert: true);
				if (num3 > 0)
				{
					int num4 = 0;
					excelOperations.setVal(1, 10, "Контролируемые величины");
					foreach (KprInfo item5 in KprInf)
					{
						excelOperations.setVal(2, 10 + num4, item5.Name);
						num4++;
					}
					excelOperations.Merge(1, 10, 1, 10 + num4 - 1, hor: true, vert: true);
				}
				excelOperations.Format(1, 1, 2, 9 + num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
				excelOperations.Borders(1, 1, 2, 9 + num3);
				num2++;
				foreach (UostResults uostResult in UostResults)
				{
					excelOperations.setVal(num2, 1, uostResult.RgName);
					int bRow = num2;
					foreach (UostShems uostShem in uostResult.UostShems)
					{
						int bRow2 = num2;
						excelOperations.setVal(num2, 2, uostShem.ShemeName);
						if (uostShem.IsStable)
						{
							foreach (UostEvents event3 in uostShem.Events)
							{
								excelOperations.setVal(num2, 3, event3.Name);
								excelOperations.setVal(num2, 4, event3.BeginNode);
								excelOperations.setVal(num2, 5, event3.EndNode);
								excelOperations.setVal(num2, 6, event3.Np);
								if (event3.Distance == -1.0)
								{
									excelOperations.setVal(num2, 7, ">100");
								}
								else if (event3.Distance == 100.0)
								{
									excelOperations.setVal(num2, 7, "<0");
								}
								else
								{
									excelOperations.setVal(num2, 7, $"{event3.Distance * 100.0:F2}");
								}
								excelOperations.setVal(num2, 8, $"{event3.BeginUost:F2}");
								excelOperations.setVal(num2, 9, $"{event3.EndUost:F2}");
								if (num3 > 0)
								{
									int num5 = 0;
									foreach (Values value in event3.Values)
									{
										excelOperations.setVal(num2, 10 + num5, value.Value);
										num5++;
									}
								}
								excelOperations.Format(num2, 3, num2, 9 + num3, ExcelHorizontalAlignment.Center, ExcelVerticalAlignment.Center);
								num2++;
							}
						}
						else
						{
							excelOperations.setVal(num2, 3, "Схема не балансируется");
							excelOperations.Merge(num2, 3, num2, 9 + num3, hor: true, vert: true);
							num2++;
						}
						excelOperations.Merge(bRow2, 2, num2 - 1, 2, hor: true, vert: true);
					}
					excelOperations.Merge(bRow, 1, num2 - 1, 1, hor: true, vert: true);
					excelOperations.Borders(bRow, 1, num2 - 1, 9 + num3);
				}
				break;
			}
			}
			excelOperations.Save(root + "\\Результат расчетов.xlsx");
			string[] files = Directory.GetFiles(root, "*.rst");
			foreach (string path in files)
			{
				File.Delete(path);
			}
			string[] files2 = Directory.GetFiles(root, "*.scn");
			foreach (string path2 in files2)
			{
				File.Delete(path2);
			}
		}

		private void ClearAllResults()
		{
			UostResults.Clear();
			MdpResults.Clear();
			CrtTimeResults.Clear();
			ShuntResults.Clear();
			DynResults.Clear();
		}

		public void OnPropertyChanged([CallerMemberName] string prop = "")
		{
			if (this.PropertyChanged != null)
			{
				this.PropertyChanged(this, new PropertyChangedEventArgs(prop));
			}
		}
	}
	public class MainWindow : Window, IComponentConnector
	{
		internal ListBox Rgms;

		internal ListBox Events;

		private bool _contentLoaded;

		public MainWindow()
		{
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			InitializeComponent();
			try
			{
				if (License())
				{
					((FrameworkElement)this).DataContext = new DataInfo();
					return;
				}
				throw new UserLicenseException("Некорректный файл лицензии");
			}
			catch (Exception ex)
			{
				MessageBox.Show("Ошибка при выполнении операции!" + Environment.NewLine + Environment.NewLine + ex.Message, "Error", (MessageBoxButton)0, (MessageBoxImage)16);
				((Window)this).Close();
			}
		}

		private void DeselectRgms(object sender, MouseButtonEventArgs e)
		{
			((Selector)Rgms).SelectedItem = null;
		}

		private void DeselectEvents(object sender, MouseButtonEventArgs e)
		{
			((Selector)Events).SelectedItem = null;
		}

		private bool License()
		{
			bool flag = false;
			string machineName = Environment.MachineName;
			if (File.Exists("C:\\ПАРУС 6\\licence.txt"))
			{
				int length = machineName.Length;
				int num = Convert.ToInt32(length / 3);
				int num2 = length - 2 * num;
				string text = machineName.Substring(0, num);
				string text2 = machineName.Substring(num, num);
				if (text2.Substring(0, 1) == "-")
				{
					text += "-";
					text2 = text2.Replace("-", "");
				}
				string text3 = machineName.Substring(length - num2, num2);
				if (text3.Substring(0, 1) == "-")
				{
					text2 += "-";
					text3 = text3.Replace("-", "");
				}
				string[] array = File.ReadAllLines("C:\\ПАРУС 6\\licence.txt").ToArray();
				return array[43].Contains(text) && array[45].Contains(text2) && array[46].Contains(text3) && array[52].Contains("p5");
			}
			throw new UserLicenseException("Файл лицензии не обнаружен");
		}

		private void RemsClear(object sender, MouseButtonEventArgs e)
		{
			DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
			dataInfo.Rems.Name = null;
			dataInfo.VrnInf.Clear();
			dataInfo.VrnInf.Add(new VrnInfo
			{
				Id = -1,
				Name = "Нормальная схема",
				Num = 0,
				Deactive = false
			});
		}

		private void VirClear(object sender, MouseButtonEventArgs e)
		{
			DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
			dataInfo.VIR.Name = null;
		}

		private void SchClear(object sender, MouseButtonEventArgs e)
		{
			DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
			dataInfo.Sechen.Name = null;
			dataInfo.SchInf.Clear();
		}

		private void KprClear(object sender, MouseButtonEventArgs e)
		{
			DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
			dataInfo.GRF.Name = null;
			dataInfo.KprInf.Clear();
		}

		private void AutoClear(object sender, MouseButtonEventArgs e)
		{
			DataInfo dataInfo = ((FrameworkElement)this).DataContext as DataInfo;
			dataInfo.LAPNU.Name = null;
			dataInfo.DynWithPA = false;
			dataInfo.UseLPN = false;
			dataInfo.lpns = "";
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		public void InitializeComponent()
		{
			if (!_contentLoaded)
			{
				_contentLoaded = true;
				Uri uri = new Uri("/DynStabSpace;component/mainwindow.xaml", UriKind.Relative);
				Application.LoadComponent((object)this, uri);
			}
		}

		[DebuggerNonUserCode]
		[GeneratedCode("PresentationBuildTasks", "4.0.0.0")]
		[EditorBrowsable(EditorBrowsableState.Never)]
		void IComponentConnector.Connect(int connectionId, object target)
		{
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Expected O, but got Unknown
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Expected O, but got Unknown
			//IL_0059: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Expected O, but got Unknown
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Expected O, but got Unknown
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0097: Expected O, but got Unknown
			//IL_009b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b1: Expected O, but got Unknown
			//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cb: Expected O, but got Unknown
			//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
			//IL_00db: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e5: Expected O, but got Unknown
			//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ff: Expected O, but got Unknown
			switch (connectionId)
			{
			case 1:
				Rgms = (ListBox)target;
				((Control)Rgms).MouseDoubleClick += new MouseButtonEventHandler(DeselectRgms);
				break;
			case 2:
				Events = (ListBox)target;
				((Control)Events).MouseDoubleClick += new MouseButtonEventHandler(DeselectEvents);
				break;
			case 3:
				((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(RemsClear);
				break;
			case 4:
				((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(AutoClear);
				break;
			case 5:
				((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(VirClear);
				break;
			case 6:
				((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(SchClear);
				break;
			case 7:
				((Control)(GroupBox)target).MouseDoubleClick += new MouseButtonEventHandler(KprClear);
				break;
			default:
				_contentLoaded = true;
				break;
			}
		}
	}
}
namespace DynStabSpace.Properties
{
	[GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "4.0.0.0")]
	[DebuggerNonUserCode]
	[CompilerGenerated]
	internal class Resources
	{
		private static ResourceManager resourceMan;

		private static CultureInfo resourceCulture;

		[EditorBrowsable(EditorBrowsableState.Advanced)]
		internal static ResourceManager ResourceManager
		{
			get
			{
				if (resourceMan == null)
				{
					ResourceManager resourceManager = new ResourceManager("DynStabSpace.Properties.Resources", typeof(Resources).Assembly);
					resourceMan = resourceManager;
				}
				return resourceMan;
			}
		}

		[EditorBrowsable(EditorBrowsableState.Advanced)]
		internal static CultureInfo Culture
		{
			get
			{
				return resourceCulture;
			}
			set
			{
				resourceCulture = value;
			}
		}

		internal Resources()
		{
		}
	}
	[CompilerGenerated]
	[GeneratedCode("Microsoft.VisualStudio.Editors.SettingsDesigner.SettingsSingleFileGenerator", "11.0.0.0")]
	internal sealed class Settings : ApplicationSettingsBase
	{
		private static Settings defaultInstance = (Settings)(object)SettingsBase.Synchronized((SettingsBase)(object)new Settings());

		public static Settings Default => defaultInstance;
	}
}
namespace ASTRALib
{
	[ComImport]
	[CompilerGenerated]
	[Guid("7E534FE3-B0C6-11D5-A75D-005004526FE6")]
	[CoClass(typeof(object))]
	[TypeIdentifier]
	public interface Cols : ICols
	{
	}
	[CompilerGenerated]
	[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib.DFWSyncLossCause")]
	public enum DFWSyncLossCause
	{
		SYNC_LOSS_NONE = 0,
		SYNC_LOSS_BRANCHANGLE = 1,
		SYNC_LOSS_COA = 2,
		SYNC_LOSS_OVERSPEED = 4,
		SYNC_LOSS_METHODFAILED = 5
	}
	[ComImport]
	[CompilerGenerated]
	[CoClass(typeof(object))]
	[Guid("708E3897-3EF5-4BEC-B0C5-F5B13A8D448B")]
	[TypeIdentifier]
	public interface FWDynamic : IFWDynamic
	{
	}
	[ComImport]
	[CompilerGenerated]
	[Guid("7E534FE0-B0C6-11D5-A75D-005004526FE6")]
	[TypeIdentifier]
	public interface ICol
	{
		void _VtblGap1_5();

		[DispId(4)]
		object Z
		{
			[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
			[DispId(4)]
			[return: MarshalAs(UnmanagedType.Struct)]
			get;
			[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
			[DispId(4)]
			[param: In]
			[param: MarshalAs(UnmanagedType.Struct)]
			set;
		}

		void _VtblGap2_6();

		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(7)]
		void Calc([MarshalAs(UnmanagedType.BStr)] string formula);
	}
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
	[ComImport]
	[CompilerGenerated]
	[Guid("A44744E4-ADCE-11D5-A75D-005004526FE6")]
	[TypeIdentifier]
	public interface ITable
	{
		void _VtblGap1_2();

		[DispId(2)]
		Cols Cols
		{
			[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
			[DispId(2)]
			[return: MarshalAs(UnmanagedType.Interface)]
			get;
		}

		[DispId(3)]
		int Size
		{
			[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
			[DispId(3)]
			get;
			[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
			[DispId(3)]
			[param: In]
			set;
		}

		void _VtblGap2_4();

		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(6)]
		void AddRow();

		void _VtblGap3_2();

		[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
		[DispId(9)]
		void SetSel([MarshalAs(UnmanagedType.BStr)] string viborka);

		void _VtblGap4_10();

		[DispId(19)]
		int FindNextSel
		{
			[MethodImpl(MethodImplOptions.InternalCall, MethodCodeType = MethodCodeType.Runtime)]
			[DispId(19)]
			get;
		}
	}
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
	[CompilerGenerated]
	[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib.LogErrorCodes")]
	public enum LogErrorCodes
	{
		LOG_SYSTEM_ERROR,
		LOG_FAILED,
		LOG_ERROR,
		LOG_WARNING,
		LOG_MESSAGE,
		LOG_INFO,
		LOG_STAGE_OPEN,
		LOG_STAGE_CLOSE,
		LOG_ENTER_DEFAULT,
		LOG_RESET,
		LOG_NONE
	}
	[CompilerGenerated]
	[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib.RG_KOD")]
	public enum RG_KOD
	{
		RG_ADD,
		RG_REPL,
		RG_KEY,
		RG_KEYADD,
		RG_KEY_REPLOTHERS
	}
	[ComImport]
	[CompilerGenerated]
	[CoClass(typeof(object))]
	[Guid("84B0508C-ABC9-11D3-B740-00500454CF3F")]
	[TypeIdentifier]
	public interface Rastr : IRastr, _IRastrEvents_Event
	{
	}
	[CompilerGenerated]
	[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib.RastrRetCode")]
	public enum RastrRetCode
	{
		AST_OK = 0,
		AST_NB = 1,
		AST_REPT = 2,
		AST_CONTROL = 3,
		AST_NBAP = 4,
		AST_UB = 256
	}
	[ComImport]
	[CompilerGenerated]
	[CoClass(typeof(object))]
	[Guid("A44744E0-ADCE-11D5-A75D-005004526FE6")]
	[TypeIdentifier]
	public interface Tables : ITables
	{
	}
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
	[ComImport]
	[CompilerGenerated]
	[ComEventInterface(typeof(_IRastrEvents), typeof(_IRastrEvents))]
	[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib._IRastrEvents_Event")]
	public interface _IRastrEvents_Event
	{
		void _VtblGap1_6();

		event _IRastrEvents_OnLogEventHandler OnLog;
	}
	[CompilerGenerated]
	[TypeIdentifier("84b05080-abc9-11d3-b740-00500454cf3f", "ASTRALib._IRastrEvents_OnLogEventHandler")]
	public delegate void _IRastrEvents_OnLogEventHandler([In] LogErrorCodes Code, [In] int Level, [In] int StageId, [In][MarshalAs(UnmanagedType.BStr)] string TableName, [In] int TableIndex, [In][MarshalAs(UnmanagedType.BStr)] string Description, [In][MarshalAs(UnmanagedType.BStr)] string FormName);
	[ComImport]
	[CompilerGenerated]
	[CoClass(typeof(object))]
	[Guid("7E534FE0-B0C6-11D5-A75D-005004526FE6")]
	[TypeIdentifier]
	public interface col : ICol
	{
	}
	[ComImport]
	[CompilerGenerated]
	[CoClass(typeof(object))]
	[Guid("A44744E4-ADCE-11D5-A75D-005004526FE6")]
	[TypeIdentifier]
	public interface table : ITable
	{
	}
}
